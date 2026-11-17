import streamlit as st

from utils import BASE_DIR, load_contacts, require_account, save_contacts


def stop_sos_sound():
    st.session_state["sos_sound_requested"] = False


account = require_account()
st.title("🛡️ SHEild AI")
st.header("🚨 Emergency Dashboard")
st.write("Add trusted contacts for your emergency plan.")

st.image(
    str(BASE_DIR / "assets" / "images" / "Dashboard.jpeg"),
    width="stretch",
)

contacts = []
contact_error = None

try:
    contacts = load_contacts(account["id"])
except (OSError, ValueError) as error:
    contact_error = str(error)

if contact_error:
    st.error(f"Contacts could not be loaded: {contact_error}")
else:
    contact1 = contacts[0] if len(contacts) > 0 else {"name": "", "phone": ""}
    contact2 = contacts[1] if len(contacts) > 1 else {"name": "", "phone": ""}
    contact3 = contacts[2] if len(contacts) > 2 else {"name": "", "phone": ""}

    st.write("These contacts are saved to your account for easy reference.")

    with st.form("trusted_contacts_form"):
        st.subheader("Emergency Contact 1")
        contact1_name = st.text_input(
            "Name",
            value=contact1["name"],
            max_chars=80,
            key="contact_name_0",
        )
        contact1_phone = st.text_input(
            "Phone number",
            value=contact1["phone"],
            max_chars=32,
            key="contact_phone_0",
        )

        st.subheader("Emergency Contact 2")
        contact2_name = st.text_input(
            "Name",
            value=contact2["name"],
            max_chars=80,
            key="contact_name_1",
        )
        contact2_phone = st.text_input(
            "Phone number",
            value=contact2["phone"],
            max_chars=32,
            key="contact_phone_1",
        )

        st.subheader("Emergency Contact 3")
        contact3_name = st.text_input(
            "Name",
            value=contact3["name"],
            max_chars=80,
            key="contact_name_2",
        )
        contact3_phone = st.text_input(
            "Phone number",
            value=contact3["phone"],
            max_chars=32,
            key="contact_phone_2",
        )

        save = st.form_submit_button(
            "💾 Save Emergency Contacts",
            key="save_contacts",
        )

    if save:
        contacts_to_save = [
            {"name": contact1_name, "phone": contact1_phone},
            {"name": contact2_name, "phone": contact2_phone},
            {"name": contact3_name, "phone": contact3_phone},
        ]

        try:
            save_contacts(account["id"], contacts_to_save)
            st.success("Emergency contacts saved successfully.")
        except (ValueError, OSError) as error:
            st.error(f"Contacts could not be saved: {error}")

st.divider()
st.header("🚨 Emergency Alert")
st.write("If you need help, use the button below to play the SOS sound.")

if st.button("🚨 SOS - Play Sound", type="primary", key="play_sos_sound"):
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
        st.button(
            "⏹️ Stop sound",
            key="stop_sos_sound",
            on_click=stop_sos_sound,
        )
        st.subheader("✉️ SMS preview")
        st.write("I need help. Please contact me.")
    else:
        st.error("The SOS sound file is missing. Restore assets/sos-alert.mp3 to enable playback.")
