import streamlit as st

from guidance import GUIDANCE_TOPICS
from utils import BASE_DIR, render_page_sidebar

render_page_sidebar()
st.title("Learning")
st.write("Read short guides about safety planning, rights, and getting help.")
st.space("small")

selected_topic = st.selectbox("Choose a topic", list(GUIDANCE_TOPICS))
topic = GUIDANCE_TOPICS[selected_topic]

st.space("medium")
content_column, image_column = st.columns([1.3, 0.9], gap="large")
with content_column:
    with st.container(border=True):
        st.subheader(topic["title"])
        st.write(topic["introduction"])
        for point in topic["points"]:
            st.markdown(f"- {point}")
with image_column:
    st.image(
        str(BASE_DIR / "assets" / "images" / "img-learning.png"),
        width="stretch",
    )
