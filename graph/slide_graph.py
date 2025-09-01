from langchain_openai import ChatOpenAI
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, SystemMessage
from prompt_manager import get_prompt
from langchain_openai import OpenAI
import json

from slash_command_runner import run_slash_command

def create_llm_msg(system_prompt: str, messageHistory: list[BaseMessage]):
    resp = []
    resp.append(SystemMessage(content=system_prompt))
    resp.extend(messageHistory)
    return resp


class AgentState(TypedDict):
    response_to_user: str
    incremental_response: str
    final_response: str
    category: str
    user_prompt: str
    original_slides: dict
    message_history: list[BaseMessage]

class Category(BaseModel):
    category: str
    information: str

VALID_CATEGORIES = ["clarification", "generate_slide_content", "update_content", "generate_for_code"]

class SlideContentBlockText(BaseModel):
    type: str = "text"
    body: str

class SlideContentBlockCode(BaseModel):
    type: str = "code"
    language: str = "python"
    body: str

class SlideContentBlockImage(BaseModel):
    type: str = "image"
    query: str
    caption: str = ""

class Slides(BaseModel):
    title: str
    subtitle: str = ""
    content_blocks: list[SlideContentBlockText | SlideContentBlockCode | SlideContentBlockImage]
    user_message: str = ""

def save_slides(slides: Slides):
    print(f"Saving slides: {slides}")
    slide_md = f"# {slides.title}\n\n"
    if slides.subtitle:
        slide_md += f"## {slides.subtitle}\n\n"
    for block in slides.content_blocks:
        if block.type == "text":
            slide_md += f"{block.body}\n\n"
        elif block.type == "code":
            slide_md += f"```{block.language}\n{block.body}\n```\n\n"
        elif block.type == "image":
            slide_md += f"![{block.caption}](https://source.unsplash.com/featured/?{block.query})\n\n"
    slide_md += f"---\n\n*Generated based on your message:*\n\n{slides.user_message}\n\n"
    yield {"content":slide_md}
    
    def stream_response():
        yield slide_md

    return stream_response()


class SlideGraph():
    def __init__(self, model, api_key):
        self.model = ChatOpenAI(model=model, api_key=api_key)


        workflow = StateGraph(AgentState)
        workflow.add_node("classifier", self.initial_classifier)
        workflow.add_node("clarification", self.clarification)
        workflow.add_node("generate_slide_content", self.generate_slide_content)
        workflow.add_node("update_content", self.update_content)
        workflow.add_node("generate_for_code", self.generate_for_code)

        workflow.add_conditional_edges("classifier", self.main_router)
        workflow.add_edge(START, "classifier")
        workflow.add_edge("clarification", END)
        workflow.add_edge("generate_slide_content", END)
        workflow.add_edge("update_content", END)
        workflow.add_edge("generate_for_code", END)


        self.graph = workflow.compile()

    def initial_classifier(self, state: AgentState):
        print("initial classifier")
        user_prompt = state['user_prompt']
        message_history = state['message_history']
        original_slides = state.get('original_slides', None)
        if user_prompt.startswith("/"):
            print(f"Got a command {user_prompt}, ignoring it for now.")
            rs=run_slash_command(self.model, user_prompt, message_history, original_slides)
            return {
                "category": "slash_command",
                "final_response": rs,
            }
        CLASSIFIER_PROMPT = get_prompt("classifier")
        llm_messages = create_llm_msg(CLASSIFIER_PROMPT, state['message_history'])
        llm_response = self.model.with_structured_output(Category).invoke(llm_messages)
        category = llm_response.category
        print(f"category is {category}")
        return{
            "category": category,
        }
    
    def main_router(self, state: AgentState):
        my_category = state['category']
        if my_category in VALID_CATEGORIES:
            return my_category
        elif my_category == "slash_command":
            print("slash command, ending")
            return END
        else:
            print(f"unknown category: {my_category}")
            return END
        
    def clarification(self, state: AgentState):
        print("clarification")
        llm_messages = create_llm_msg(get_prompt("clarification"), state['message_history'])
        return {
            "incremental_response": self.model.stream(llm_messages)
        }
    
    def generate_slide_content(self, state: AgentState):
        print("generate_slide+content")
        llm_messages = create_llm_msg(get_prompt("generate_slide_content"), state['message_history'])
        resp = self.model.with_structured_output(Slides).invoke(llm_messages)
        # Convert the Pydantic model to a plain dict for serialization/state
        resp_dict = resp.model_dump() if hasattr(resp, "model_dump") else resp.dict()

        return {
            "full_response": json.dumps(resp_dict, indent=2),
            "original_slides": resp_dict,
        }
    
    def update_content(self, state: AgentState):
        print("update_content")
        llm_messages = create_llm_msg(get_prompt("update_content"), state['message_history'])
        return {
            "incremental_response": self.model.stream(llm_messages)
        }
    
    def generate_for_code(self, state: AgentState):
        print("generate_for_code")
        llm_messages = create_llm_msg(get_prompt("generate_for_code"), state['message_history'])
        return {
            "incremental_response": self.model.stream(llm_messages)
        }
    
