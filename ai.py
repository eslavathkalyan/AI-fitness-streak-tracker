import streamlit as st
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Page configuration
st.set_page_config(
    page_title="🏋️ Streak Fitness Tracker",
    page_icon="💪",
    layout="centered"
)

# Background and styling
background_image_url = "https://images.unsplash.com/photo-1599058917212-d750089bc07a"  # Fitness background
st.markdown(
    """
    <style>
        /* Fitness-themed gradient background with subtle texture */
        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            background-attachment: fixed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #f0f4f8;
            margin: 0;
            padding: 0;
        }

        /* Main app container with glassmorphism effect */
        .stApp {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 25px;
            padding: 40px 50px;
            box-shadow:
                0 8px 32px 0 rgba(31, 38, 135, 0.37),
                0 0 0 1px rgba(255, 255, 255, 0.18);
            color: #e0e7ff;
            font-size: 18px;
            line-height: 1.7;
            transition: background-color 0.3s ease;
        }

        /* Chat message styling with fitness accent colors */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.15);
            border-left: 6px solid #ff6f61; /* Vibrant coral accent */
            padding: 20px 25px;
            border-radius: 15px;
            margin-bottom: 18px;
            color: #f1f5f9;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: background-color 0.3s ease, box-shadow 0.3s ease;
        }
        .stChatMessage:hover {
            background: rgba(255, 255, 255, 0.25);
            box-shadow: 0 6px 20px rgba(255, 111, 97, 0.5);
        }

        /* Sidebar with complementary dark translucent background */
        .stSidebar {
            background: rgba(20, 30, 45, 0.85);
            border-radius: 20px;
            padding: 30px 25px;
            color: #cbd5e1;
            box-shadow:
                inset 0 0 15px #ff6f61;
            font-size: 16px;
            font-weight: 500;
        }

        /* Sidebar buttons with fitness coral accent */
        .stSidebar .stButton > button {
            background-color: #ff6f61;
            color: white;
            border-radius: 12px;
            padding: 12px 18px;
            font-weight: 700;
            font-size: 16px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 12px rgba(255, 111, 97, 0.6);
        }
        .stSidebar .stButton > button:hover {
            background-color: #e85b4a;
            box-shadow: 0 6px 20px rgba(232, 91, 74, 0.8);
        }

        /* Links styling */
        a {
            color: #ff6f61 !important;
            text-decoration: underline;
            font-weight: 600;
        }

        /* Titles with subtle shadow for better readability */
        .stTitle, .stCaption {
            text-shadow: 1px 1px 6px rgba(0, 0, 0, 0.7);
        }
    </style>
    """,unsafe_allow_html=True

)
# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hey there! 👋 I’m your Streak Fitness Tracker. Ask me anything about workouts, diet, or fitness progress!"
    }]

# Sidebar settings
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.markdown("[Get API Key](https://openrouter.ai/keys)")

    model_name = st.selectbox(
        "Choose AI Model",
        ("deepseek/deepseek-r1-zero:free", "google/palm-2-chat-bison"),
        index=0
    )

    with st.expander("Advanced Settings"):
        temperature = st.slider("Response Creativity", 0.0, 1.0, 0.6)
        max_retries = st.number_input("Max Retries", 1, 5, 2)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Chat cleared! Ready to help with your fitness journey! 💪"
        }]

# App Title
st.title("💪 Streak Fitness Tracker")
st.caption("Track your streaks, get fitness tips, and stay motivated!")

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='stChatMessage'>{message['content']}</div>", unsafe_allow_html=True)

# Handle user input
if prompt := st.chat_input("Ask me about workouts, nutrition, or tracking your fitness..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='stChatMessage'>{prompt}</div>", unsafe_allow_html=True)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔑 API key required! Check sidebar settings")
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0

        while attempts < max_retries:
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://fitness-tracker.streamlit.app",
                        "X-Title": "Streak Fitness Tracker"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are a professional fitness coach chatbot for Streak Fitness Tracker. Follow these STRICT rules:
1. RESPOND ONLY IN PLAIN TEXT
2. NEVER USE JSON, MARKDOWN, OR CODE BLOCKS
3. ONLY answer questions related to fitness, workouts, health, diet, and motivation
4. If the query is NOT about fitness, say "I'm here only to talk about your fitness journey!"
5. Format all tips using hyphens (-) only
6. Be supportive and use friendly tone
7. Add line breaks for readability
8. Current date: {time.strftime("%B %d, %Y")}
"""
                            },
                            *st.session_state.messages
                        ],
                        "temperature": temperature
                    },
                    timeout=15
                )

                response.raise_for_status()
                raw_response = response.json()['choices'][0]['message']['content']

                for chunk in raw_response.split():
                    full_response += chunk + " "
                    response_placeholder.markdown(f"<div class='stChatMessage'>{full_response}▌</div>", unsafe_allow_html=True)
                    time.sleep(0.03)

                response_placeholder.markdown(f"<div class='stChatMessage'>{full_response}</div>", unsafe_allow_html=True)
                break

            except requests.exceptions.RequestException as e:
                logging.error(f"Network Error: {str(e)}")
                response_placeholder.error(f"🌐 Network Error: {str(e)}")
                full_response = "Error: Connection issue - try again later"
                break

            except Exception as e:
                logging.error(f"Unexpected Error: {str(e)}")
                response_placeholder.error(f"❌ Unexpected error: {str(e)}")
                full_response = "Error: Please check your input and try again"
                break

    st.session_state.messages.append({"role": "assistant", "content": full_response})
