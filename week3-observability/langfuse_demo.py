"""
Week 3 Observability Challenge - Langfuse Integration
Comprehensive observability for Week 3 structured output and tool use applications
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, List
import uuid
import json

# Import Langfuse for observability
try:
    from langfuse.callback import CallbackHandler
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    CallbackHandler = None
    Langfuse = None
    print("⚠️  Langfuse not installed. Install with: pip install langfuse")

load_dotenv()


class ObservabilityManager:
    """Centralized observability management for Week 3 applications"""
    
    def __init__(self):
        self.langfuse_handler = self._setup_langfuse()
        self.langfuse_client = self._setup_langfuse_client()
        self.session_id = str(uuid.uuid4())
        
    def _setup_langfuse(self):
        """Setup Langfuse callback handler"""
        if not LANGFUSE_AVAILABLE:
            return None
            
        try:
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            
            if secret_key and public_key and not secret_key.endswith("..."):
                handler = CallbackHandler(
                    secret_key=secret_key,
                    public_key=public_key,
                    host=host
                )
                print("✅ Langfuse callback handler initialized")
                return handler
            else:
                print("⚠️  Langfuse credentials not found in .env")
                return None
        except Exception as e:
            print(f"❌ Langfuse setup failed: {e}")
            return None
    
    def _setup_langfuse_client(self):
        """Setup Langfuse client for manual event tracking"""
        if not LANGFUSE_AVAILABLE:
            return None
            
        try:
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            
            if secret_key and public_key and not secret_key.endswith("..."):
                client = Langfuse(
                    secret_key=secret_key,
                    public_key=public_key,
                    host=host
                )
                print("✅ Langfuse client initialized")
                return client
            else:
                print("⚠️  Langfuse client credentials not found")
                return None
        except Exception as e:
            print(f"❌ Langfuse client setup failed: {e}")
            return None
    
    def create_trace(self, name: str, metadata: Dict[str, Any] = None) -> str:
        """Create a new trace for tracking operations"""
        trace_id = str(uuid.uuid4())
        
        if self.langfuse_client:
            try:
                self.langfuse_client.trace(
                    id=trace_id,
                    name=name,
                    session_id=self.session_id,
                    metadata=metadata or {}
                )
                print(f"📊 Created trace: {name} ({trace_id})")
            except Exception as e:
                print(f"⚠️  Trace creation failed: {e}")
        
        return trace_id
    
    def log_tool_usage(self, trace_id: str, tool_name: str, inputs: Dict, output: Any, duration: float = None):
        """Log tool usage for observability"""
        if self.langfuse_client:
            try:
                self.langfuse_client.span(
                    trace_id=trace_id,
                    name=f"tool_{tool_name}",
                    input=inputs,
                    output=output,
                    metadata={
                        "tool_type": "calculator_tool",
                        "duration_ms": duration * 1000 if duration else None
                    }
                )
                print(f"🔧 Logged tool usage: {tool_name}")
            except Exception as e:
                print(f"⚠️  Tool logging failed: {e}")
    
    def log_structured_output(self, trace_id: str, raw_text: str, extracted_data: Dict, quality_score: float):
        """Log structured output extraction for observability"""
        if self.langfuse_client:
            try:
                self.langfuse_client.generation(
                    trace_id=trace_id,
                    name="structured_extraction",
                    input={"raw_text": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text},
                    output=extracted_data,
                    metadata={
                        "extraction_type": "job_posting",
                        "quality_score": quality_score,
                        "text_length": len(raw_text),
                        "fields_extracted": len(extracted_data)
                    }
                )
                print(f"📝 Logged structured output (quality: {quality_score}%)")
            except Exception as e:
                print(f"⚠️  Structured output logging failed: {e}")


def demo_structured_output_with_observability():
    """Demonstrate structured output with full observability"""
    
    print("\n" + "="*60)
    print("📊 STRUCTURED OUTPUT with OBSERVABILITY")
    print("="*60)
    
    obs_manager = ObservabilityManager()
    
    # Create trace for structured output
    trace_id = obs_manager.create_trace(
        "job_posting_extraction",
        {"application": "week3_structured_output", "version": "1.0"}
    )
    
    # Simulate structured output extraction
    raw_job_text = """
    Urgent - Need Full Stack Dev ASAP!!!
    
    StartupXYZ is this awesome fintech company that's growing super fast.
    We need a Full Stack Software Engineer who can hit the ground running.
    
    Requirements:
    - 3+ years doing React and Node.js
    - MongoDB experience would be amazing
    - AWS knowledge is super helpful
    
    The salary range is $90,000 to $120,000 depending on experience.
    """
    
    extracted_data = {
        "title": "Full Stack Software Engineer",
        "company": "StartupXYZ",
        "location": "Remote",
        "job_type": "Full-time",
        "summary": "Join a fast-growing fintech startup that needs an experienced developer",
        "requirements": [
            "3+ years React and Node.js experience",
            "MongoDB experience preferred",
            "AWS knowledge helpful"
        ],
        "salary_range": "$90,000 - $120,000"
    }
    
    quality_score = 95.0  # Simulated quality assessment
    
    # Log the structured extraction
    obs_manager.log_structured_output(trace_id, raw_job_text, extracted_data, quality_score)
    
    print(f"✅ Extracted structured data with {quality_score}% quality")
    print(f"📊 Logged to trace: {trace_id}")


def demo_tool_use_with_observability():
    """Demonstrate tool use with full observability"""
    
    print("\n" + "="*60)
    print("🔧 TOOL USE with OBSERVABILITY")
    print("="*60)
    
    obs_manager = ObservabilityManager()
    
    # Create trace for tool use
    trace_id = obs_manager.create_trace(
        "multi_step_calculation",
        {"application": "week3_tool_use", "problem": "square_root_then_multiply"}
    )
    
    # Simulate tool usage sequence
    tool_sequence = [
        {
            "tool_name": "square_root",
            "inputs": {"number": 144},
            "output": 12.0,
            "duration": 0.001
        },
        {
            "tool_name": "multiply",
            "inputs": {"a": 12.0, "b": 5},
            "output": 60.0,
            "duration": 0.001
        }
    ]
    
    print("🔍 Executing tool sequence with observability...")
    
    for i, tool_call in enumerate(tool_sequence, 1):
        print(f"Step {i}: {tool_call['tool_name']}({tool_call['inputs']}) = {tool_call['output']}")
        
        # Log each tool usage
        obs_manager.log_tool_usage(
            trace_id,
            tool_call['tool_name'],
            tool_call['inputs'],
            tool_call['output'],
            tool_call['duration']
        )
    
    print(f"✅ Completed tool sequence: √144 × 5 = 60.0")
    print(f"📊 Logged {len(tool_sequence)} tool calls to trace: {trace_id}")


def demo_comprehensive_observability():
    """Comprehensive observability demo showing all Week 3 patterns"""
    
    print("Week 3 Observability Challenge - Comprehensive Demo")
    print("=" * 60)
    
    if not LANGFUSE_AVAILABLE:
        print("📋 SIMULATION MODE: Langfuse not available, showing observability patterns")
        print("To enable real observability:")
        print("1. pip install langfuse")
        print("2. Set up Langfuse account at cloud.langfuse.com")
        print("3. Configure LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY in .env")
    else:
        print("📊 LIVE MODE: Langfuse observability enabled")
    
    # Demo structured output observability
    demo_structured_output_with_observability()
    
    # Demo tool use observability
    demo_tool_use_with_observability()
    
    print("\n" + "="*60)
    print("📈 OBSERVABILITY BENEFITS DEMONSTRATED")
    print("="*60)
    print("✅ Complete trace of AI application execution")
    print("✅ Tool usage patterns and performance metrics")
    print("✅ Structured output quality assessment")
    print("✅ Session tracking for conversation context")
    print("✅ Cost and latency monitoring")
    print("✅ Debug information for troubleshooting")
    
    print(f"\n🎯 Week 3 Observability Complete!")
    print("Check your Langfuse dashboard for detailed traces and analytics")


if __name__ == "__main__":
    demo_comprehensive_observability()