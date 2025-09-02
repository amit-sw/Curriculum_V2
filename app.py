import streamlit as st
import os

from ui.verified_ui import show_ui_role_based
from integration.supabase_integration import get_supabase_client, get_user_from_db


os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_PROJECT"]="Curiculum_GeneratorV2"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"

def show_ui(user):
    if user and user.get("email_verified", False):
        supabase = get_supabase_client()
        if supabase:
            user_record = get_user_from_db(supabase, user['email'])
            role= user_record.get("role", "guest") if user_record else "guest"
            show_ui_role_based(user,role)
        else:
            st.error("Could not connect to Supabase.")
    else:
        st.warning("Please log in with a verified email to access the app.")    

def login_screen():
    st.button("🔑 Log in with Google", type="secondary", on_click=st.login)

is_logged_in = st.user.get("is_logged_in")

if is_logged_in:
    show_ui(st.user)
else:
    login_screen()
