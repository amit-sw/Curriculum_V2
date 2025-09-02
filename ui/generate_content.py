import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

import time

from integration.supabase_integration import get_supabase_client, get_all_brainstorms_from_db, update_brainstorm_slides_in_db
from utils.llm_calls import create_llm_msg
from utils.prompt_manager import get_prompt

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

class Slide(BaseModel):
    id: str
    title: str
    content_blocks: list[SlideContentBlockText | SlideContentBlockCode | SlideContentBlockImage]

class SlideDeck(BaseModel):
    title: str
    subtitle: str = ""
    slides: list[Slide]
    user_message: str = ""

def generate_json_for_slides(row_id, title, content):
    print(f"\n\nTO-DO TO-DO \n\nGenerating JSON for slides for {row_id=}, {title=}, {content[:50]=}...")
    model = ChatOpenAI(model=st.secrets['OPENAI_MODEL_NAME'], api_key=st.secrets['OPENAI_API_KEY']).with_structured_output(SlideDeck)
    llm_messages = create_llm_msg(get_prompt("generate_slide_content"), [HumanMessage(content=f"Title: {title}\n\nContent: {content}")])
    #print(f"\n\nLLM Messages: {llm_messages}:XXXXXX\n\n")
    resp = model.invoke(llm_messages)
    supabase=get_supabase_client()
    update_brainstorm_slides_in_db(supabase, row_id, resp.model_dump_json())
    return

def generate_content():
    supabase = get_supabase_client()
    brainstorms = get_all_brainstorms_from_db(supabase)    
    selection=st.dataframe(brainstorms, selection_mode="single-row", on_select="rerun")
    print(f"\n\n DEBUG. SELECTION: {selection=}")
    if selection and selection.get("selection") and selection["selection"].get("rows"):
        selected_row_array = selection["selection"]["rows"]
        if not selected_row_array or len(selected_row_array) == 0:
            return
        selected_row_id = selection["selection"]["rows"][0]
        selected_row = brainstorms[selected_row_id]
        row_id = selected_row.get("id")
        title = selected_row.get("title", "No Title")
        content = selected_row.get("content", "No Content")
        slide_json = selected_row.get("slide_json", "{}")
        with st.expander(f"Title: {title}"):
           st.markdown(content)
        if slide_json and slide_json != "{}":
            st.text_area("Slides JSON", slide_json, height=300)
            if st.button("Render Slides"):
                st.markdown("### TO-DO TO-DO TO-DO: Slides Preview")
        else:
            if st.button("Generate JSON"):
                start_time = time.time()
                with st.spinner("Generating slides...", show_time=True):
                    generate_json_for_slides(row_id, title, content)
                    elapsed = time.time() - start_time
                    st.markdown(f"Slide generation: ({elapsed:.1f}s elapsed)")
        
    
st.title("Generate Content")   
generate_content()