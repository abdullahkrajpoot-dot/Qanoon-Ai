import streamlit as st
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(page_title="Qanoon AI", page_icon="⚖️", layout="centered")

# Custom UI Styling
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #ffffff; }
    .stHeading h1 { color: #2ecc71; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    .stChatInput input { background-color: #1f2937 !important; color: white !important; }
    .bot-title { text-align: center; color: #8892b0; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ Qanoon AI")
st.markdown("<p class='bot-title'>Your Personal AI Legal Assistant for Pakistan Law</p>", unsafe_allow_html=True)

# New 2026 Official Client Setup (No more 404/v1beta issues)
GEMINI_API_KEY = "AIzaSyB3mfOVLN_3rGI1UIH14-1JC7Pmfzfpg6c"
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are Qanoon AI, an expert legal assistant specializing in the laws of Pakistan "
    "(including the Pakistan Penal Code, Constitution of Pakistan, and CrPC). "
    "Provide accurate, helpful, and professional legal citations and explanations based on Pakistani law. "
    "Answer in English or Roman Urdu depending on how the user asks."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Ask me about your legal problem..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("🔍 Checking Pakistan Legal Database...")
        
        try:
            # New standard configuration block
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            )
            
            # Direct official model hit
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_query,
                config=config
            )
            
            bot_response = response.text
            response_placeholder.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
        except Exception as e:
            response_placeholder.markdown(f"❌ Error: {str(e)}")