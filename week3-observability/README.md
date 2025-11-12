# Week 3: Observability Challenge - Langfuse Integration

This directory demonstrates Week 3's **Observability Challenge** with comprehensive Langfuse tracing for LangChain applications.

## 🎯 Learning Objectives

- **Langfuse Setup**: Configure cloud observability for AI applications
- **Trace Management**: Create and manage execution traces for debugging
- **Performance Monitoring**: Track token usage, costs, and latency
- **Quality Assessment**: Monitor structured output and tool usage patterns

## 🚀 What This Demonstrates

### Core Observability Patterns
1. **Trace Creation**: Session-based tracking of AI application flows
2. **Tool Usage Logging**: Monitor individual tool calls and performance
3. **Structured Output Tracking**: Quality assessment and extraction monitoring
4. **Error Handling**: Graceful observability failures and fallbacks

### Real-World Benefits
- **Production Monitoring**: Track AI application health in real-time
- **Performance Optimization**: Identify bottlenecks and optimize costs
- **Quality Assurance**: Monitor output quality and user satisfaction
- **Debugging Support**: Detailed traces for troubleshooting issues

## 🔧 Implementation Highlights

### Langfuse Integration Setup
```python
from langfuse.callback import CallbackHandler
from langfuse import Langfuse

# Callback handler for automatic LangChain tracing
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host="https://cloud.langfuse.com"
)

# Direct client for custom event logging
langfuse_client = Langfuse(
    secret_key=secret_key,
    public_key=public_key,
    host=host
)
```

### Comprehensive Observability Manager
- **Session Tracking**: UUID-based session identification
- **Tool Monitoring**: Individual tool call logging with duration
- **Quality Metrics**: Structured output quality scoring
- **Error Resilience**: Graceful fallbacks when observability fails

## 📊 Observability Features Demonstrated

### 1. Structured Output Monitoring
```python
obs_manager.log_structured_output(
    trace_id=trace_id,
    raw_text=messy_job_text,
    extracted_data=clean_job_data,
    quality_score=95.0
)
```

### 2. Tool Usage Tracking
```python
obs_manager.log_tool_usage(
    trace_id=trace_id,
    tool_name="square_root",
    inputs={"number": 144},
    output=12.0,
    duration=0.001
)
```

### 3. Comprehensive Trace Creation
- **Multi-step operations** tracked as single trace
- **Metadata enrichment** with application context
- **Performance metrics** for optimization insights
- **Quality scores** for reliability assessment

## 🎓 Week 3 Observability Skills

✅ **Langfuse Cloud Setup** - Account creation and API key configuration  
✅ **LangChain Integration** - Callback handler for automatic tracing  
✅ **Custom Event Logging** - Manual tool and output tracking  
✅ **Session Management** - User and conversation context tracking  
✅ **Performance Monitoring** - Duration, cost, and quality metrics  
✅ **Production Readiness** - Error handling and graceful degradation  

## 🔍 Dashboard Insights Available

### Trace Explorer
- **Execution Flow**: Step-by-step operation visualization
- **Input/Output**: Complete data flow inspection
- **Performance**: Latency and cost analysis per operation
- **Quality Metrics**: Custom scoring and assessment tracking

### Analytics Dashboard
- **Usage Patterns**: Most/least used tools and features
- **Performance Trends**: Speed and cost optimization opportunities
- **Quality Trends**: Output reliability and improvement areas
- **Error Analysis**: Failure patterns and debugging insights

## ⚙️ Setup Instructions

1. **Install Langfuse**: `pip install langfuse`
2. **Create Account**: Visit [cloud.langfuse.com](https://cloud.langfuse.com)
3. **Get API Keys**: Generate public/secret keys in project settings
4. **Configure Environment**:
   ```bash
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```
5. **Run Demo**: `python langfuse_demo.py`

## 🌟 Production Integration Patterns

### LangChain Applications
```python
# Automatic tracing for existing chains
response = chain.invoke(
    {"question": "Your question"},
    config={"callbacks": [langfuse_handler]}
)
```

### Custom Applications
```python
# Manual event tracking for complex workflows
trace_id = langfuse.trace(name="custom_workflow")
langfuse.generation(trace_id=trace_id, name="step1", input=data, output=result)
```

---

*This implementation showcases Week 3's focus on building robust, observable AI applications with comprehensive monitoring and quality assessment.*