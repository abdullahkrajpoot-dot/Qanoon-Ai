import os

import requests
import streamlit as st
from dotenv import load_dotenv


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash"
APP_VERSION = "openrouter-2026-06-09-4"
MAX_OUTPUT_TOKENS = 900

BASE_SYSTEM_PROMPT = (
    "You are Qanoon AI, an expert legal assistant specializing in the laws of Pakistan "
    "(including the Pakistan Penal Code, Constitution of Pakistan, and CrPC). "
    "Provide accurate, helpful, and professional legal citations and explanations based on Pakistani law. "
    "Include a brief note that the answer is informational and not a substitute for a licensed lawyer "
    "when the question asks for legal advice."
)

LANGUAGE_INSTRUCTIONS = {
    "English": "Answer only in clear English.",
    "Urdu": "Answer only in Urdu using Urdu script.",
    "Roman Urdu": "Answer only in Roman Urdu.",
}

CHAT_PLACEHOLDERS = {
    "English": "Ask me about your legal problem...",
    "Urdu": "Apna legal masla yahan likhein...",
    "Roman Urdu": "Apna legal masla yahan likhein...",
}

LOADING_TEXT = {
    "English": "Checking Pakistan legal sources and drafting an answer...",
    "Urdu": "Pakistan ke qanooni sources check kar raha hoon aur jawab tayar kar raha hoon...",
    "Roman Urdu": "Pakistan ke qanooni sources check kar raha hoon aur jawab tayar kar raha hoon...",
}


def get_secret(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None

    return value or os.getenv(name)


def get_openrouter_api_key() -> str | None:
    load_dotenv()
    return get_secret("OPENROUTER_API_KEY")


def build_system_prompt(language: str) -> str:
    return f"{BASE_SYSTEM_PROMPT} {LANGUAGE_INSTRUCTIONS[language]}"


def ask_qanoon_ai(user_query: str, api_key: str, language: str) -> str:
    model = get_secret("OPENROUTER_MODEL") or DEFAULT_MODEL
    messages = [{"role": "system", "content": build_system_prompt(language)}]
    messages.extend(st.session_state.messages[-6:])
    messages.append({"role": "user", "content": user_query})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://qanoon-ai.streamlit.app",
        "X-Title": "Qanoon AI",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": MAX_OUTPUT_TOKENS,
    }

    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if not response.ok:
        try:
            detail = response.json().get("error", {}).get("message", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"OpenRouter error {response.status_code}: {detail}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


st.set_page_config(page_title="Qanoon AI", page_icon="⚖️", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background: #0d1117;
        color: #ffffff;
    }
    .stHeading h1 {
        color: #2ecc71;
        text-align: center;
        font-family: "Helvetica Neue", sans-serif;
    }
    .stChatInput textarea {
        background-color: #1f2937 !important;
        color: white !important;
    }
    .bot-title {
        color: #9aa7c7;
        margin-bottom: 20px;
        text-align: center;
    }
    .version {
        color: #4b5563;
        font-size: 0.72rem;
        margin-top: 1.25rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚖️ Qanoon AI")
st.markdown(
    "<p class='bot-title'>Your Personal AI Legal Assistant for Pakistan Law</p>",
    unsafe_allow_html=True,
)

api_key = get_openrouter_api_key()
language = st.segmented_control(
    "Language",
    options=["English", "Urdu", "Roman Urdu"],
    default="English",
    label_visibility="collapsed",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not api_key:
    st.error("OPENROUTER_API_KEY is missing. Add it to Streamlit secrets or your local .env file.")

if user_query := st.chat_input(CHAT_PLACEHOLDERS[language], disabled=not api_key):
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown(LOADING_TEXT[language])

        try:
            bot_response = ask_qanoon_ai(user_query, api_key, language)
            response_placeholder.markdown(bot_response)

            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
        except Exception as exc:
            response_placeholder.error(str(exc))

st.markdown(f"<p class='version'>{APP_VERSION}</p>", unsafe_allow_html=True)
