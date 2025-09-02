from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI


def create_llm_msg(system_prompt: str, messageHistory: list[BaseMessage]):
    resp = []
    resp.append(SystemMessage(content=system_prompt))
    resp.extend(messageHistory)
    return resp

def run_model(model,llm_messages):
    response = model.invoke(llm_messages)

    # Extract text from response.content if it's a list of dicts
    if isinstance(response.content, list):
        returned_string = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in response.content
        )
    else:
        returned_string = str(response.content)
    return returned_string, response