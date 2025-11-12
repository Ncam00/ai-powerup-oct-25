"""
TODO: Create a job extractor using structured output

Instructions:
1. Import necessary modules (dotenv, ChatGoogleGenerativeAI, ChatPromptTemplate)
2. Import your JobPosting model
3. Create extract_job_posting function that:
   - Initializes the LLM
   - Creates structured LLM with with_structured_output()
   - Creates a prompt template
   - Builds and invokes the chain

See README.md for detailed step-by-step instructions.
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from job_models import JobPosting

load_dotenv()


def extract_job_posting(text: str) -> JobPosting:
    """Extract job posting information from text using structured output"""
    
    # Initialize the LLM - using Google Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp", 
        temperature=0
    )
    
    # Create structured LLM - this is the magic!
    structured_llm = llm.with_structured_output(JobPosting)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(
        """
Extract job posting information from the following text.

Focus on identifying:
- Job title
- Company name
- Location
- Employment type (full-time, part-time, contract, etc.)
- Brief summary of the role
- Key requirements
- Salary range if mentioned

Text to analyze:
{text}
"""
    )
    
    # Create chain and extract
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    
    return result
