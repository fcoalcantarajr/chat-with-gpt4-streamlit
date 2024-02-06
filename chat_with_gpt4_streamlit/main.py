from openai import OpenAI
import streamlit as st
from configs import OAI_MODEL, EXPORT_DIR
from utils import export_current_conversation, num_tokens_from_messages

st.title(f"Chat with [{OAI_MODEL}] model using Streamlit")
st.subheader(f"Conversations will be exported to {EXPORT_DIR}")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = OAI_MODEL

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Layout modification: Include the text_area and send button in the same line
col1, col2 = st.columns([5, 1])  # Adjust the ratio as needed
with col1:
    prompt = st.text_area("What is up?", key="prompt", height=75, label_visibility="collapsed")
with col2:
    send_button = st.button("Send")

# Process the prompt when the button is clicked
if send_button and prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

dados = export_current_conversation(st.session_state.messages)
data_as_csv= dados.to_csv(index=False).encode("utf-8")
download_button = st.download_button(label="Download", data=data_as_csv, file_name='chat-gpt4.csv', mime='text/csv')

    # # Clear the prompt area after sending the message
    # st.session_state['prompt'] = ''

# Display the total tokens used in the conversation
st.markdown(f"<span style='color:red'>Total tokens used till now in conversation (your input + model's output): {num_tokens_from_messages(st.session_state.messages, OAI_MODEL)}</span>", unsafe_allow_html=True)