"""
Week 3 Deep Dive: Advanced Pydantic Models
Exploring custom validators, complex types, and real-world patterns
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Union, Literal
from datetime import datetime, date
from enum import Enum
import re


class SkillLevel(str, Enum):
    """Enum for skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ContactInfo(BaseModel):
    """Nested model for contact information"""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    linkedin: Optional[str] = Field(None, pattern=r'^https://.*linkedin\.com/.*')
    website: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Custom validator for email domain restrictions"""
        forbidden_domains = ['tempmail.org', '10minutemail.com']
        domain = v.split('@')[1].lower()
        if domain in forbidden_domains:
            raise ValueError(f'Email domain {domain} is not allowed')
        return v.lower()


class Skill(BaseModel):
    """Individual skill with validation"""
    name: str = Field(..., min_length=2, max_length=50)
    level: SkillLevel
    years_experience: int = Field(..., ge=0, le=50)
    certified: bool = False
    
    @validator('name')
    def validate_skill_name(cls, v):
        """Ensure skill name is properly formatted"""
        return ' '.join(word.capitalize() for word in v.strip().split())


class Project(BaseModel):
    """Project information with complex validation"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    technologies: List[str] = Field(..., min_items=1, max_items=20)
    status: Literal["planning", "in-progress", "completed", "on-hold"]
    start_date: date
    end_date: Optional[date] = None
    priority: Priority = Priority.MEDIUM
    budget: Optional[float] = Field(None, gt=0)
    team_size: int = Field(..., ge=1, le=100)
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Ensure end date is after start date"""
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('technologies')
    def validate_technologies(cls, v):
        """Normalize and validate technology names"""
        if not v:
            raise ValueError('At least one technology is required')
        
        # Normalize technology names
        normalized = []
        for tech in v:
            tech = tech.strip().lower()
            if len(tech) < 2:
                raise ValueError(f'Technology name "{tech}" is too short')
            normalized.append(tech.capitalize())
        
        return list(set(normalized))  # Remove duplicates


class Experience(BaseModel):
    """Work experience with advanced validation"""
    company: str = Field(..., min_length=2, max_length=100)
    position: str = Field(..., min_length=2, max_length=100)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: str = Field(..., min_length=20, max_length=2000)
    achievements: List[str] = Field(default_factory=list, max_items=10)
    skills_used: List[str] = Field(default_factory=list, max_items=15)
    
    @root_validator
    def validate_employment_period(cls, values):
        """Complex validation across multiple fields"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        is_current = values.get('is_current', False)
        
        if is_current and end_date:
            raise ValueError('Current job cannot have an end date')
        
        if not is_current and not end_date:
            raise ValueError('Non-current job must have an end date')
        
        if end_date and start_date and end_date < start_date:
            raise ValueError('End date must be after start date')
        
        if start_date and start_date > date.today():
            raise ValueError('Start date cannot be in the future')
        
        return values


class Portfolio(BaseModel):
    """Complete portfolio with comprehensive validation"""
    name: str = Field(..., min_length=2, max_length=100)
    title: str = Field(..., min_length=5, max_length=200)
    summary: str = Field(..., min_length=50, max_length=1000)
    contact: ContactInfo
    skills: List[Skill] = Field(..., min_items=3, max_items=30)
    experience: List[Experience] = Field(..., min_items=1, max_items=20)
    projects: List[Project] = Field(default_factory=list, max_items=15)
    education: Dict[str, Union[str, int]] = Field(default_factory=dict)
    certifications: List[str] = Field(default_factory=list, max_items=20)
    languages: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    @validator('skills')
    def validate_skill_diversity(cls, v):
        """Ensure good mix of skill levels"""
        if not v:
            return v
        
        levels = [skill.level for skill in v]
        unique_levels = set(levels)
        
        if len(unique_levels) < 2:
            raise ValueError('Portfolio should demonstrate diverse skill levels')
        
        return v
    
    @validator('experience')
    def validate_experience_progression(cls, v):
        """Check for logical career progression"""
        if len(v) <= 1:
            return v
        
        # Sort by start date
        sorted_exp = sorted(v, key=lambda x: x.start_date)
        
        # Check for gaps longer than 2 years
        for i in range(1, len(sorted_exp)):
            prev_end = sorted_exp[i-1].end_date
            curr_start = sorted_exp[i].start_date
            
            if prev_end and (curr_start - prev_end).days > 730:  # 2 years
                raise ValueError(f'Gap of more than 2 years between {sorted_exp[i-1].company} and {sorted_exp[i].company}')
        
        return v
    
    @root_validator
    def validate_portfolio_consistency(cls, values):
        """Comprehensive portfolio validation"""
        skills = values.get('skills', [])
        projects = values.get('projects', [])
        experience = values.get('experience', [])
        
        # Extract all mentioned technologies
        project_techs = set()
        for project in projects:
            project_techs.update(tech.lower() for tech in project.technologies)
        
        exp_skills = set()
        for exp in experience:
            exp_skills.update(skill.lower() for skill in exp.skills_used)
        
        skill_names = set(skill.name.lower() for skill in skills)
        
        # Check if skills mentioned in projects/experience are in skill list
        all_mentioned = project_techs | exp_skills
        missing_skills = all_mentioned - skill_names
        
        if missing_skills and len(missing_skills) > 3:
            raise ValueError(f'Many skills mentioned in projects/experience are missing from skills list: {list(missing_skills)[:3]}...')
        
        return values

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        extra = "forbid"
        schema_extra = {
            "example": {
                "name": "Jane Developer",
                "title": "Senior Full-Stack Developer & AI Enthusiast",
                "summary": "Passionate developer with 5+ years of experience building scalable web applications and AI-powered solutions.",
                "contact": {
                    "email": "jane@example.com",
                    "phone": "+1-555-0123",
                    "linkedin": "https://linkedin.com/in/jane-developer"
                },
                "skills": [
                    {
                        "name": "Python",
                        "level": "advanced",
                        "years_experience": 5,
                        "certified": True
                    }
                ]
            }
        }


