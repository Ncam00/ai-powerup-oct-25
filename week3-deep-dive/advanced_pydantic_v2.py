"""
Week 3 Deep Dive: Advanced Pydantic Models (Pydantic v2)
Exploring field validation, constraints, and real-world patterns
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Union, Literal, Annotated
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
    """Nested model for contact information with validation"""
    email: Annotated[str, Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')]
    phone: Optional[Annotated[str, Field(pattern=r'^\+?[\d\s\-\(\)]+$')]] = None
    linkedin: Optional[Annotated[str, Field(pattern=r'^https://.*linkedin\.com/.*')]] = None
    website: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        """Custom validator for email domain restrictions"""
        forbidden_domains = ['tempmail.org', '10minutemail.com']
        domain = v.split('@')[1].lower()
        if domain in forbidden_domains:
            raise ValueError(f'Email domain {domain} is not allowed')
        return v.lower()


class Skill(BaseModel):
    """Individual skill with validation"""
    name: Annotated[str, Field(min_length=2, max_length=50)]
    level: SkillLevel
    years_experience: Annotated[int, Field(ge=0, le=50)]
    certified: bool = False
    
    @field_validator('name')
    @classmethod
    def validate_skill_name(cls, v: str) -> str:
        """Ensure skill name is properly formatted"""
        return ' '.join(word.capitalize() for word in v.strip().split())


class Project(BaseModel):
    """Project information with complex validation"""
    name: Annotated[str, Field(min_length=3, max_length=100)]
    description: Annotated[str, Field(min_length=10, max_length=1000)]
    technologies: Annotated[List[str], Field(min_length=1, max_length=20)]
    status: Literal["planning", "in-progress", "completed", "on-hold"]
    start_date: date
    end_date: Optional[date] = None
    priority: Priority = Priority.MEDIUM
    budget: Optional[Annotated[float, Field(gt=0)]] = None
    team_size: Annotated[int, Field(ge=1, le=100)]
    
    @field_validator('technologies')
    @classmethod
    def validate_technologies(cls, v: List[str]) -> List[str]:
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
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Ensure end date is after start date"""
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError('End date must be after start date')
        return self


class Experience(BaseModel):
    """Work experience with advanced validation"""
    company: Annotated[str, Field(min_length=2, max_length=100)]
    position: Annotated[str, Field(min_length=2, max_length=100)]
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Annotated[str, Field(min_length=20, max_length=2000)]
    achievements: Annotated[List[str], Field(max_length=10)] = []
    skills_used: Annotated[List[str], Field(max_length=15)] = []
    
    @model_validator(mode='after')
    def validate_employment_period(self):
        """Complex validation across multiple fields"""
        if self.is_current and self.end_date:
            raise ValueError('Current job cannot have an end date')
        
        if not self.is_current and not self.end_date:
            raise ValueError('Non-current job must have an end date')
        
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError('End date must be after start date')
        
        if self.start_date and self.start_date > date.today():
            raise ValueError('Start date cannot be in the future')
        
        return self


class Portfolio(BaseModel):
    """Complete portfolio with comprehensive validation"""
    name: Annotated[str, Field(min_length=2, max_length=100)]
    title: Annotated[str, Field(min_length=5, max_length=200)]
    summary: Annotated[str, Field(min_length=50, max_length=1000)]
    contact: ContactInfo
    skills: Annotated[List[Skill], Field(min_length=3, max_length=30)]
    experience: Annotated[List[Experience], Field(min_length=1, max_length=20)]
    projects: List[Project] = []
    education: Dict[str, Union[str, int]] = {}
    certifications: Annotated[List[str], Field(max_length=20)] = []
    languages: Dict[str, str] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    @field_validator('skills')
    @classmethod
    def validate_skill_diversity(cls, v: List[Skill]) -> List[Skill]:
        """Ensure good mix of skill levels"""
        if not v:
            return v
        
        levels = [skill.level for skill in v]
        unique_levels = set(levels)
        
        if len(unique_levels) < 2:
            raise ValueError('Portfolio should demonstrate diverse skill levels')
        
        return v
    
    @model_validator(mode='after')
    def validate_portfolio_consistency(self):
        """Comprehensive portfolio validation"""
        # Extract all mentioned technologies
        project_techs = set()
        for project in self.projects:
            project_techs.update(tech.lower() for tech in project.technologies)
        
        exp_skills = set()
        for exp in self.experience:
            exp_skills.update(skill.lower() for skill in exp.skills_used)
        
        skill_names = set(skill.name.lower() for skill in self.skills)
        
        # Check if skills mentioned in projects/experience are in skill list
        all_mentioned = project_techs | exp_skills
        missing_skills = all_mentioned - skill_names
        
        if missing_skills and len(missing_skills) > 3:
            print(f"⚠️  Warning: Many skills mentioned in projects/experience are missing from skills list: {list(missing_skills)[:3]}...")
        
        return self

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
        "json_schema_extra": {
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
        print(f"📧 Contact: {portfolio.contact.email}")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    print("\n" + "-" * 50)
    
    # Test 2: Validation errors
    print("\n🧪 Testing validation errors...")
    
    test_cases = [
        ("Invalid email format", {"email": "not-an-email"}),
        ("Future start date", {"start_date": "2030-01-01", "description": "Test job description with enough characters", "is_current": True}),
        ("Empty skill name", {"name": "", "level": "beginner", "years_experience": 1}),
    ]
    
    for test_name, invalid_data in test_cases:
        try:
            if "email" in invalid_data:
                ContactInfo(**invalid_data)
            elif "start_date" in invalid_data:
                Experience(company="Test Co", position="Developer", **invalid_data)
            elif "name" in invalid_data:
                Skill(**invalid_data)
            print(f"❌ {test_name}: Should have failed!")
        except Exception as e:
            print(f"✅ {test_name}: {str(e)[:80]}...")
    
    print("\n📚 Key Advanced Pydantic Features Demonstrated:")
    print("• Field validation with @field_validator decorator")
    print("• Model validation with @model_validator for cross-field checks") 
    print("• Annotated types with Field constraints")
    print("• Pattern validation for strings (regex)")
    print("• Complex nested models with relationships")
    print("• Field constraints (min/max length, numeric ranges)")
    print("• Enum validation and type constraints")
    print("• Custom error messages and validation logic")


if __name__ == "__main__":
    demonstrate_advanced_validation()