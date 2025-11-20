"""
Week 5: Voice-Enabled Chatbot
Extends the enhanced chatbot from Week 2 with voice input (STT) and output (TTS)
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from streamlit.runtime.uploaded_file_manager import UploadedFile
import tempfile

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Page config
st.set_page_config(
    page_title="Voice-Enabled AI Chatbot",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Voice-Enabled AI Chatbot")
st.caption("Powered by OpenAI GPT-4 + Whisper (STT) + ElevenLabs (TTS)")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferWindowMemory(
        k=10, 
        memory_key="chat_history", 
        return_messages=True
    )
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = False
if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = "None"
if "transcriber" not in st.session_state:
    st.session_state.transcriber = None

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Voice Input Settings
    st.subheader("🎤 Voice Input (STT)")
    stt_provider = st.selectbox(
        "Speech-to-Text Provider",
        ["None", "OpenAI Whisper"],
        index=1 if OPENAI_API_KEY else 0
    )
    
    # Voice Output Settings
    st.subheader("🔊 Voice Output (TTS)")
    tts_provider = st.selectbox(
        "Text-to-Speech Provider",
        ["None", "ElevenLabs", "OpenAI TTS"],
        index=1 if ELEVENLABS_API_KEY else 0
    )
    
    st.session_state.tts_enabled = tts_provider != "None"
    
    # Conversation Style
    st.subheader("💬 Conversation Style")
    conversation_style = st.selectbox(
        "Select Style",
        ["Friendly", "Professional", "Humorous", "Philosophical", "Concise"],
        index=0
    )
    
    # Voice Settings for TTS
    if st.session_state.tts_enabled and tts_provider == "ElevenLabs":
        st.subheader("🎵 Voice Settings")
        voice_options = {
            "Rachel (Calm Female)": "21m00Tcm4TlvDq8ikWAM",
            "Adam (Deep Male)": "pNInz6obpgDQGcFmaJgB",
            "Antoni (Well-Rounded Male)": "ErXwobaYiN019PkySvjV",
            "Arnold (Crisp Male)": "VR6AewLTigWG4xSOukaG",
            "Bella (Soft Female)": "EXAVITQu4vr4xnSDxMaL",
            "Callum (Video Game)": "N2lVS1w4EtoT3dr4eOWO",
            "Charlie (Casual Male)": "IKne3meq5aSn9XLyUdCD",
            "Domi (Strong Female)": "AZnzlk1XvdvUeBnXmlld",
            "Emily (Calm Female)": "LcfcDJNUP1GQjkzn1xUU",
            "Grace (Young Female)": "oWAxZDx7w5VEj9dCyTzz"
        }
        selected_voice = st.selectbox("Voice", list(voice_options.keys()))
        voice_id = voice_options[selected_voice]
    else:
        voice_id = None
    
    # Clear chat
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.rerun()


def get_whisper_transcription(audio_file: UploadedFile) -> str:
    """Transcribe audio using OpenAI Whisper API"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_path = tmp_file.name
        
        # Transcribe using Whisper
        with open(tmp_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="en"
            )
        
        # Cleanup
        os.unlink(tmp_path)
        
        return transcript.text
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return ""


def generate_elevenlabs_tts(text: str, voice_id: str) -> bytes:
    """Generate speech using ElevenLabs API"""
    try:
        import requests
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"TTS API error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"TTS generation error: {str(e)}")
        return None


def generate_openai_tts(text: str) -> bytes:
    """Generate speech using OpenAI TTS API"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        return response.content
    except Exception as e:
        st.error(f"TTS generation error: {str(e)}")
        return None


# Style-specific prompts
STYLE_PROMPTS = {
    "Friendly": "You are a warm and friendly AI assistant. Use casual language and show empathy.",
    "Professional": "You are a professional AI assistant. Be formal, precise, and business-appropriate.",
    "Humorous": "You are a witty AI assistant. Include humor and lighthearted jokes when appropriate.",
    "Philosophical": "You are a thoughtful AI assistant. Provide deep insights and ask thought-provoking questions.",
    "Concise": "You are a direct AI assistant. Keep responses brief and to the point."
}

# Create chat chain
def create_chat_chain(style: str):
    """Create a chat chain with the specified conversation style"""
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        streaming=True,
        api_key=OPENAI_API_KEY
    )
    
    system_prompt = STYLE_PROMPTS[style]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    return prompt | llm


# Voice Input Section
st.markdown("### 🎤 Voice Input")
if stt_provider == "OpenAI Whisper":
    audio_file = st.audio_input("Record your voice", key="audio_recorder")
    
    if audio_file is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.audio(audio_file)
        
        with col2:
            if st.button("📝 Transcribe", use_container_width=True):
                with st.spinner("Transcribing..."):
                    transcription = get_whisper_transcription(audio_file)
                    if transcription:
                        st.session_state.transcribed_text = transcription
                        st.success("✅ Transcribed!")
        
        # Display transcribed text with option to edit
        if "transcribed_text" in st.session_state and st.session_state.transcribed_text:
            st.info(f"**Transcribed:** {st.session_state.transcribed_text}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Send as message", use_container_width=True):
                    user_input = st.session_state.transcribed_text
                    st.session_state.transcribed_text = ""
                    # Process the message (will be handled below)
                    st.session_state.pending_message = user_input
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.transcribed_text = ""
                    st.rerun()
else:
    st.info("Enable voice input by selecting 'OpenAI Whisper' in the sidebar")

st.divider()

# Display chat messages
st.markdown("### 💬 Chat History")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Play audio if available
        if message["role"] == "assistant" and "audio" in message:
            st.audio(message["audio"], format="audio/mpeg")

# Chat input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.pending_message = prompt

# Handle pending message from voice or text input
if "pending_message" in st.session_state and st.session_state.pending_message:
    user_message = st.session_state.pending_message
    st.session_state.pending_message = ""
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_message})
    st.session_state.memory.chat_memory.add_user_message(user_message)
    
    with st.chat_message("user"):
        st.markdown(user_message)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        chain = create_chat_chain(conversation_style)
        
        try:
            # Get chat history
            chat_history = st.session_state.memory.load_memory_variables({})["chat_history"]
            
            # Stream response
            for chunk in chain.stream({
                "input": user_message,
                "chat_history": chat_history
            }):
                full_response += chunk.content
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Generate TTS if enabled
            audio_data = None
            if st.session_state.tts_enabled:
                with st.spinner("🔊 Generating voice..."):
                    if tts_provider == "ElevenLabs" and voice_id:
                        audio_data = generate_elevenlabs_tts(full_response, voice_id)
                    elif tts_provider == "OpenAI TTS":
                        audio_data = generate_openai_tts(full_response)
                    
                    if audio_data:
                        st.audio(audio_data, format="audio/mpeg")
            
            # Save to memory and history
            st.session_state.memory.chat_memory.add_ai_message(full_response)
            message_dict = {"role": "assistant", "content": full_response}
            if audio_data:
                message_dict["audio"] = audio_data
            st.session_state.messages.append(message_dict)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.caption("🎤 Voice-enabled chatbot with Speech-to-Text (Whisper) and Text-to-Speech (ElevenLabs/OpenAI)")
