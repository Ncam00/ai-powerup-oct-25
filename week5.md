# Week 5: Multimodal AI with Focus on Voice

Welcome to Week 5 of AI Coding Essentials! This week, you'll explore voice-first AI applications by building practical voice interfaces that combine transcription, text-to-speech, and real-time voice APIs. You'll create rich experiences that go beyond text-based interactions.

## Learning Objectives

By the end of this week, you will be able to:
- Implement speech-to-text transcription using Whisper and faster-whisper
- Build text-to-speech solutions using both hosted (ElevenLabs) and open-source (Chatterbox) technologies
- Implement voice cloning using reference audio samples
- Design voice UI patterns with proper error handling and user feedback
- Create multi-provider TTS architecture with fallback strategies
- Optimize performance for real-time voice interactions (lazy loading, device optimization)
- Build complete voice-enabled chatbot interfaces with bidirectional voice communication

## Lecture: Voice-Enabled Chatbots

Examine the AICE chatbot's voice implementation progression through sections 5 and 6, covering the complete journey from voice input to bidirectional voice conversations.

- **[View the Slides](./slides/5-multimodal-voice-export.pdf)** - Complete slide deck covering voice implementation patterns

## Week 5 Exercises

### Core Exercises
1. **[AICE Chatbot Voice](https://github.com/ai-powerup-oct-25/aice-chatbot-voice)** - Extend your chatbot from previous weeks by adding voice capabilities:
   - **Section 5**: Add voice input with Whisper transcription, browser audio recording, and send/cancel controls
   - **Section 6**: Complete the voice interface with TTS (Chatterbox local + ElevenLabs cloud), voice cloning, and quality controls

### Alternative Challenge
1. **Multi-Provider TTS System** - Create a text-to-speech system that supports multiple providers (ElevenLabs for hosted, Chatterbox for open-source) with automatic fallback handling. Reference the implementation in [AICE Chatbot Voice Section 6](https://github.com/ai-powerup-oct-25/aice-chatbot-voice/tree/main/6-tts)

### Optional Exercises
1. **Voice UI Patterns Exploration** - Research and document best practices for voice user interface design, including error handling patterns and user feedback
2. [Continue Your Personal Project](./exercises/plan-your-personal-project.md) - Add multimodal capabilities (especially voice) to your ongoing project
3. **Compare Voice Technologies** - Build a simple demo that lets you compare different TTS engines side-by-side (ElevenLabs vs Chatterbox vs others)
4. **Explore Real-time Voice APIs** - Research OpenAI Realtime API and Google Gemini Live for bidirectional voice conversations

## Weekly Tasks

- [ ] Review the slides:
  - [ ] [Voice-Enabled Chatbots Slides](./slides/5-multimodal-voice-export.pdf)
- [ ] Attend or watch the live Q&A session
- [ ] Complete AICE Chatbot sections 5 & 6 OR build a voice interface implementation
- [ ] Apply what you've learned to your personal project

### Optional
- [ ] Build a multi-provider TTS system with fallback strategies
- [ ] Explore voice UI design patterns and document your findings
- [ ] Research and experiment with OpenAI Realtime API or Google Gemini Live
- [ ] Share your voice-enabled application in the [#show-and-tell Discord channel](https://discord.com/channels/690141234596937780/1427499665812881518)
- [ ] Experiment with different voice models and compare quality/latency trade-offs
- [ ] Try voice cloning with your own reference audio samples

## Key Concepts Covered

- **Speech-to-Text (STT)**: Converting spoken audio into text using Whisper and faster-whisper implementations
- **Text-to-Speech (TTS)**: Generating natural-sounding speech from text using both hosted services (ElevenLabs) and open-source solutions (Chatterbox, Kokoro)
- **Real-time Voice APIs**: Bidirectional voice interaction using OpenAI Realtime API and Google Gemini Live
- **Voice UI Design**: Patterns for creating intuitive voice interfaces with proper feedback and error handling
- **Multi-Provider Architecture**: Building systems that can switch between different TTS providers with fallback strategies
- **Performance Optimization**: Techniques for reducing latency and improving responsiveness in real-time voice applications
- **Voice Integration**: Combining transcription, generation, and synthesis into complete voice-enabled experiences

## Technology Stack

### Speech-to-Text
- **Whisper**: OpenAI's robust speech recognition model
- **faster-whisper**: Optimized implementation for better performance and lower latency

### Text-to-Speech
- **Hosted Solutions**: ElevenLabs API for high-quality commercial TTS with 10 professional voices
- **Open-Source Solutions**: Chatterbox TTS for self-hosted voice generation with voice cloning capabilities

### Browser Integration
- **Streamlit Audio Input**: Native browser-based audio recording (`st.audio_input`)
- **Audio Player**: Inline audio playback with download capabilities

### Performance Optimization
- **PyTorch Isolation**: Custom import system to prevent Streamlit conflicts
- **Lazy Loading**: On-demand model loading for faster startup (5-10x improvement)
- **Device Optimization**: Automatic CUDA/MPS/CPU detection with intelligent fallbacks

---

Remember, voice interfaces require special consideration for user experience. Focus on creating natural interactions with appropriate feedback, clear error handling, and graceful degradation when things go wrong. Take time to experiment with different voice models and providers to understand their trade-offs in quality, latency, and cost!
