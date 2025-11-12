"""
LangChain Joke Teller - Week 2 Optional Exercise
A specialized AI comedian using LangChain with different humor styles and joke categories
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
import random
import time
from datetime import datetime

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state for the joke teller"""
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if "joke_history" not in st.session_state:
        st.session_state.joke_history = []
    if "favorite_jokes" not in st.session_state:
        st.session_state.favorite_jokes = []

def create_joke_prompt(joke_type, style, topic=None):
    """Create specialized prompts for different types of jokes"""
    
    style_instructions = {
        "dad": "Create dad jokes that are wonderfully cheesy, punny, and groan-worthy. Use simple setups with punchy punchlines.",
        "witty": "Create clever, sophisticated humor with wordplay, irony, and intelligent observations.",
        "clean": "Create family-friendly humor that's appropriate for all ages. Be wholesome and positive.",
        "nerdy": "Create geeky humor about technology, science, programming, or academic subjects.",
        "observational": "Create humor based on everyday observations and common experiences that everyone can relate to."
    }
    
    joke_type_instructions = {
        "one_liner": "Create a single-sentence joke that delivers the punchline quickly.",
        "setup_punchline": "Create a classic setup-and-punchline format joke with a clear question/answer or statement/response structure.",
        "story": "Create a short, humorous story with a funny conclusion or twist.",
        "riddle": "Create a riddle-style joke where the answer is the punchline."
    }
    
    base_prompt = f"""You are a professional comedian AI with a specialty in {style} humor. 
Your task is to create {joke_type_instructions[joke_type]}

Style: {style_instructions[style]}

Guidelines:
- Keep it {style} in tone
- Make it genuinely funny, not just silly
- Ensure the punchline is surprising but logical
- Length appropriate for the joke type
- Be original and creative"""

    if topic:
        base_prompt += f"\nTopic: Create a joke about {topic}"
    
    base_prompt += "\n\nJoke:"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", base_prompt),
        ("human", "Tell me a joke!")
    ])
    
    return prompt

def setup_joke_llm(api_key: str):
    """Setup the LLM for joke generation"""
    if not api_key:
        st.error("Please provide an OpenAI API key!")
        st.stop()
    
    return ChatOpenAI(
        api_key=api_key,
        model="gpt-3.5-turbo",
        temperature=0.9,  # Higher creativity for jokes
        streaming=False
    )

def generate_joke(joke_type, style, topic=None, custom_prompt=None):
    """Generate a joke using LangChain"""
    try:
        llm = setup_joke_llm(st.session_state.openai_api_key)
        
        if custom_prompt:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a professional comedian AI. Create original, funny jokes based on the user's request."),
                ("human", custom_prompt)
            ])
        else:
            prompt = create_joke_prompt(joke_type, style, topic)
        
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({})
        
        # Clean up the response
        joke = response.strip()
        if joke.startswith("Joke:"):
            joke = joke[5:].strip()
        
        return joke
    except Exception as e:
        st.error(f"Error generating joke: {str(e)}")
        return None

