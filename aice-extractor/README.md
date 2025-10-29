# Job Posting Extractor Challenge

Build a structured output extractor that transforms messy job posting text into clean, validated Python objects using Pydantic and LangChain.

## What You'll Build

By the end of this challenge, you'll have created an AI system that can:
- Take messy, real-world job posting text
- Extract key information using structured output
- Return validated Python objects with clean data
- Handle various text formats and missing information

## Prerequisites

- Basic Python knowledge
- Understanding of Pydantic models
- Google AI API key (get one from [Google AI Studio](https://aistudio.google.com/))

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Create a `.env` file with your Google AI API key:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Test with sample data:
```bash
python main.py
```

## Phase 1: Create the Pydantic Model (Step-by-Step)

First, let's create a Pydantic model to define our data structure.

### Step 1.1: Add Imports to `job_models.py`

Replace the TODO comment with these imports:

```python
from pydantic import BaseModel, Field
from typing import Optional, List
```

### Step 1.2: Create the JobPosting Class

Add this class definition:

```python
class JobPosting(BaseModel):
    """A simple job posting model for structured output extraction"""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    job_type: Optional[str] = Field(
        None,
        description="Employment type (full-time, part-time, contract, etc.)",
    )
    summary: str = Field(..., description="Brief summary of the job")
    requirements: List[str] = Field(
        default_factory=list, description="Key job requirements"
    )
    salary_range: Optional[str] = Field(
        None, description="Salary range if mentioned"
    )
```

### Step 1.3: Test Your Model

Create a simple test to verify your model works:

```python
# Test in Python interpreter
from job_models import JobPosting
job = JobPosting(
    title="Software Engineer",
    company="TechCorp",
    location="San Francisco, CA",
    summary="Build cool stuff"
)
print(job.model_dump())
```

## Phase 2: Create the Extraction Function (Guided)

Now let's implement the extraction logic in `job_extractor.py`.

### Step 2.1: Add Imports

Replace the first TODO with these imports:

```python
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from job_models import JobPosting
```

### Step 2.2: Load Environment Variables

Replace the second TODO with:

```python
load_dotenv()
```

### Step 2.3: Create the Basic Function Structure

Replace the third TODO with this function skeleton:

```python
def extract_job_posting(text: str) -> JobPosting:
    """Extract job posting information from text using structured output"""
    
    # TODO: Initialize the LLM
    # TODO: Create structured LLM
    # TODO: Create prompt template
    # TODO: Build and invoke chain
    
    pass
```

### Step 2.4: Initialize the LLM

Replace the first inner TODO with:

```python
# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-04-17", temperature=0
)
```

### Step 2.5: Create Structured LLM

Replace the second inner TODO with:

```python
# Create structured LLM
structured_llm = llm.with_structured_output(JobPosting)
```

### Step 2.6: Create Prompt Template

Replace the third inner TODO with:

```python
# Create prompt
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
```

### Step 2.7: Build and Invoke Chain

Replace the fourth inner TODO and the `pass` statement with:

```python
# Create chain and extract
chain = prompt | structured_llm
result = chain.invoke({"text": text})

return result
```

### Step 2.8: Test Your Function

Test with a simple example:

```python
# Test in Python interpreter
from job_extractor import extract_job_posting
text = "Software Engineer at TechCorp in SF. Full-time, $100k."
result = extract_job_posting(text)
print(result.model_dump())
```

## Phase 3: Test with Real Data (Independent)

Now test your implementation with the messy sample data.

### Step 3.1: Run the Main Script

```bash
python main.py
```

You should see structured output extracted from three different job posting styles.

### Step 3.2: Analyze the Results

Look at how the AI handles:
- **Casual email format** (Sample 1) - Informal language, scattered information
- **Professional email** (Sample 2) - Formal but wordy, buried requirements  
- **Social media style** (Sample 3) - Emojis, bullet points, casual tone

## Phase 4: Experiment and Improve (Challenge)

### Your Tasks

1. **Test Edge Cases**: Try your extractor with incomplete or unusual job postings
2. **Improve the Prompt**: Experiment with different prompt wording to get better results
3. **Add Validation**: Handle cases where required fields might be missing
4. **Extend the Model**: Add new fields like `benefits`, `experience_level`, or `remote_friendly`

### Advanced Challenges

1. **Error Handling**: Add try/catch blocks and handle API errors gracefully
2. **Multiple Jobs**: Extract multiple jobs from a single text (hint: use `List[JobPosting]`)
3. **Confidence Scoring**: Add a confidence field to indicate extraction quality
4. **Custom Validators**: Use Pydantic validators to clean and normalize data

## Success Criteria

Your implementation is successful when:

- ✅ The Pydantic model validates data correctly
- ✅ The extractor handles all three sample formats
- ✅ Required fields are properly extracted
- ✅ Optional fields work correctly (job_type, salary_range)
- ✅ Lists are populated with relevant items (requirements)
- ✅ The output is clean and usable

## Key Learning Points

1. **Structured Output** - Transform unstructured text into validated data structures
2. **Pydantic Models** - Create robust schemas with automatic validation
3. **LangChain Integration** - Use `with_structured_output()` for reliable extraction
4. **Prompt Engineering** - Design prompts that guide AI to extract the right information
5. **Real-world Application** - Handle messy, inconsistent text like you'd find online

## Example Expected Output

```json
{
  "title": "Full Stack Software Engineer",
  "company": "StartupXYZ",
  "location": "Austin, Texas",
  "job_type": "full-time",
  "summary": "Join our growing fintech team building scalable applications",
  "requirements": [
    "3+ years React and Node.js experience",
    "MongoDB experience", 
    "AWS knowledge helpful",
    "Startup experience preferred"
  ],
  "salary_range": "$90,000 to $120,000"
}
```

## Common Issues and Solutions

### Issue: Import errors
- Ensure all dependencies are installed with `uv sync`
- Check that your `.env` file contains a valid API key
- Verify file names and import paths

### Issue: Model validation errors
- Check that required fields are marked with `...`
- Ensure optional fields use `Optional[]` typing
- Verify Field descriptions are helpful for the AI

### Issue: Poor extraction quality
- Improve your prompt with more specific instructions
- Add examples in your prompt template
- Experiment with different model parameters

### Issue: API errors
- Verify your Google API key is correct and active
- Check your internet connection
- Add error handling with try/catch blocks

## Need Help?

- Review the sample_data.py to understand input formats
- Test individual components before combining them
- Use print statements to debug the extraction process
- Check the LangChain documentation for `with_structured_output()`

Good luck building your structured output extractor! 🚀📊