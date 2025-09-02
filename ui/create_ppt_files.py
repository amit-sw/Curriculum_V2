import streamlit as st

from integration.supabase_integration import get_supabase_client, get_all_brainstorms_from_db

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
        slides_json = selected_row.get("slides_json", "{}")
        st.markdown(f"## Title: {title}")
        st.markdown(f"### Content")
        st.markdown(content)
        st.markdown(f"### Slides JSON")
        st.json(slides_json)
        
    
st.title("Create PPT Files")    
create_ppt_files()