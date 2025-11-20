"""
Concept Search Tool (RAG)
==========================

Week 4: RAG implementation for Python documentation
"""

from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
from pathlib import Path

from api.models.config import settings

logger = logging.getLogger(__name__)

# Initialize embeddings and vector store
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

# For demo purposes - in production, load pre-built vector store
# vector_store = Chroma(
#     persist_directory=settings.VECTOR_STORE_PATH,
#     embedding_function=embeddings
# )

@tool
def search_concepts(query: str, max_results: int = 3) -> str:
    """
    Search Python documentation and concepts.
    
    Use this when student asks about Python concepts, syntax, or built-in features.
    Returns relevant documentation excerpts and code examples.
    
    Args:
        query: What to search for (e.g., "list comprehension", "decorators")
        max_results: Maximum number of results to return (default: 3)
    
    Returns:
        Relevant documentation and examples
    
    Examples:
        >>> search_concepts("how do list comprehensions work")
        "List Comprehensions provide a concise way to create lists...
        
        Example:
        squares = [x**2 for x in range(10)]"
    """
    
    logger.info(f"Searching concepts for: {query}")
    
    # For demo - return mock documentation
    # In production, use vector store retrieval
    
    concept_database = {
        "list comprehension": """
**List Comprehensions**

A concise way to create lists based on existing sequences.

Syntax:
```python
new_list = [expression for item in iterable if condition]
```

Examples:
```python
# Square numbers
squares = [x**2 for x in range(10)]

# Filter even numbers
evens = [x for x in range(20) if x % 2 == 0]

# Nested comprehension
matrix = [[i*j for j in range(3)] for i in range(3)]
```

Benefits:
- More readable than loops for simple operations
- Often faster than equivalent for loops
- More Pythonic
        """,
        
        "decorator": """
**Decorators**

Functions that modify the behavior of other functions.

Syntax:
```python
@decorator
def function():
    pass
```

Example:
```python
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end-start:.2f}s")
        return result
    return wrapper

@timing_decorator
def slow_function():
    time.sleep(1)
```

Common uses:
- Logging
- Access control
- Caching
- Input validation
        """,
        
        "class": """
**Classes and Object-Oriented Programming**

Classes are blueprints for creating objects.

Syntax:
```python
class MyClass:
    def __init__(self, value):
        self.value = value
    
    def method(self):
        return self.value * 2
```

Example:
```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def bark(self):
        return f"{self.name} says woof!"

my_dog = Dog("Buddy", 3)
print(my_dog.bark())  # "Buddy says woof!"
```

Key concepts:
- Encapsulation
- Inheritance
- Polymorphism
        """
    }
    
    # Simple keyword matching for demo
    query_lower = query.lower()
    
    results = []
    for concept, content in concept_database.items():
        if concept in query_lower or query_lower in concept:
            results.append(content)
    
    if results:
        return "\n\n---\n\n".join(results[:max_results])
    
    # Default response if no match
    return f"""
I don't have specific documentation for "{query}" in my knowledge base.

However, I can help you understand this concept! Let me explain it step by step.

Would you like me to:
1. Provide a detailed explanation
2. Show code examples
3. Create practice exercises
    """

def build_knowledge_base(docs_path: str):
    """
    Build vector store from Python documentation.
    
    This would be run once to index documentation.
    """
    
    # Load documents
    docs = []
    # ... load Python docs, tutorials, etc.
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(docs)
    
    # Create vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.VECTOR_STORE_PATH
    )
    
    vector_store.persist()
    logger.info(f"Knowledge base built: {len(chunks)} chunks indexed")
