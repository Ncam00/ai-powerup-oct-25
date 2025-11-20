"""
Voice Cloning Demo - Zero-Shot Voice Replication
Demonstrates voice cloning using ElevenLabs API with custom voice samples

IMPORTANT: This is for educational purposes. Always get consent before cloning someone's voice.
"""

import os
import requests
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

st.set_page_config(
    page_title="Voice Cloning Demo",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 Voice Cloning Demo")
st.caption("Zero-shot voice replication using ElevenLabs Instant Voice Cloning")

# Educational warning
st.warning("""
⚠️ **Ethical Use Only**

Voice cloning technology should only be used with proper consent:
- ✅ Clone your own voice
- ✅ Clone voices with written permission
- ✅ Use for accessibility (helping those who lost their voice)
- ✅ Creative projects with consent

- ❌ Impersonation without consent
- ❌ Fraud or deception
- ❌ Deepfakes
- ❌ Any harmful use

**By using this demo, you confirm you have the right to clone the uploaded voice.**
""")

if not ELEVENLABS_API_KEY:
    st.error("❌ ELEVENLABS_API_KEY not found in environment variables")
    st.info("Get your API key from: https://elevenlabs.io/")
    st.stop()

# Sidebar - Instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    ### How Voice Cloning Works
    
    1. **Upload Reference Audio**
       - 30 seconds to 2 minutes recommended
       - Clear speech, minimal background noise
       - Single speaker only
       - WAV, MP3, or M4A format
    
    2. **Create Custom Voice**
       - API analyzes speech patterns
       - Extracts voice characteristics
       - Generates unique voice ID
    
    3. **Generate Speech**
       - Type any text
       - AI speaks in cloned voice
       - Maintains emotion and tone
    
    ### Quality Tips
    - 📱 Record in quiet environment
    - 🎤 Use good quality microphone
    - 🗣️ Speak naturally and clearly
    - ⏱️ Longer samples = better quality
    - 🎵 Varied emotions help capture range
    """)


def upload_voice_sample(file_path: str, voice_name: str, voice_description: str = "") -> dict:
    """
    Upload a voice sample to ElevenLabs and create a cloned voice
    
    Args:
        file_path: Path to audio file
        voice_name: Name for the cloned voice
        voice_description: Optional description
    
    Returns:
        dict with voice_id and other details
    """
    url = "https://api.elevenlabs.io/v1/voices/add"
    
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    # Read audio file
    with open(file_path, 'rb') as audio_file:
        files = {
            'files': audio_file
        }
        
        data = {
            'name': voice_name,
            'description': voice_description or f"Custom cloned voice: {voice_name}",
            'labels': '{"use_case": "demo", "type": "cloned"}'
        }
        
        response = requests.post(url, headers=headers, data=data, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Voice upload failed: {response.status_code} - {response.text}")


def generate_speech_from_cloned_voice(text: str, voice_id: str) -> bytes:
    """
    Generate speech using a cloned voice
    
    Args:
        text: Text to convert to speech
        voice_id: ID of the cloned voice
    
    Returns:
        Audio bytes (MP3 format)
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # Best model for cloned voices
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,  # Higher = more like original
            "style": 0.0,  # 0-1, how expressive
            "use_speaker_boost": True  # Enhance voice characteristics
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"TTS generation failed: {response.status_code} - {response.text}")


def get_available_voices() -> list:
    """Get list of all available voices including custom cloned ones"""
    url = "https://api.elevenlabs.io/v1/voices"
    
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('voices', [])
    else:
        return []


def delete_voice(voice_id: str) -> bool:
    """Delete a custom voice"""
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
    
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    response = requests.delete(url, headers=headers)
    return response.status_code == 200


# Main interface
tab1, tab2, tab3 = st.tabs(["🎤 Clone Voice", "🗣️ Use Cloned Voice", "📚 Manage Voices"])

