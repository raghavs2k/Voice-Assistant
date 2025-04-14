import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import time
import base64
from io import BytesIO
import json
from datetime import datetime

# Set page config and theme
st.set_page_config(
    page_title="Merchant Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }
    .chat-message-bot {
        background-color: #f0f2f5;
        padding: 1rem;
        border-radius: 1rem;
        border-bottom-left-radius: 0.25rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        width: fit-content;
        max-width: 80%;
    }
    .chat-message-user {
        background-color: #6c5ce7;
        color: white;
        padding: 1rem;
        border-radius: 1rem;
        border-bottom-right-radius: 0.25rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        width: fit-content;
        max-width: 80%;
        margin-left: auto;
    }
    .chat-message-time {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    .user-time {
        color: #c7d2fe;
    }
    .chat-header {
        display: flex;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        background-color: #192738;
        color: white;
    }
    .assistant-icon {
        width: 40px;
        height: 40px;
        background-color: #6c5ce7;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        margin-right: 1rem;
    }
    .assistant-info {
        display: flex;
        flex-direction: column;
    }
    .assistant-name {
        font-weight: 600;
        font-size: 1.1rem;
    }
    .assistant-status {
        display: flex;
        align-items: center;
        color: #10b981;
        font-size: 0.85rem;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        margin-right: 5px;
    }
    .voice-btn {
        background-color: #6c5ce7 !important;
        color: white !important;
    }
    .send-btn {
        background-color: #6c5ce7 !important;
        color: white !important;
    }
    .stTextInput>div>div>input {
        border-radius: 1.5rem;
    }
    /* Audio player styling */
    .audio-player-container {
        margin-top: 0.5rem;
    }
    .audio-player {
        width: 100%;
        height: 30px;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    initial_message = {
        "role": "assistant",
        "content": "Hello! I'm your merchant assistant. You can type your questions or click the microphone button to speak. How can I help you today?",
        "time": "10:18 AM"
    }
    st.session_state.messages.append(initial_message)
    
    # Generate initial audio once
    tts = gTTS(text=initial_message["content"], lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    initial_message["audio"] = fp.getvalue()

# Audio functions
def create_audio_player(audio_data, autoplay=False):
    b64 = base64.b64encode(audio_data).decode()
    audio_tag = f"""
    <div class="audio-player-container">
        <audio {'autoplay' if autoplay else ''} controls class="audio-player">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    </div>
    """
    return audio_tag

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

def save_voice_recording():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            with st.spinner("🎤 Listening... Speak now!"):
                audio = r.listen(source)
                
                # Get the raw audio data
                wav_data = BytesIO(audio.get_wav_data())
                wav_data.seek(0)
                raw_audio = wav_data.getvalue()
                
                # Transcribe to text
                try:
                    text = r.recognize_google(audio)
                    return {
                        "text": text,
                        "voice_data": raw_audio
                    }
                except sr.UnknownValueError:
                    st.error("Could not understand audio. Please try again.")
                    return None
                except sr.RequestError:
                    st.error("Could not request results. Please check your internet connection.")
                    return None
    except Exception as e:
        error_message = str(e)
        if "PyAudio" in error_message:
            st.error("PyAudio is not installed. Run: brew install portaudio && pip install pyaudio")
        elif "FLAC" in error_message:
            st.error("FLAC is not installed. Run: brew install flac")
        else:
            st.error(f"Error accessing microphone: {error_message}")
        return None

# Main chat container with fixed width
chat_container = st.container()

# Chat header
with chat_container:
    st.markdown("""
    <div class="chat-header">
        <div class="assistant-icon">🤖</div>
        <div class="assistant-info">
            <div class="assistant-name">Merchant Assistant</div>
            <div class="assistant-status">
                <div class="status-dot"></div>
                Online
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]
        time = message.get("time", datetime.now().strftime("%I:%M %p"))
        
        # Start message container
        message_html = ""
        
        if role == "assistant":
            message_html += f"""
            <div class="chat-message-bot">
                {content}
                <div class="chat-message-time">{time}</div>
            """
        else:
            message_html += f"""
            <div class="chat-message-user">
                {content}
                <div class="chat-message-time user-time">{time}</div>
            """
        
        # Add audio player if available - only in the message itself
        if role == "assistant" and "audio" in message:
            # For the newest message, enable autoplay. For others, just controls.
            autoplay = (idx == len(st.session_state.messages) - 1 and message.get("should_autoplay", False))
            message_html += create_audio_player(message["audio"], autoplay=autoplay)
            
            # Mark as played so it doesn't autoplay again on page refresh
            if autoplay:
                message["should_autoplay"] = False
                
        elif role == "user" and "voice_data" in message:
            message_html += create_audio_player(message["voice_data"])
            
        # Close message container
        message_html += "</div>"
        
        # Render message
        st.markdown(message_html, unsafe_allow_html=True)

# Input area
st.markdown("<hr style='margin-top: 2rem; margin-bottom: 1rem; opacity: 0.3;'>", unsafe_allow_html=True)

# Input container with columns
col1, col2, col3 = st.columns([1, 10, 1])

with col1:
    voice_button = st.button("🎤", key="voice_button", help="Click to speak", use_container_width=True)

with col2:
    # Clear input after sending
    if "clear_input" not in st.session_state:
        st.session_state.clear_input = ""
        
    user_input = st.text_input("Type your message...", key="user_input", 
                              value=st.session_state.clear_input,
                              label_visibility="collapsed")

with col3:
    send_button = st.button("➤", key="send_button", help="Send message", use_container_width=True)

# Handle voice input
if voice_button:
    voice_result = save_voice_recording()
    if voice_result and 'last_user_input' not in st.session_state:
        st.session_state.last_user_input = voice_result["text"]
        
        # Add user message with voice data
        user_message = {
            "role": "user",
            "content": f"🎤 {voice_result['text']}",
            "time": datetime.now().strftime("%I:%M %p"),
            "voice_data": voice_result["voice_data"]
        }
        st.session_state.messages.append(user_message)
        
        # Generate bot response with audio
        bot_response = f"I received your voice message: {voice_result['text']}"
        bot_audio = text_to_speech(bot_response)
        
        if bot_audio:
            bot_message = {
                "role": "assistant",
                "content": bot_response,
                "time": datetime.now().strftime("%I:%M %p"),
                "audio": bot_audio,
                "should_autoplay": True
            }
            st.session_state.messages.append(bot_message)
            
        # Clear input field for next message
        st.session_state.clear_input = ""
        st.rerun()

# Handle text input
if send_button or (user_input and user_input != st.session_state.get('prev_input', '')):
    if user_input and 'last_user_input' not in st.session_state:
        st.session_state.prev_input = user_input
        st.session_state.last_user_input = user_input
        
        # Add user message
        user_message = {
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%I:%M %p")
        }
        st.session_state.messages.append(user_message)
        
        # Generate bot response with audio
        bot_response = f"I received your message: {user_input}"
        bot_audio = text_to_speech(bot_response)
        
        if bot_audio:
            bot_message = {
                "role": "assistant",
                "content": bot_response,
                "time": datetime.now().strftime("%I:%M %p"),
                "audio": bot_audio,
                "should_autoplay": True
            }
            st.session_state.messages.append(bot_message)
        
        # Clear input field for next message
        st.session_state.clear_input = ""
        st.rerun()

# Clear last_user_input after the rerun
if 'last_user_input' in st.session_state:
    del st.session_state.last_user_input 