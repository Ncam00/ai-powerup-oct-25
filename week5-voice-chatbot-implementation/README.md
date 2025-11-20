# Week 5: Voice-Enabled Chatbot

## Overview
This implementation extends the enhanced chatbot from Week 2 by adding voice capabilities:
- **Voice Input (STT)**: OpenAI Whisper for speech-to-text transcription
- **Voice Output (TTS)**: ElevenLabs and OpenAI TTS for text-to-speech
- **Multi-Modal Interface**: Seamless switching between text and voice input

## Features

### Voice Input (Speech-to-Text)
- Browser-based audio recording using Streamlit's `st.audio_input`
- OpenAI Whisper API integration for high-quality transcription
- Review and edit transcribed text before sending
- Send/Cancel controls for user confirmation

### Voice Output (Text-to-Speech)
- **ElevenLabs TTS**: 10 professional voice options with natural prosody
- **OpenAI TTS**: Alternative provider with "alloy" voice
- Real-time audio generation for assistant responses
- Inline audio player with download capabilities
- Audio saved with message history for replay

### Conversation Styles (from Week 2)
- Friendly - Warm and empathetic
- Professional - Formal and business-appropriate  
- Humorous - Witty with jokes
- Philosophical - Deep and thought-provoking
- Concise - Brief and direct

### Memory Management (from Week 2)
- ConversationBufferWindowMemory with 10-message window
- Conversation history preserved across interactions
- Clear chat functionality to reset context

## Installation

### Prerequisites
```bash
# Python 3.10+
python --version

# Install dependencies
pip install streamlit langchain langchain-openai openai requests python-dotenv
```

### Environment Setup
Create a `.env` file:
```env
# Required for chatbot
OPENAI_API_KEY=your-openai-api-key-here

# Optional for ElevenLabs TTS (otherwise use OpenAI TTS)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

### Getting API Keys

1. **OpenAI API Key** (Required)
   - Sign up at https://platform.openai.com/
   - Navigate to API Keys section
   - Create new secret key
   - Provides access to GPT-4, Whisper, and TTS

2. **ElevenLabs API Key** (Optional)
   - Sign up at https://elevenlabs.io/
   - Free tier includes 10,000 characters/month
   - Professional voices with emotional range
   - Alternative: Use OpenAI TTS instead

## Usage

### Running the Application
```bash
streamlit run voice_chatbot.py
```

The app will open in your browser at `http://localhost:8501`

### Voice Input Workflow
1. Click the microphone icon to start recording
2. Speak your message clearly
3. Click "Stop Recording" when done
4. Review the transcribed text
5. Click "Send as message" to submit or "Cancel" to discard

### Voice Output
- Enable TTS in sidebar settings
- Choose provider (ElevenLabs or OpenAI TTS)
- Select voice (10 options for ElevenLabs)
- Assistant responses automatically generate audio
- Play inline or download for later

### Text Input (Traditional)
- Type in the chat input box at the bottom
- Press Enter to send
- Works alongside voice input

## Architecture

### Components
- **Streamlit UI**: Web interface with audio components
- **LangChain**: Conversation management and memory
- **OpenAI Whisper**: Speech-to-text transcription
- **ElevenLabs/OpenAI TTS**: Text-to-speech synthesis
- **Session State**: Preserves messages, memory, and settings

### Data Flow
```
User Voice Input → Whisper API → Transcription → Review → GPT-4 → Response → TTS API → Audio Output
User Text Input → GPT-4 → Response → TTS API (optional) → Audio Output
```

## Key Learning Objectives (Week 5)

### ✅ Speech-to-Text Implementation
- Browser audio recording with Streamlit
- Whisper API integration and error handling
- Audio file management and cleanup
- Transcription quality validation

### ✅ Text-to-Speech Implementation  
- Multi-provider TTS architecture (ElevenLabs + OpenAI)
- Voice selection and customization
- Audio generation and streaming
- Performance optimization for real-time interactions

### ✅ Voice UI Design Patterns
- Send/Cancel controls for user confirmation
- Visual feedback for recording and transcription status
- Inline audio player for message history
- Graceful error handling and fallback strategies

### ✅ Integration Skills
- Combining voice input and output seamlessly
- Preserving conversation context across modalities
- Session state management for audio components
- API rate limiting and error recovery

## Challenges and Solutions

### Challenge 1: Audio File Handling
**Problem**: Streamlit UploadedFile objects need temporary storage for API calls
**Solution**: Use `tempfile.NamedTemporaryFile` with automatic cleanup

### Challenge 2: Async Audio Generation
**Problem**: TTS generation can block the UI
**Solution**: Show spinner feedback and generate audio after displaying text response

### Challenge 3: Message History with Audio
**Problem**: Need to store and replay audio with messages
**Solution**: Save audio bytes in message dict, display with st.audio() in history

### Challenge 4: State Management
**Problem**: Audio input persists after message sent
**Solution**: Track pending messages in session state, clear after processing

## Future Enhancements

1. **Voice Cloning**: Upload reference audio for personalized voices
2. **Real-time Streaming**: Use OpenAI Realtime API for bidirectional voice
3. **Emotion Detection**: Analyze voice sentiment and adjust responses
4. **Multi-language Support**: Extend beyond English for global users
5. **Local Models**: Add faster-whisper and Chatterbox for privacy
6. **Performance Optimization**: Lazy loading, caching, device optimization

## References
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech)
- [ElevenLabs API](https://elevenlabs.io/docs/api-reference)
- [Streamlit Audio Components](https://docs.streamlit.io/library/api-reference/media)
- [LangChain Memory](https://python.langchain.com/docs/modules/memory/)

## Week 5 Completion Checklist
- ✅ Implemented voice input with Whisper transcription
- ✅ Added text-to-speech with multiple providers
- ✅ Created voice UI patterns with proper feedback
- ✅ Built multi-provider TTS architecture with fallback
- ✅ Optimized for real-time voice interactions
- ✅ Maintained conversation memory across modalities
- ✅ Tested complete voice workflow end-to-end
