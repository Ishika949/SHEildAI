import sqlite3

import streamlit as st

from utils import BASE_DIR, load_contacts, require_account, save_contacts


def stop_sos_sound():
    st.session_state["sos_sound_requested"] = False


account = require_account()
st.title("Dashboard")

contact_error = None
contacts = []
try:
    contacts = load_contacts(account["id"])
except (OSError, sqlite3.Error, ValueError) as error:
    contact_error = str(error)

intro_column, image_column = st.columns([1.3, 0.9], gap="large")
with intro_column:
    st.write("Manage your trusted contacts and use SOS.")
with image_column:
    st.image(
        str(BASE_DIR / "assets" / "images" / "img-dashboard.png"),
        width="stretch",
    )

st.space("medium")
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.subheader("Trusted contacts")
    if contact_error:
        st.error(f"Contacts could not be loaded: {contact_error}")
    else:
        existing = contacts + [{"name": "", "phone": ""}] * (3 - len(contacts))
        with st.form("trusted_contacts_form"):
            contact_values = []
            for index in range(3):
                if index:
                    st.space("small")
                st.markdown(f"**Trusted contact {index + 1}**")
                name = st.text_input(
                    "Name",
                    value=existing[index]["name"],
                    max_chars=80,
                    key=f"contact_name_{index}",
                )
                phone = st.text_input(
                    "Phone number",
                    value=existing[index]["phone"],
                    max_chars=32,
                    key=f"contact_phone_{index}",
                )
                contact_values.append({"name": name, "phone": phone})
            save = st.form_submit_button("Save contacts")
        if save:
            try:
                save_contacts(account["id"], contact_values)
                st.success("Contacts saved.")
            except (ValueError, OSError, sqlite3.Error) as error:
                st.error(f"Contacts could not be saved: {error}")

with right:
    with st.container(border=True):
        st.subheader("SOS sound")
        if st.button("Play SOS sound", type="primary", key="play_sos_sound"):
            st.session_state["sos_sound_requested"] = True
        if st.session_state.get("sos_sound_requested", False):
            sound_path = BASE_DIR / "assets" / "sos-alert.mp3"
            if sound_path.is_file():
                st.audio(
                    sound_path,
                    format="audio/mpeg",
                    end_time=15,
                    autoplay=True,
                    loop=False,
                )
                st.button("Stop sound", key="stop_sos_sound", on_click=stop_sos_sound)
            else:
                st.error("The SOS sound file is missing. Restore assets/sos-alert.mp3 to enable playback.")
            with st.container(border=True):
                st.subheader("SMS preview")
                st.write("I need help. Please contact me.")
