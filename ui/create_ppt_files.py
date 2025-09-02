import streamlit as st
import json

from integration.supabase_integration import get_supabase_client, get_all_brainstorms_from_db
from utils.ppt_generator import create_one_presentation

def create_ppt_files():
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
        title = selected_row.get("title", "No Title")
        content = selected_row.get("content", "No Content")
        slide_json = json.loads(selected_row.get("slide_json", "{}"))
        with st.sidebar.expander(f"Title: {title}"):
            st.markdown(content)
        st.sidebar.markdown(f"### Slides JSON")
        st.sidebar.json(slide_json, expanded=False)
        if st.button("Generate PPTX"):
            st.warning("PPTX generation not yet implemented.")
            # TO-DO: Implement PPTX generation from slide_json
            title_safe = title.replace(" ", "_").replace("/", "_")
            create_one_presentation(slide_json,"Not used", f"output/{title_safe}.pptx")
            st.success(f"PPTX file created: output/{title_safe}.pptx")
            
        
    
st.title("Create PPT Files")    
create_ppt_files()