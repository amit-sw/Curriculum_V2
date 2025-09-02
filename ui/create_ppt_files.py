import streamlit as st
import json
import os

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
        title_safe = title.replace(" ", "_").replace("/", "_")
        title_safe = st.text_input("Filename to use (without extension)", value=title_safe)
                    
        if st.button("Generate PPTX"):

            output_fname = f"{title_safe}.pptx"
            create_one_presentation(slide_json,"Not used", output_fname)

            output_path = os.path.join("output", output_fname)
            st.success(f"PPTX file created: {output_path}")

            with open(output_path, 'rb') as f:
                presentation_bytes = f.read()
            #output_fname = st.text_input("Filename to download", value=output_fname)
            st.download_button(
                "📥 Download Presentation",
                presentation_bytes,
                output_fname,
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
                    
        
    
st.title("Create PPT Files")    
create_ppt_files()