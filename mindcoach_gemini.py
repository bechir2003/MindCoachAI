import streamlit as st
import requests
from datetime import datetime

# Gemini config
api_key = "AIzaSyChBfvdVA1bRLfIEukWLNGOAfSl5hlHZ9A"
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
headers = {"Content-Type": "application/json"}

# Initialize chat history and sessions
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "user",
            "parts": [{
                "text": """You are MindCoachAI — a motivational mental coach for athletes.
Help athletes deal with stress, low motivation, performance anxiety, and burnout.
Give brief, clear suggestions: mental resets, breathing, encouragement, visualization.
Don't diagnose or give medical advice."""
            }]
        }
    ]

# Initialize chat history storage
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# Initialize current chat ID
if "current_chat" not in st.session_state:
    st.session_state.current_chat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.chat_history[st.session_state.current_chat] = st.session_state.messages.copy()

# Flag to clear input after submit
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

st.title("🏋️‍♂️ MindCoachAI")

# Sidebar for chat history
with st.sidebar:
    st.header("Chat History")
    
    # Button to create new chat
    if st.button("➕ New Chat"):
        # Save current chat before creating new one
        st.session_state.chat_history[st.session_state.current_chat] = st.session_state.messages.copy()
        
        # Create new chat
        new_chat_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.current_chat = new_chat_id
        st.session_state.messages = [
            {
                "role": "user",
                "parts": [{
                    "text": """You are MindCoachAI — a motivational mental coach for athletes.
Help athletes deal with stress, low motivation, performance anxiety, and burnout.
Give brief, clear suggestions: mental resets, breathing, encouragement, visualization.
Don't diagnose or give medical advice."""
                }]
            }
        ]
        st.session_state.chat_history[new_chat_id] = st.session_state.messages.copy()
        st.session_state.clear_input = True
        st.rerun()
    
    # Display chat history
    for chat_id in sorted(st.session_state.chat_history.keys(), reverse=True):
        if st.button(chat_id):
            # Load selected chat
            st.session_state.current_chat = chat_id
            st.session_state.messages = st.session_state.chat_history[chat_id].copy()
            st.session_state.clear_input = True
            st.rerun()

# Display current chat messages
for i in range(1, len(st.session_state.messages), 2):
    user_msg = st.session_state.messages[i]["parts"][0]["text"]
    bot_msg = ""
    if i + 1 < len(st.session_state.messages):
        bot_msg = st.session_state.messages[i + 1]["parts"][0]["text"]
    st.markdown(f"👤 **You:** {user_msg}")
    st.markdown(f"🤖 **MindCoachAI:** {bot_msg}")

# Determine default input value based on clear_input flag
default_input = "" if st.session_state.clear_input else None

if st.session_state.clear_input:
    # Reset input field if clear_input is True
    st.session_state.user_message = ""
    st.session_state.clear_input = False
else:
    # Use existing input value if not clearing
    default_input = st.session_state.get("user_message", "")

with st.form(key="chat_form"):
    user_input = st.text_input("Your message:", key="user_message", value=default_input)
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "parts": [{"text": user_input}]})
    
    # Update current chat in history
    st.session_state.chat_history[st.session_state.current_chat] = st.session_state.messages.copy()

    payload = {"contents": st.session_state.messages}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            reply_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            st.session_state.messages.append({"role": "model", "parts": [{"text": reply_text}]})
            # Update history with the response
            st.session_state.chat_history[st.session_state.current_chat] = st.session_state.messages.copy()
            # Set flag to clear input next run
            st.session_state.clear_input = True
            st.rerun()
        except Exception as e:
            st.error("Failed to parse Gemini response.")
            st.text(str(e))
    else:
        st.error(f"API error: {response.status_code}")
        st.text(response.text)
else:
    # Reset flag if no submit, so input is not cleared next run
    st.session_state.clear_input = False