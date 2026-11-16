import streamlit as st

from utils import require_account, update_account

account = require_account()
st.title("🛡️ SHEild AI")
st.header("👤 User Profile and Settings")
st.write("Update the name and phone number saved with your account.")

with st.form("profile_form"):
    name = st.text_input(
        "Full name",
        value=account["name"],
        max_chars=80,
        key="profile_name",
    )
    st.text_input(
        "Email address",
        value=account["email"],
        disabled=True,
        key="profile_email",
    )
    phone = st.text_input(
        "Phone number",
        value=account.get("phone", ""),
        max_chars=32,
        key="profile_phone",
    )
    save = st.form_submit_button("💾 Save profile", key="save_profile")

if save:
    try:
        updated_account = update_account(account["id"], name, phone)
        if updated_account is None:
            st.error("The account could not be found.")
        else:
            st.session_state["current_user"] = updated_account
            st.success("Profile saved.")
    except (ValueError, OSError) as error:
        st.error(f"Profile could not be saved: {error}")
