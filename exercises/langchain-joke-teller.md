# Optional Exercise: Build a LangChain Joke Teller

In this exercise, you'll create a simple Python application that uses LangChain to generate jokes based on user input. This is a fun way to get started with LangChain while building something that actually works.

## Learning Objectives

By completing this exercise, you will:
- Set up a new Python project from scratch using best practices
- Learn how to use LangChain with an LLM to generate content
- Build a simple CLI or web application that responds to user input
- Practice proper project structure and dependency management

## Project Setup

Follow these steps to create a new Python project from scratch:

### 1. Create Project Directory and Initialize Git

```bash
# Create project directory
mkdir langchain-joke-teller
cd langchain-joke-teller

# Initialize git repository
git init
```

### 2. Set Up Virtual Environment with UV

[UV](https://github.com/astral-sh/uv) is a fast, reliable Python package installer and resolver. It's a modern alternative to pip.

```bash
# Install UV if you don't have it already
pip install uv

# Create a virtual environment
uv venv

# Activate the virtual environment
# On Windows:
# .venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Create Project Structure

Keep it simple with just the essential files:

```bash
# Create the basic files
touch main.py .env .gitignore README.md

# Generate pyproject.toml using uv
uv init
```

### 4. Set Up .gitignore

Create a `.gitignore` file with the following content:

```
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/

# Environment variables
.env

# IDE specific files
.idea/
.vscode/
```

### 5. Edit the pyproject.toml

After running `uv init`, update the generated pyproject.toml with your dependencies:

```bash
# Edit pyproject.toml (using your preferred editor)
# Add these dependencies under [project.dependencies]:
# - langchain
# - langchain-google-genai
# - python-dotenv
# - streamlit (only needed if you do the Streamlit extension)
```

Your pyproject.toml should look something like this:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "langchain-joke-teller"
version = "0.1.0"
description = "A simple joke teller built with LangChain"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "langchain",
    "langchain-google-genai",
    "python-dotenv",
]

# Important: Add this section to fix package build issues
[tool.hatch.build.targets.wheel]
packages = ["."]
```

### 6. Create .env File

Create a `.env` file for your API keys:

```
GOOGLE_API_KEY=your_google_api_key_here
# Add other API keys as needed
```

You can get a Google AI API key for free from [Google AI Studio](https://ai.google.dev/):

1. Visit [ai.google.dev](https://ai.google.dev/) and sign in with your Google account
2. Click on "Get API key" in the top right corner
3. Create a new API key or use an existing one
4. Copy the API key and add it to your .env file

**Note:** Make sure there are no spaces around the equals sign in your .env file. The key should look exactly like:
```
GOOGLE_API_KEY=abcdef123456789
```

**Important:** The Google API may take a few minutes to activate after you first create your key. If you get authentication errors, wait a few minutes and try again.

## Building the Joke Teller

Now you'll build a simple command-line joke teller application using LangChain and the Google Gemini model.

### Implementation Tips

Follow these steps to create your joke teller in `main.py`:

1. **Import the necessary modules**:
   - `os` - for environment variables
   - `sys` - for command line arguments
   - `dotenv` - for loading environment variables
   - `langchain_google_genai` - for the Gemini model
   - `langchain.prompts` - for creating prompt templates
   - `langchain_core.output_parsers` - for parsing model output

2. **Load the .env file**:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. **Create a function that builds a LangChain chain**:
   - Initialize a `ChatGoogleGenerativeAI` model
   - Create a prompt template that asks for a joke about a specific topic
   - Use LCEL (LangChain Expression Language) to chain the prompt with the model
   - Return the chain

4. **Create a main function that**:
   - Checks that the `GOOGLE_API_KEY` environment variable is set
   - Gets a topic from command line arguments or user input
   - Uses the chain to generate a joke about the topic
   - Prints the joke to the console with some nice formatting
   - Handles any errors gracefully

5. **Don't forget the Python script entry point**:
   ```python
   if __name__ == "__main__":
       main()
   ```

### Hints and Code Snippets

Here are some helpful code snippets to guide you:

**Initializing the language model**:
```python
# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-04-17",
    temperature=0.7,  # Adding some creativity
)
```

**Creating a prompt template**:
```python
# Create a prompt template
prompt = ChatPromptTemplate.from_template(
    """You are a comedian specialized in generating jokes.

    Create a funny joke about the following topic: {topic}

    Make sure the joke is appropriate for all audiences.
    """
)
```

**Building a chain with LCEL**:
```python
# Create a chain
chain = prompt | llm | StrOutputParser()
```

**Getting user input**:
```python
# Get topic from command line arguments or prompt user
if len(sys.argv) > 1:
    topic = sys.argv[1]
else:
    topic = input("Enter a topic for your joke: ")
```

**Using the chain**:
```python
# Get response from the chain
joke = chain.invoke({"topic": topic})
```

### Install Dependencies and Run

```bash
# Install dependencies from pyproject.toml
uv pip install .

# To run the CLI version:
python main.py "programming"
```

## LangChain Tips

Here are some key LangChain concepts used in this exercise:

1. **LangChain Expression Language (LCEL)**: The pipe syntax (`|`) for creating chains is part of LCEL, which provides a concise way to connect components.

2. **ChatPromptTemplate**: Used to create structured prompts for your LLM. You can define variables using curly braces `{variable_name}`.

3. **ChatOpenAI**: The interface to the OpenAI model API. You can control parameters like `temperature` to adjust the creativity of responses.

4. **StrOutputParser**: Converts the structured LLM response into a simple string.

5. **Invocation**: Use the `.invoke()` method to run your chain with inputs.

## Extensions and Challenges

Once you have the basic joke teller working, try these extensions:

1. **Add a Streamlit interface**: Create a web UI using Streamlit that lets users enter topics through a text input field

2. **Add categories**: Let users select joke categories (puns, dad jokes, knock-knock, etc.)

3. **Custom formatting**: Parse the output to format multi-line jokes properly

4. **Memory**: Add conversation memory so the app remembers previous jokes

5. **Multiple LLMs**: Try different models and compare their humor styles

6. **Voice output**: Add text-to-speech to deliver the jokes audibly

## Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [UV Documentation](https://github.com/astral-sh/uv)
