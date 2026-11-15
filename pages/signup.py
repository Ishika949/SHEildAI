import sqlite3

import streamlit as st

from utils import BASE_DIR, create_account, render_page_sidebar

render_page_sidebar()
st.title("Sign Up")
st.write("Create an account to manage your contacts.")
st.space("medium")

form_column, image_column = st.columns([1.2, 0.8], gap="large")
if st.session_state.get("current_user"):
    with form_column:
        st.info("You are already signed in. Use the sidebar to open your Profile or sign out.")
else:
    with form_column:
        with st.container(border=True):
            st.subheader("Create an account")
            with st.form("signup_form"):
                name = st.text_input("Full name", key="signup_name", max_chars=80)
                email = st.text_input("Email address", key="signup_email", max_chars=254)
                phone = st.text_input("Phone number (optional)", key="signup_phone", max_chars=32)
                password = st.text_input(
                    "Password",
                    key="signup_password",
                    type="password",
                    help="Use at least 8 characters. Do not reuse a password from another account.",
                )
                confirm_password = st.text_input(
                    "Confirm password",
                    key="signup_confirm_password",
                    type="password",
                )
                submitted = st.form_submit_button("Create account")

    if submitted:
        if password != confirm_password:
            st.error("The passwords do not match.")
        else:
            try:
                account = create_account(email, name, phone, password)
                if account is None:
                    st.error("An account already uses this email address.")
                else:
                    st.session_state["current_user"] = account
                    st.switch_page("pages/dashboard.py")
            except (ValueError, OSError, sqlite3.Error) as error:
                st.error(f"Account could not be created: {error}")

    with form_column:
        st.space("small")
        st.page_link("pages/login.py", label="Already have an account? Login")

with image_column:
    st.image(
        str(BASE_DIR / "assets" / "images" / "img-signup.png"),
        width="stretch",
    )
