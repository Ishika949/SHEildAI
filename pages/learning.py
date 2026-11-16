import streamlit as st

from guidance import GUIDANCE_TOPICS
from utils import BASE_DIR, render_page_sidebar

render_page_sidebar()
st.title("🛡️ SHEild AI")
st.header("📚 Learn & Know")
st.write(
    "Learn about women's safety, legal rights, "
    "constitutional rights and important safety information."
)
st.divider()

selected_topic = st.selectbox("Choose a topic:", list(GUIDANCE_TOPICS))

if selected_topic == "Women's Safety Rules":
    st.subheader("🛡️ Women's Safety Rules")
elif selected_topic == "Legal Rights in India":
    st.subheader("⚖️ Legal Rights in India")
elif selected_topic == "Constitutional Rights":
    st.subheader("🏛️ Constitutional Rights")
elif selected_topic == "What To Do in an Unsafe Situation":
    st.subheader("🚨 What To Do in an Unsafe Situation")

topic = GUIDANCE_TOPICS[selected_topic]

content_column, image_column = st.columns([1.3, 0.9], gap="large")
with content_column:
    if topic["introduction"]:
        st.write(topic["introduction"])

    for index, point in enumerate(topic["points"], start=1):
        if topic.get("ordered"):
            st.write(f"{index}. {point}")
        else:
            st.write(f"• {point}")

    if topic.get("note"):
        st.info(topic["note"])
    if topic.get("warning"):
        st.warning(topic["warning"])
with image_column:
    st.image(
        str(BASE_DIR / "assets" / "images" / "img-learning.png"),
        width="stretch",
    )
