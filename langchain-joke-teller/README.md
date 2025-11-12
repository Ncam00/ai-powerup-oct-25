# 🎭 LangChain Joke Teller

A specialized AI comedian built with LangChain that generates jokes in different styles and formats. This project demonstrates advanced LangChain concepts including prompt engineering, specialized AI personas, and interactive UI components.

## 🌟 Features

### Joke Types
- **🎯 One-liners** - Quick, punchy single-sentence jokes
- **❓ Setup & Punchline** - Classic joke format with setup and punchline
- **📖 Short Stories** - Brief humorous narratives with funny endings
- **🧩 Riddles** - Question-and-answer style humor

### Humor Styles
- **👨 Dad Jokes** - Wonderfully cheesy and punny
- **🧠 Witty & Clever** - Sophisticated wordplay and observations
- **👪 Family-Friendly** - Clean humor for all ages
- **🤓 Geeky & Nerdy** - Tech, science, and academic humor
- **👁️ Observational** - Everyday life and common experiences

### Advanced Features
- **Custom Topics** - Generate jokes about specific subjects
- **Custom Prompts** - Write your own joke requests
- **Joke History** - Track all generated jokes
- **Favorites System** - Save your best jokes
- **Quick Joke Buttons** - One-click jokes by category
- **Export Functionality** - Download jokes as text files

## 🚀 Getting Started

### Installation
```bash
cd langchain-joke-teller
pip install -r requirements.txt
```

### Setup
1. Copy `.env.example` to `.env`
2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   ```

### Run the Application
```bash
streamlit run app.py
```

## 🎯 How It Works

### LangChain Components Used

1. **ChatPromptTemplate** - Creates specialized prompts for different joke styles
2. **ChatOpenAI** - LLM configured for creative humor generation
3. **StrOutputParser** - Parses and cleans the joke responses
4. **Chain Composition** - Combines prompt, LLM, and parser into efficient chains

### Prompt Engineering Techniques

The app demonstrates advanced prompt engineering:

```python
def create_joke_prompt(joke_type, style, topic=None):
    style_instructions = {
        "dad": "Create dad jokes that are wonderfully cheesy, punny...",
        "witty": "Create clever, sophisticated humor with wordplay...",
        # ... more styles
    }
    
    joke_type_instructions = {
        "one_liner": "Create a single-sentence joke...",
        "setup_punchline": "Create a classic setup-and-punchline...",
        # ... more types
    }
```

### Key Features Implementation

- **Dynamic Prompt Generation** - Prompts adapt based on user selections
- **Session State Management** - Persistent joke history and favorites
- **Interactive UI Components** - Quick actions and export functionality
- **Error Handling** - Graceful handling of API errors

## 📚 Learning Outcomes

This project demonstrates:

- **Specialized AI Personas** - How to create AI with specific personality traits
- **Dynamic Prompt Engineering** - Adapting prompts based on user input
- **LangChain Chain Composition** - Building efficient processing pipelines
- **State Management** - Persistent data across Streamlit sessions
- **Interactive UI Design** - Creating engaging user experiences

## 🎨 Example Usage

### Generate a Dad Joke about Programming
```python
joke = generate_joke(
    joke_type="setup_punchline",
    style="dad", 
    topic="programming"
)
# Output: "Why do programmers prefer dark mode? Because light attracts bugs!"
```

### Custom Joke Request
```python
custom_prompt = "Tell me a witty joke about a robot learning to cook"
joke = generate_joke(custom_prompt=custom_prompt)
```

## 🔧 Technical Details

- **Framework**: Streamlit for the web interface
- **LLM**: OpenAI GPT-3.5-turbo with high creativity (temperature=0.9)
- **Prompt Templates**: Dynamic generation based on style and type
- **State Management**: Session-based joke history and favorites
- **UI Components**: Interactive buttons, expandable sections, download functionality

## 🚀 Future Enhancements

- **Joke Rating System** - Let users rate jokes for quality feedback
- **Social Sharing** - Share jokes on social media
- **Joke Categories** - More specific joke categories (work, relationships, etc.)
- **Multilingual Support** - Jokes in different languages
- **Voice Output** - Text-to-speech for joke delivery
- **Joke Competitions** - Compare jokes from different styles

## 📖 Week 2 Learning Objectives

This project fulfills Week 2 learning objectives:

- ✅ **LangChain Advanced Patterns** - Specialized prompts and chains
- ✅ **Prompt Engineering** - Dynamic prompt generation for humor
- ✅ **Interactive Applications** - Rich Streamlit UI with state management
- ✅ **AI Personas** - Different humor styles and personalities
- ✅ **Chain Composition** - Efficient LangChain processing pipelines

---

*Part of Week 2: Building with LLMs - AI Coding Essentials*