def demonstrate_advanced_validation():
    """Demonstrate advanced Pydantic validation features"""
    
    print("🔬 Advanced Pydantic Validation Demo")
    print("=" * 50)
    
    # Test 1: Valid portfolio
    try:
        portfolio_data = {
            "name": "Alex Thompson",
            "title": "Senior AI Engineer & Full-Stack Developer",
            "summary": "Experienced engineer specializing in AI applications and scalable web systems with proven track record in production environments.",
            "contact": {
                "email": "alex.thompson@example.com",
                "phone": "+1-555-0199",
                "linkedin": "https://linkedin.com/in/alex-thompson"
            },
            "skills": [
                {"name": "python", "level": "advanced", "years_experience": 6, "certified": True},
                {"name": "javascript", "level": "intermediate", "years_experience": 4, "certified": False},
                {"name": "machine learning", "level": "advanced", "years_experience": 3, "certified": True},
                {"name": "react", "level": "beginner", "years_experience": 1, "certified": False}
            ],
            "experience": [
                {
                    "company": "Tech Startup Inc",
                    "position": "Senior AI Engineer",
                    "start_date": "2022-01-15",
                    "is_current": True,
                    "description": "Leading AI initiatives and building machine learning pipelines for production systems.",
                    "achievements": ["Increased model accuracy by 25%", "Reduced inference time by 40%"],
                    "skills_used": ["Python", "Machine Learning", "AWS"]
                },
                {
                    "company": "Web Solutions Co",
                    "position": "Full Stack Developer",
                    "start_date": "2020-03-01",
                    "end_date": "2021-12-31",
                    "is_current": False,
                    "description": "Developed and maintained web applications using modern frameworks.",
                    "achievements": ["Built 5 successful web applications"],
                    "skills_used": ["JavaScript", "React", "Node.js"]
                }
            ],
            "projects": [
                {
                    "name": "AI-Powered Chatbot",
                    "description": "Built an intelligent customer service chatbot using natural language processing.",
                    "technologies": ["python", "langchain", "openai", "streamlit"],
                    "status": "completed",
                    "start_date": "2023-06-01",
                    "end_date": "2023-08-15",
                    "priority": "high",
                    "team_size": 3
                }
            ]
        }
        
        portfolio = Portfolio(**portfolio_data)
        print("✅ Valid portfolio created successfully!")
        print(f"📊 Portfolio for: {portfolio.name}")
        print(f"🎯 Skills: {len(portfolio.skills)} skills across {len(set(s.level for s in portfolio.skills))} levels")
        print(f"💼 Experience: {len(portfolio.experience)} positions")
        print(f"🚀 Projects: {len(portfolio.projects)} projects")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    print("\n" + "-" * 50)
    
    # Test 2: Invalid data to show validation
    print("\n🧪 Testing validation errors...")
    
    invalid_cases = [
        {
            "name": "Testing invalid email",
            "data": {"contact": {"email": "invalid-email"}},
            "error_type": "Email format validation"
        },
        {
            "name": "Testing future start date",
            "data": {"experience": [{"start_date": "2030-01-01"}]},
            "error_type": "Date validation"
        },
        {
            "name": "Testing skill level diversity",
            "data": {"skills": [
                {"name": "Python", "level": "beginner", "years_experience": 1},
                {"name": "JavaScript", "level": "beginner", "years_experience": 1}
            ]},
            "error_type": "Skill diversity validation"
        }
    ]
    
    for case in invalid_cases:
        try:
            # This should fail
            Portfolio(**case["data"])
        except Exception as e:
            print(f"✅ {case['error_type']}: {str(e)[:100]}...")
    
    print("\n📚 Key Advanced Pydantic Features Demonstrated:")
    print("• Custom validators with @validator decorator")
    print("• Root validators for cross-field validation") 
    print("• Enum constraints and type validation")
    print("• Regex patterns for string validation")
    print("• Complex nested models with relationships")
    print("• Field constraints (min/max length, ranges)")
    print("• Custom error messages and validation logic")
    print("• Configuration options and schema generation")


if __name__ == "__main__":
    demonstrate_advanced_validation()