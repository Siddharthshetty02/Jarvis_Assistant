import streamlit as st
import speech_recognition as sr
import threading
import asyncio
from backend import ask_ai, check_and_open_site
from utils import safe_speak, stop_audio
from backend import check_and_return_datetime
from backend import web_search_duckduckgo
# ✅ Must be the first Streamlit command
st.set_page_config(
    page_title="Jarvis Assistant",
    layout="centered",
    page_icon="🤖"
)

# ✅ Initialize session state
if "stop_jarvis" not in st.session_state:
    st.session_state.stop_jarvis = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_input" not in st.session_state:
    st.session_state.last_input = ""

# 🔊 Background speech thread launcher
def run_speak(text):
    threading.Thread(target=safe_speak, args=(text,), daemon=True).start()

# 🧠 UI Header
st.markdown("<h1 style='text-align: center;'>🤖 Jarvis - AI Assistant</h1>", unsafe_allow_html=True)

# 🔘 Control Buttons
col1, col2 = st.columns(2)
with col1:
    ask = st.button("Ask Jarvis")
with col2:
    stop = st.button("Stop Jarvis")

# 🛑 Handle Stop
if stop:
    st.session_state.stop_jarvis = True
    stop_audio()
    st.warning("🛑 Jarvis stopped.")
    st.stop()

# 🎤 Input options
use_mic = st.toggle("🎙️ Use Microphone")

if use_mic:
    if st.button("Record Voice"):
        with st.spinner("🎤 Listening..."):
            r = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source, timeout=5)
                user_input = r.recognize_google(audio)
                st.session_state.last_input = user_input
                st.success(f"✅ You said: {user_input}")
            except sr.UnknownValueError:
                st.warning("❌ Could not understand audio.")
                st.stop()
            except sr.RequestError:
                st.error("🔌 Network error with speech recognition service.")
                st.stop()
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                st.stop()
else:
    user_input = st.text_input("Type your question")
    st.session_state.last_input = user_input

# 🚪 Exit command keywords
EXIT_COMMANDS = {"exit", "quit", "stop", "bye", "goodbye"}


# this initializes after the activating jarvis
# 💬 Ask Jarvis Logic
if ask and st.session_state.last_input.strip() != "":
    user_msg = st.session_state.last_input.strip()

    # 🔗 Check for site command
    if check_and_open_site(user_msg):
        site = user_msg.split()[-1]
        run_speak(f"Opening {site}")
        st.success(f"🔗 Opened {site.title()} in browser!")
        st.stop()
    dt_response = check_and_return_datetime(user_msg)
    if dt_response:
        st.session_state.chat_history.append({"role": "assistant", "content": dt_response})
        st.success("Jarvis replied:")
        st.write(dt_response)
        stop_audio()
        run_speak(dt_response)
        st.stop()
    # 👋 Exit Jarvis
    if user_msg.lower() in EXIT_COMMANDS:
        run_speak("Goodbye!")
        st.success("👋 Jarvis: Goodbye!")
        st.session_state.chat_history.clear()
        st.stop()

    if st.session_state.stop_jarvis:
        st.warning("🛑 Jarvis was stopped before answering.")
        st.session_state.stop_jarvis = False
        st.stop()

    with st.spinner("💭 Jarvis is thinking..."):
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        ai_reply = ask_ai(user_msg, st.session_state.chat_history)

    # Handle unexpected stop
    if st.session_state.stop_jarvis:
        st.warning("🛑 Jarvis was stopped before speaking.")
        st.session_state.stop_jarvis = False
        st.stop()
        
    # 🔍 Check for web search command (e.g., starts with "search" or "look up")
    if user_msg.lower().startswith(("search", "look up", "find")):
        search_query = user_msg.partition(" ")[2]
        with st.spinner("🔍 Searching the web..."):
            try:
                result = asyncio.run(web_search_duckduckgo(search_query))
            except RuntimeError:
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(web_search_duckduckgo(search_query))

            st.success("🌐 Web Results:")
            st.markdown(result)
        st.stop()
        
        
    # Show and speak reply
    st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
    st.success("🤖 Jarvis replied:")
    st.write(ai_reply)

    stop_audio()
    run_speak(ai_reply)

# 📝 Conversation History
st.markdown("### 📝 Conversation")
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Jarvis:** {msg['content']}")
