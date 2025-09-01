import streamlit as st

def show_sidebar(user, role):
    name = user.get("name", "Unknown User")
    email = user.get("email", "Unknown Email")
    picture = user.get("picture", "")
    email_verified = user.get("email_verified", False)

    with st.sidebar:
        st.text(f"Welcome {name}\n {email}")
        st.text(f"Role: {role}")
        if email_verified:
            st.success("Email is verified.")
        else:
            st.warning("Email is not verified.")
        if picture:
            st.image(picture, width=100)
        if st.button("Log out"):
            st.logout()

def show_ui_core(user,role):

    show_sidebar(user, role)
    pages = {
        "Generate": [
            st.Page("create_content.py", title="Content"),
            st.Page("create_slides.py", title="Slides"),
        ],
        "View": [
            st.Page("view_content.py", title="Content"),
            st.Page("view_slides.py", title="Slides"),
        ],
    }
    if role == "admin":
        pages["Admin"] = [
            st.Page("manage_users.py", title="Users"),
        ]

    #pg = st.navigation(pages, position="top")
    pg = st.navigation(pages)
    pg.run()


def show_ui_role_based(user, role):
    if role == "guest":
        st.title("Guest Access")
        st.write(f"You do not have access. Please reach out to System Administrator with your information\n Email: {user.get('email', 'Unknown Email')}.")
        if st.button("Log out"):
            st.logout()
    else:
        show_ui_core(user, role)
