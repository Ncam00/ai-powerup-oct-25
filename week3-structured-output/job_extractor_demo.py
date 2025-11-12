"""
Week 3 Structured Output Challenge - Demo Implementation
Demonstrates Pydantic models for reliable data extraction without API dependency
"""

from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
import json


class JobPosting(BaseModel):
    """A robust job posting model for structured output extraction"""

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

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        str_strip_whitespace = True


def simulate_llm_extraction(text: str) -> JobPosting:
    """
    Simulate what an LLM would extract using structured output.
    In a real implementation, this would be:
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    structured_llm = llm.with_structured_output(JobPosting)
    chain = prompt | structured_llm
    return chain.invoke({"text": text})
    """
    
    # For demo purposes, simulate extracted data from the messy text
    if "StartupXYZ" in text:
        return JobPosting(
            title="Full Stack Software Engineer",
            company="StartupXYZ",
            location="Austin, Texas (Remote Friendly)",
            job_type="Full-time",
            summary="Join a fast-growing fintech startup after Series A funding. Work with React, Node.js, and MongoDB in a dynamic startup environment.",
            requirements=[
                "3+ years experience with React and Node.js",
                "MongoDB experience preferred",
                "AWS knowledge helpful",
                "Startup experience a plus"
            ],
            salary_range="$90,000 - $120,000 plus equity"
        )
    elif "Big Tech Corp" in text:
        return JobPosting(
            title="Data Scientist",
            company="Big Tech Corp",
            location="San Francisco, California",
            job_type="Full-time",
            summary="Join AI Research division to build predictive models and drive product decisions with massive datasets.",
            requirements=[
                "PhD in Computer Science, Statistics, Mathematics, or related field",
                "5+ years Python programming experience",
                "Deep ML algorithms and statistical modeling expertise",
                "TensorFlow or PyTorch experience",
                "Strong communication skills",
                "Large-scale data processing experience preferred"
            ],
            salary_range="Competitive base salary plus equity (above market rate)"
        )
    elif "Creative Minds Agency" in text:
        return JobPosting(
            title="Marketing Coordinator",
            company="Creative Minds Agency",
            location="Denver, Colorado (Hybrid)",
            job_type="Part-time",
            summary="Join a boutique marketing agency managing social media and content for local restaurants, tech startups, and non-profits.",
            requirements=[
                "2+ years marketing experience",
                "Social media platform expertise",
                "Good writing skills",
                "Basic design sense",
                "Independent work ability",
                "Available for office work 2 days per week"
            ],
            salary_range="$25-30 per hour"
        )
    else:
        # Default fallback
        return JobPosting(
            title="Unknown Position",
            company="Unknown Company",
            location="Unknown Location",
            summary="Unable to extract complete information from the provided text."
        )


def validate_extraction_quality(job_posting: JobPosting) -> dict:
    """Demonstrate validation and quality checking of extracted data"""
    
    quality_score = 0
    issues = []
    
    # Check required fields are meaningful
    if job_posting.title and job_posting.title != "Unknown Position":
        quality_score += 20
    else:
        issues.append("Title extraction failed")
    
    if job_posting.company and job_posting.company != "Unknown Company":
        quality_score += 20
    else:
        issues.append("Company extraction failed")
    
    if job_posting.location and job_posting.location != "Unknown Location":
        quality_score += 15
    else:
        issues.append("Location extraction failed")
    
    # Check optional fields
    if job_posting.job_type:
        quality_score += 10
    
    if job_posting.salary_range:
        quality_score += 15
    
    if job_posting.requirements and len(job_posting.requirements) > 0:
        quality_score += 20
    else:
        issues.append("No requirements extracted")
    
    return {
        "quality_score": quality_score,
        "max_score": 100,
        "percentage": round((quality_score / 100) * 100, 1),
        "issues": issues,
        "status": "Good" if quality_score >= 80 else "Needs Improvement" if quality_score >= 60 else "Poor"
    }


def demo_structured_output():
    """Main demo function showing structured output capabilities"""
    
    # Sample messy job posting text
    messy_text = """
    Subject: Re: Urgent - Need Full Stack Dev ASAP!!! 

    Hey everyone! 

    So we just lost our lead developer (long story, don't ask lol) and we REALLY need someone to jump in quickly. StartupXYZ is this awesome fintech company that's growing super fast - we just raised our Series A and everything is crazy right now.

    We're based in Austin, Texas but honestly with COVID and everything, most of our team works remotely anyway. The office is nice though if you want to come in - we have a ping pong table and free kombucha on tap (yes really).

    Anyway, we need a Full Stack Software Engineer who can hit the ground running. Here's what we're looking for:

    - Someone with at least 3+ years doing React and Node.js (please don't apply if you just did a bootcamp last month, we need experience)
    - MongoDB experience would be amazing since that's what we use
    - AWS knowledge is super helpful too
    - Bonus points if you've worked at a startup before and understand the chaos

    The salary range is $90,000 to $120,000 depending on experience. We also have equity (could be worth millions someday, who knows!) and good health insurance.
    """
    
    print("Week 3 Structured Output Challenge Demo")
    print("=" * 50)
    print("\n📝 Original Messy Text:")
    print("-" * 30)
    print(messy_text.strip())
    
    print("\n🔧 Extracting Structured Data...")
    print("-" * 30)
    
    # Extract structured data
    try:
        job_posting = simulate_llm_extraction(messy_text)
        
        print("✅ Extraction successful!")
        print(f"\n📊 Structured Job Posting:")
        print(json.dumps(job_posting.model_dump(), indent=2))
        
        # Validate quality
        quality = validate_extraction_quality(job_posting)
        print(f"\n🎯 Extraction Quality Analysis:")
        print(f"Score: {quality['quality_score']}/{quality['max_score']} ({quality['percentage']}%)")
        print(f"Status: {quality['status']}")
        
        if quality['issues']:
            print("Issues found:")
            for issue in quality['issues']:
                print(f"  - {issue}")
        
        # Demonstrate Pydantic validation
        print(f"\n✨ Pydantic Benefits Demonstrated:")
        print("- Type safety: All fields are properly typed")
        print("- Validation: Data is automatically validated on creation")
        print("- Serialization: Easy JSON export with model_dump()")
        print("- Documentation: Field descriptions provide context")
        
    except ValidationError as e:
        print(f"❌ Validation Error: {e}")
    except Exception as e:
        print(f"❌ Extraction Error: {e}")


if __name__ == "__main__":
    demo_structured_output()