with tab1:
    st.header("🎤 Clone a Voice")
    
    st.info("""
    **Best Practices for Reference Audio:**
    - Duration: 30 seconds to 2 minutes
    - Content: Natural speech, varied sentences
    - Quality: Clear recording, minimal background noise
    - Speaker: Single person only
    - Emotion: Variety helps (happy, sad, excited, calm)
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Reference Audio",
            type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
            help="Upload a clear audio sample of the voice you want to clone"
        )
        
        if uploaded_file:
            st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
            
            # Show file details
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
            st.caption(f"File: {uploaded_file.name} ({file_size:.2f} MB)")
    
    with col2:
        voice_name = st.text_input(
            "Voice Name",
            placeholder="e.g., My Voice, John's Voice",
            help="A unique name for this cloned voice"
        )
        
        voice_description = st.text_area(
            "Description (Optional)",
            placeholder="e.g., My personal voice for demos",
            help="Optional description for this voice"
        )
    
    if st.button("🎭 Clone This Voice", type="primary", disabled=not (uploaded_file and voice_name)):
        with st.spinner("Cloning voice... This may take 30-60 seconds..."):
            try:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                # Upload and clone voice
                result = upload_voice_sample(temp_path, voice_name, voice_description)
                
                # Cleanup temp file
                os.unlink(temp_path)
                
                # Show success
                st.success(f"✅ Voice cloned successfully!")
                st.json(result)
                
                # Save voice ID to session state
                st.session_state.last_cloned_voice_id = result['voice_id']
                st.session_state.last_cloned_voice_name = voice_name
                
                st.info("👉 Go to the **Use Cloned Voice** tab to test it!")
                
            except Exception as e:
                st.error(f"❌ Error cloning voice: {str(e)}")

with tab2:
    st.header("🗣️ Use Cloned Voice")
    
    # Get available voices
    with st.spinner("Loading available voices..."):
        voices = get_available_voices()
    
    if not voices:
        st.warning("No voices available. Clone a voice first or check your API key.")
    else:
        # Separate custom (cloned) vs preset voices
        custom_voices = [v for v in voices if not v.get('category') == 'premade']
        preset_voices = [v for v in voices if v.get('category') == 'premade']
        
        st.subheader("Select Voice")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Your Cloned Voices:**")
            if custom_voices:
                for voice in custom_voices:
                    if st.button(f"🎭 {voice['name']}", key=f"select_{voice['voice_id']}"):
                        st.session_state.selected_voice = voice
                        st.rerun()
            else:
                st.info("No custom voices yet. Clone one in the first tab!")
        
        with col2:
            st.markdown("**Preset Voices:**")
            for voice in preset_voices[:5]:  # Show first 5
                if st.button(f"🎵 {voice['name']}", key=f"select_{voice['voice_id']}"):
                    st.session_state.selected_voice = voice
                    st.rerun()
        
        # Selected voice info
        if 'selected_voice' in st.session_state:
            voice = st.session_state.selected_voice
            
            st.divider()
            st.subheader(f"Using: {voice['name']}")
            
            if voice.get('description'):
                st.caption(voice['description'])
            
            # Advanced settings
            with st.expander("⚙️ Advanced Voice Settings"):
                col1, col2 = st.columns(2)
                
                with col1:
                    stability = st.slider(
                        "Stability",
                        0.0, 1.0, 0.5,
                        help="Higher = more consistent, Lower = more variable"
                    )
                    
                    style = st.slider(
                        "Style Exaggeration",
                        0.0, 1.0, 0.0,
                        help="How much to exaggerate the speaking style"
                    )
                
                with col2:
                    similarity_boost = st.slider(
                        "Similarity Boost",
                        0.0, 1.0, 0.75,
                        help="Higher = more like original voice"
                    )
                    
                    speaker_boost = st.checkbox(
                        "Speaker Boost",
                        value=True,
                        help="Enhance voice clarity and characteristics"
                    )
            
            # Text to speak
            text_to_speak = st.text_area(
                "Enter text to speak",
                value="Hello! This is a demonstration of voice cloning technology. Amazing, isn't it?",
                height=150,
                max_chars=5000,
                help="Type the text you want the cloned voice to say"
            )
            
            char_count = len(text_to_speak)
            st.caption(f"Characters: {char_count} / 5000")
            
            if st.button("🎙️ Generate Speech", type="primary", disabled=not text_to_speak):
                with st.spinner("Generating speech with cloned voice..."):
                    try:
                        # Generate speech with custom settings
                        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice['voice_id']}"
                        
                        headers = {
                            "Accept": "audio/mpeg",
                            "Content-Type": "application/json",
                            "xi-api-key": ELEVENLABS_API_KEY
                        }
                        
                        data = {
                            "text": text_to_speak,
                            "model_id": "eleven_multilingual_v2",
                            "voice_settings": {
                                "stability": stability,
                                "similarity_boost": similarity_boost,
                                "style": style,
                                "use_speaker_boost": speaker_boost
                            }
                        }
                        
                        response = requests.post(url, json=data, headers=headers)
                        
                        if response.status_code == 200:
                            audio_data = response.content
                            
                            st.success("✅ Speech generated!")
                            st.audio(audio_data, format='audio/mpeg')
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download Audio",
                                data=audio_data,
                                file_name=f"{voice['name']}_cloned_speech.mp3",
                                mime="audio/mpeg"
                            )
                        else:
                            st.error(f"❌ Generation failed: {response.status_code} - {response.text}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

with tab3:
    st.header("📚 Manage Your Cloned Voices")
    
    with st.spinner("Loading voices..."):
        voices = get_available_voices()
        custom_voices = [v for v in voices if not v.get('category') == 'premade']
    
    if not custom_voices:
        st.info("You haven't cloned any voices yet. Head to the **Clone Voice** tab to get started!")
    else:
        st.write(f"You have {len(custom_voices)} custom voice(s):")
        
        for voice in custom_voices:
            with st.expander(f"🎭 {voice['name']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Voice ID:** `{voice['voice_id']}`")
                    if voice.get('description'):
                        st.write(f"**Description:** {voice['description']}")
                    
                    # Show labels if any
                    if voice.get('labels'):
                        st.write(f"**Labels:** {voice['labels']}")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{voice['voice_id']}"):
                        with st.spinner(f"Deleting {voice['name']}..."):
                            if delete_voice(voice['voice_id']):
                                st.success("✅ Voice deleted!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete voice")

# Footer
st.divider()
st.markdown("""
### 📖 About Voice Cloning

**How It Works:**
1. Upload a reference audio sample (30s - 2min recommended)
2. AI analyzes speech patterns, pitch, tone, and rhythm
3. Creates a unique voice model that can speak any text
4. Model maintains the original voice's characteristics

**Use Cases:**
- 🎬 Content creation (with permission)
- ♿ Accessibility (voice restoration for those who lost their voice)
- 🎮 Gaming characters
- 📚 Audiobook narration
- 🎓 Educational content

**Technical Details:**
- Model: ElevenLabs Eleven Multilingual v2
- Languages: 29 languages supported
- Quality: Professional studio-grade
- Latency: 1-3 seconds for generation

**Privacy & Ethics:**
- Only clone voices you have permission to use
- ElevenLabs API has built-in safety measures
- Audio samples are not shared publicly
- Use responsibly and ethically

---

💡 **Tip**: For best results, provide audio with varied emotions and speaking styles. 
The AI learns better from diverse samples!
""")

st.caption("Built with ❤️ for Week 5 Optional Exercises | Powered by ElevenLabs API")
