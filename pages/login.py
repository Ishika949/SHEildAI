import sqlite3

import streamlit as st

from utils import BASE_DIR, authenticate, render_page_sidebar

render_page_sidebar()
st.title("Login")
st.write("Sign in to manage your contacts and profile.")
st.space("medium")

form_column, image_column = st.columns([1.2, 0.8], gap="large")
if st.session_state.get("current_user"):
    with form_column:
        st.info("You are already signed in. Use the sidebar to open your Profile or sign out.")
else:
    with form_column:
        with st.container(border=True):
            st.subheader("Sign in")
            with st.form("login_form"):
                email = st.text_input("Email address", key="login_email", max_chars=254)
                password = st.text_input("Password", key="login_password", type="password")
                submitted = st.form_submit_button("Login")

    if submitted:
        if not email.strip() or not password:
            st.error("Enter your email address and password.")
        else:
            try:
                account = authenticate(email, password)
                if account is None:
                    st.error("Email or password is incorrect.")
                else:
                    st.session_state["current_user"] = account
                    st.switch_page("pages/dashboard.py")
            except (ValueError, OSError, sqlite3.Error) as error:
                st.error(f"Login could not be completed: {error}")

    with form_column:
        st.space("small")
        st.page_link("pages/signup.py", label="Create an account")

with image_column:
    st.image(
        str(BASE_DIR / "assets" / "images" / "img-login.png"),
        width="stretch",
    )