def save_joke_to_history(joke, joke_type, style, topic=None):
    """Save joke to session history"""
    joke_entry = {
        "joke": joke,
        "type": joke_type,
        "style": style,
        "topic": topic,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.joke_history.append(joke_entry)

def render_joke_generator():
    """Render the main joke generation interface"""
    st.title("🎭 LangChain Joke Teller")
    st.markdown("*Your AI comedian powered by LangChain*")
    
    if not st.session_state.openai_api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar!")
        return
    
    # Joke generation controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Joke Type")
        joke_type = st.selectbox(
            "Choose joke format:",
            ["one_liner", "setup_punchline", "story", "riddle"],
            format_func=lambda x: {
                "one_liner": "🎯 One-liner",
                "setup_punchline": "❓ Setup & Punchline",
                "story": "📖 Short Story",
                "riddle": "🧩 Riddle"
            }[x]
        )
    
    with col2:
        st.subheader("😄 Humor Style")
        humor_style = st.selectbox(
            "Choose humor style:",
            ["dad", "witty", "clean", "nerdy", "observational"],
            format_func=lambda x: {
                "dad": "👨 Dad Jokes",
                "witty": "🧠 Witty & Clever", 
                "clean": "👪 Family-Friendly",
                "nerdy": "🤓 Geeky & Nerdy",
                "observational": "👁️ Observational"
            }[x]
        )
    
    # Optional topic
    st.subheader("📚 Topic (Optional)")
    topic = st.text_input("Enter a specific topic for your joke (leave blank for any topic):")
    
    # Custom prompt option
    with st.expander("🎨 Advanced: Custom Prompt"):
        custom_prompt = st.text_area(
            "Write your own joke request:",
            placeholder="e.g., 'Tell me a joke about a programmer who walks into a coffee shop...'"
        )
    
    # Generate joke button
    if st.button("🎲 Generate Joke!", type="primary", use_container_width=True):
        with st.spinner("🤔 Crafting the perfect joke..."):
            joke = generate_joke(
                joke_type=joke_type,
                style=humor_style,
                topic=topic if topic.strip() else None,
                custom_prompt=custom_prompt if custom_prompt.strip() else None
            )
            
            if joke:
                # Display the joke with nice formatting
                st.success("🎉 Fresh joke served!")
                
                # Create a nice joke display
                joke_container = st.container()
                with joke_container:
                    st.markdown("---")
                    st.markdown(f"### {joke}")
                    st.markdown("---")
                    
                    # Joke actions
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("❤️ Love it!", key="love"):
                            if joke not in [fav["joke"] for fav in st.session_state.favorite_jokes]:
                                st.session_state.favorite_jokes.append({
                                    "joke": joke,
                                    "type": joke_type,
                                    "style": humor_style,
                                    "topic": topic,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                st.success("Added to favorites!")
                            else:
                                st.info("Already in favorites!")
                    
                    with col2:
                        if st.button("🔄 Another one!", key="another"):
                            st.rerun()
                    
                    with col3:
                        st.download_button(
                            "📋 Copy Joke",
                            data=joke,
                            file_name=f"joke_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                
                # Save to history
                save_joke_to_history(joke, joke_type, humor_style, topic)

def render_sidebar():
    """Render the sidebar with settings and history"""
    with st.sidebar:
        st.title("🎭 Joke Controls")
        
        # API Key
        api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_api_key,
            type="password",
            help="Enter your OpenAI API key"
        )
        st.session_state.openai_api_key = api_key
        
        st.divider()
        
        # Quick joke buttons
        st.subheader("⚡ Quick Jokes")
        
        quick_jokes = [
            ("🍕", "dad", "food"),
            ("💻", "nerdy", "programming"), 
            ("🐶", "clean", "animals"),
            ("☕", "observational", "coffee"),
            ("🎯", "witty", "work")
        ]
        
        for icon, style, topic in quick_jokes:
            if st.button(f"{icon} {topic.title()}", key=f"quick_{topic}", use_container_width=True):
                joke = generate_joke("setup_punchline", style, topic)
                if joke:
                    st.info(f"**{topic.title()} Joke:**\n\n{joke}")
                    save_joke_to_history(joke, "setup_punchline", style, topic)
        
        st.divider()
        
        # Stats
        st.subheader("📊 Comedy Stats")
        st.metric("Total Jokes", len(st.session_state.joke_history))
        st.metric("Favorites", len(st.session_state.favorite_jokes))
        
        # Random joke from history
        if st.session_state.joke_history and st.button("🎲 Random from History"):
            random_joke = random.choice(st.session_state.joke_history)
            st.info(f"**Random Joke:**\n\n{random_joke['joke']}")

def render_joke_history():
    """Render joke history and favorites"""
    if st.session_state.favorite_jokes:
        st.subheader("❤️ Favorite Jokes")
        for i, fav in enumerate(reversed(st.session_state.favorite_jokes[-5:])):  # Show last 5
            with st.expander(f"{fav['style'].title()} {fav['type']} - {fav['timestamp']}"):
                st.markdown(f"**{fav['joke']}**")
                if st.button(f"Remove from favorites", key=f"remove_fav_{i}"):
                    st.session_state.favorite_jokes.remove(fav)
                    st.rerun()
    
    if st.session_state.joke_history:
        st.subheader("📜 Recent Jokes")
        for joke_entry in reversed(st.session_state.joke_history[-10:]):  # Show last 10
            with st.expander(f"{joke_entry['style'].title()} {joke_entry['type']} - {joke_entry['timestamp']}"):
                st.markdown(f"**{joke_entry['joke']}**")
                if joke_entry.get('topic'):
                    st.caption(f"Topic: {joke_entry['topic']}")

def main():
    """Main application"""
    st.set_page_config(
        page_title="LangChain Joke Teller",
        page_icon="🎭",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Create layout
    col1, col2 = st.columns([2, 1])
    
    with col2:
        render_sidebar()
    
    with col1:
        render_joke_generator()
        st.divider()
        render_joke_history()
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with LangChain for Week 2 of AI Coding Essentials* 🤖")

if __name__ == "__main__":
    main()