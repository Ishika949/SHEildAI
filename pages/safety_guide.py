import streamlit as st

from guidance import search_guidance
from utils import BASE_DIR, render_page_sidebar

INITIAL_MESSAGE = {"role": "assistant", "content": "Hi! How can I help you today?"}
NO_MATCH_MESSAGE = (
    "I couldn't find an answer to that. Try asking about safety planning, rights, or emergency help."
)


def assistant_reply(question):
    matches = search_guidance(question, limit=1)
    if not matches:
        return NO_MATCH_MESSAGE
    match = matches[0]
    points = "\n".join(f"- {point}" for point in match["points"])
    return f"**{match['title']}**\n\n{match['introduction']}\n\n{points}"


render_page_sidebar()
st.title("AI Chat")

intro_column, image_column = st.columns([1.3, 0.9], gap="large")
with intro_column:
    st.write("Ask about safety planning, rights, or getting help.")
with image_column:
    st.image(
        str(BASE_DIR / "assets" / "images" / "img-chat.png"),
        width="stretch",
    )

st.space("medium")

st.session_state.setdefault("ai_chat_messages", [INITIAL_MESSAGE.copy()])
if st.button("Clear chat", key="clear_ai_chat"):
    st.session_state["ai_chat_messages"] = [INITIAL_MESSAGE.copy()]

for message in st.session_state["ai_chat_messages"]:
    avatar = ":material/person:" if message["role"] == "user" else ":material/chat:"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

question = st.chat_input("Type your safety question here...")
if question and question.strip():
    question = question.strip()
    st.session_state["ai_chat_messages"].append(
        {"role": "user", "content": question}
    )
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(question)

    answer = assistant_reply(question)
    st.session_state["ai_chat_messages"].append(
        {"role": "assistant", "content": answer}
    )
    with st.chat_message("assistant", avatar=":material/chat:"):
        st.markdown(answer)
