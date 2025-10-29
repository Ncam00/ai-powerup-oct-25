"""
Week 3 Deep Dive: Complex Multi-Tool Agent
Combining structured output, advanced tools, and comprehensive observability
"""

import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Import our advanced components
import sys
import os
sys.path.append('/root/overview/week3-deep-dive')

from advanced_pydantic_v2 import Portfolio, ContactInfo, Skill, Experience, Project, SkillLevel
from advanced_tools_system import (
    enhanced_calculator, text_analysis_tool, data_processing_tool, 
    ToolChain, ToolResult, track_performance
)
from advanced_observability import AdvancedObservabilityManager, ExperimentConfig, ExperimentType

# Mock LangChain components for demonstration
class MockChatModel:
    """Mock chat model for demonstration"""
    
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        self.tools = []
    
    def bind_tools(self, tools):
        self.tools = tools
        return self
    
    def invoke(self, messages, **kwargs):
        # Simple mock response based on input
        if isinstance(messages, list) and messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                content = last_message.content
            else:
                content = str(last_message)
        else:
            content = str(messages)
        
        # Simulate tool usage based on content
        mock_response = MockAIMessage(
            content=f"I'll help you with: {content[:100]}...",
            tool_calls=self._generate_mock_tool_calls(content)
        )
        
        return mock_response
    
    def _generate_mock_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Generate mock tool calls based on content"""
        tool_calls = []
        
        # Simple heuristics for tool selection
        if any(word in content.lower() for word in ['calculate', 'math', 'compute']):
            tool_calls.append({
                "id": str(uuid.uuid4()),
                "name": "enhanced_calculator",
                "args": {"expression": "2 + 2"}
            })
        
        if any(word in content.lower() for word in ['analyze', 'text', 'sentiment']):
            tool_calls.append({
                "id": str(uuid.uuid4()),
                "name": "text_analysis_tool", 
                "args": {"text": content[:200], "analysis_type": "sentiment"}
            })
        
        if any(word in content.lower() for word in ['portfolio', 'profile', 'resume']):
            tool_calls.append({
                "id": str(uuid.uuid4()),
                "name": "portfolio_builder",
                "args": {"action": "validate", "data": content}
            })
        
        return tool_calls


class MockAIMessage:
    """Mock AI message with tool calls"""
    
    def __init__(self, content: str, tool_calls: List[Dict[str, Any]] = None):
        self.content = content
        self.tool_calls = tool_calls or []


class TaskType(str, Enum):
    """Types of tasks the agent can handle"""
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    DATA_PROCESSING = "data_processing"
    TEXT_ANALYSIS = "text_analysis"
    CALCULATION = "calculation"
    RESEARCH_SYNTHESIS = "research_synthesis"


@dataclass
class AgentTask:
    """Structured task definition"""
    id: str
    task_type: TaskType
    description: str
    input_data: Dict[str, Any]
    priority: int = 1
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class ComplexMultiToolAgent:
    """Advanced agent combining all Week 3 concepts"""
    
    def __init__(self, name: str = "DeepDive_Agent", model: str = "gpt-4"):
        self.name = name
        self.model = MockChatModel(model)
        self.observability = AdvancedObservabilityManager(f"agent_{name.lower()}")
        self.task_history = []
        self.active_experiments = {}
        
        # Bind tools to model
        self.tools = [
            enhanced_calculator,
            text_analysis_tool,
            data_processing_tool
        ]
        self.model.bind_tools(self.tools)
        
        # Initialize A/B testing for agent behavior
        self._setup_agent_experiments()
    
    def _setup_agent_experiments(self):
        """Setup A/B testing experiments for agent behavior"""
        
        # Experiment 1: Response style
        response_style_config = ExperimentConfig(
            name="response_style",
            experiment_type=ExperimentType.PROMPT_VARIANT,
            variants=[
                {"style": "detailed", "explanation_level": "high"},
                {"style": "concise", "explanation_level": "medium"},
                {"style": "interactive", "explanation_level": "medium"}
            ],
            traffic_split=[0.4, 0.3, 0.3],
            success_metrics=["user_satisfaction", "task_completion_rate"]
        )
        
        self.observability.create_experiment(response_style_config)
        
        # Experiment 2: Tool selection strategy
        tool_strategy_config = ExperimentConfig(
            name="tool_selection_strategy",
            experiment_type=ExperimentType.TOOL_SELECTION,
            variants=[
                {"strategy": "conservative", "confidence_threshold": 0.8},
                {"strategy": "aggressive", "confidence_threshold": 0.6},
                {"strategy": "adaptive", "confidence_threshold": 0.7}
            ],
            traffic_split=[0.33, 0.33, 0.34],
            success_metrics=["tool_accuracy", "execution_time"]
        )
        
        self.observability.create_experiment(tool_strategy_config)
    
    def process_task(self, task: AgentTask, user_id: str = None) -> Dict[str, Any]:
        """Process a complex task using all Week 3 concepts"""
        
        # Start observability tracking
        conversation_id = f"task_{task.id}"
        
        # Get experiment variants for this user
        response_variant = self.observability.get_experiment_variant("response_style", user_id)
        tool_variant = self.observability.get_experiment_variant("tool_selection_strategy", user_id)
        
        # Process based on task type
        start_time = time.time()
        
        try:
            if task.task_type == TaskType.PORTFOLIO_ANALYSIS:
                result = self._process_portfolio_task(task, response_variant)
            elif task.task_type == TaskType.DATA_PROCESSING:
                result = self._process_data_task(task, tool_variant)
            elif task.task_type == TaskType.TEXT_ANALYSIS:
                result = self._process_text_task(task, response_variant)
            elif task.task_type == TaskType.CALCULATION:
                result = self._process_calculation_task(task, tool_variant)
            else:
                result = self._process_general_task(task, response_variant)
            
            execution_time = time.time() - start_time
            
            # Track with observability
            self.observability.track_conversation(
                conversation_id=conversation_id,
                user_input=task.description,
                ai_response=str(result),
                model_used=self.model.model_name,
                tools_used=result.get('tools_used', []),
                custom_metadata={
                    'task_type': task.task_type,
                    'task_id': task.id,
                    'execution_time': execution_time,
                    'response_variant': response_variant,
                    'tool_variant': tool_variant,
                    'user_id': user_id
                }
            )
            
            # Evaluate the result
            evaluation_scores = self.observability.evaluate_conversation(
                conversation_id,
                {
                    "task_completion": 0.3,
                    "response_quality": 0.25,
                    "tool_usage": 0.25,
                    "efficiency": 0.2
                }
            )
            
            # Store task in history
            task_result = {
                'task': task,
                'result': result,
                'execution_time': execution_time,
                'evaluation_scores': evaluation_scores,
                'variants_used': {
                    'response': response_variant,
                    'tool_selection': tool_variant
                },
                'completed_at': datetime.now()
            }
            
            self.task_history.append(task_result)
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time,
                'evaluation_scores': evaluation_scores,
                'conversation_id': conversation_id
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            error_result = {
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'task_id': task.id
            }
            
            # Track error with observability
            self.observability.track_conversation(
                conversation_id=conversation_id,
                user_input=task.description,
                ai_response=f"Error: {str(e)}",
                model_used=self.model.model_name,
                custom_metadata={
                    'error': True,
                    'task_type': task.task_type,
                    'execution_time': execution_time
                }
            )
            
            return error_result
    
    def _process_portfolio_task(self, task: AgentTask, variant: Dict[str, Any]) -> Dict[str, Any]:
        """Process portfolio-related tasks with structured output"""
        
        # Extract portfolio data from input
        portfolio_data = task.input_data.get('portfolio_data', {})
        action = task.input_data.get('action', 'validate')
        
        tools_used = []
        
        if action == 'validate':
            try:
                # Use Pydantic for validation
                portfolio = Portfolio(**portfolio_data)
                
                # Analyze with text analysis tool
                summary_analysis = text_analysis_tool.func(
                    portfolio.summary, 
                    "word_count"
                )
                tools_used.append('text_analysis_tool')
                
                result = {
                    'validation_status': 'success',
                    'portfolio_name': portfolio.name,
                    'skills_count': len(portfolio.skills),
                    'experience_count': len(portfolio.experience),
                    'summary_analysis': summary_analysis,
                    'structured_data': portfolio.model_dump()
                }
                
            except Exception as e:
                result = {
                    'validation_status': 'failed',
                    'errors': [str(e)],
                    'suggestions': ['Check required fields', 'Validate data types']
                }
        
        elif action == 'analyze':
            # Perform comprehensive analysis
            if portfolio_data:
                skills = portfolio_data.get('skills', [])
                experience = portfolio_data.get('experience', [])
                
                # Calculate experience insights
                total_experience = sum(exp.get('years_experience', 0) for exp in skills if isinstance(exp, dict))
                
                result = {
                    'analysis_type': 'comprehensive',
                    'total_skills': len(skills),
                    'total_experience_years': total_experience,
                    'skill_diversity': len(set(skill.get('level') for skill in skills if isinstance(skill, dict))),
                    'recommendations': [
                        'Add more advanced skills',
                        'Include project outcomes',
                        'Quantify achievements'
                    ]
                }
                tools_used.append('portfolio_analyzer')
        
        result['tools_used'] = tools_used
        result['response_style'] = variant.get('style', 'detailed')
        
        return result
    
    def _process_data_task(self, task: AgentTask, variant: Dict[str, Any]) -> Dict[str, Any]:
        """Process data-related tasks"""
        
        data = task.input_data.get('data', '')
        operation = task.input_data.get('operation', 'parse')
        format_type = task.input_data.get('format', 'json')
        
        # Use data processing tool
        result = data_processing_tool.func(data, operation, format_type)
        
        # Create tool chain for complex operations
        if operation == 'transform_and_analyze':
            chain = ToolChain()
            chain.add_tool(data_processing_tool, operation='transform', format_type=format_type)
            chain.add_tool(text_analysis_tool, analysis_type='word_count')
            
            chain_results = chain.execute(data)
            
            return {
                'chain_results': [r.model_dump() for r in chain_results],
                'tools_used': ['data_processing_tool', 'text_analysis_tool'],
                'strategy': variant.get('strategy', 'conservative')
            }
        
        return {
            'result': result,
            'tools_used': ['data_processing_tool'],
            'confidence': variant.get('confidence_threshold', 0.7)
        }
    
    def _process_text_task(self, task: AgentTask, variant: Dict[str, Any]) -> Dict[str, Any]:
        """Process text analysis tasks"""
        
        text = task.input_data.get('text', '')
        analysis_types = task.input_data.get('analysis_types', ['sentiment', 'word_count'])
        
        results = {}
        tools_used = []
        
        for analysis_type in analysis_types:
            result = text_analysis_tool.func(text, analysis_type)
            results[analysis_type] = result
            tools_used.append('text_analysis_tool')
        
        # Add comprehensive analysis based on variant
        if variant.get('explanation_level') == 'high':
            results['detailed_insights'] = [
                "Text demonstrates clear communication patterns",
                "Vocabulary complexity suggests target audience level",
                "Sentiment analysis reveals emotional undertones"
            ]
        
        return {
            'analysis_results': results,
            'tools_used': list(set(tools_used)),
            'explanation_level': variant.get('explanation_level', 'medium')
        }
    
    def _process_calculation_task(self, task: AgentTask, variant: Dict[str, Any]) -> Dict[str, Any]:
        """Process calculation tasks"""
        
        expression = task.input_data.get('expression', '')
        
        # Use enhanced calculator
        calc_result = enhanced_calculator.func(expression)
        
        return {
            'calculation_result': calc_result,
            'expression': expression,
            'tools_used': ['enhanced_calculator'],
            'confidence_threshold': variant.get('confidence_threshold', 0.7)
        }
    
    def _process_general_task(self, task: AgentTask, variant: Dict[str, Any]) -> Dict[str, Any]:
        """Process general tasks using AI reasoning"""
        
        # Simulate AI processing
        mock_response = self.model.invoke([{"content": task.description}])
        
        tools_used = []
        
        # Execute any tool calls
        tool_results = {}
        for tool_call in mock_response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            # Find and execute the tool
            for tool in self.tools:
                if tool.name == tool_name:
                    try:
                        result = tool.func(**tool_args)
                        tool_results[tool_name] = result
                        tools_used.append(tool_name)
                    except Exception as e:
                        tool_results[tool_name] = f"Error: {str(e)}"
                    break
        
        return {
            'ai_response': mock_response.content,
            'tool_results': tool_results,
            'tools_used': tools_used,
            'response_style': variant.get('style', 'detailed')
        }
    
    def generate_agent_report(self) -> Dict[str, Any]:
        """Generate comprehensive agent performance report"""
        
        # Get observability dashboard
        dashboard = self.observability.generate_analytics_dashboard()
        
        # Calculate agent-specific metrics
        total_tasks = len(self.task_history)
        successful_tasks = sum(1 for task in self.task_history if task.get('result', {}).get('success', True))
        
        avg_execution_time = 0
        if self.task_history:
            avg_execution_time = sum(task.get('execution_time', 0) for task in self.task_history) / total_tasks
        
        # Task type distribution
        task_types = {}
        for task_result in self.task_history:
            task_type = task_result['task'].task_type
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        # Tool usage statistics
        tool_usage = {}
        for task_result in self.task_history:
            tools = task_result.get('result', {}).get('tools_used', [])
            for tool in tools:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        return {
            'agent_name': self.name,
            'performance_metrics': {
                'total_tasks': total_tasks,
                'success_rate': (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                'avg_execution_time': round(avg_execution_time, 3),
                'task_type_distribution': task_types,
                'tool_usage_statistics': tool_usage
            },
            'observability_dashboard': dashboard,
            'active_experiments': len(self.observability.experiments),
            'generated_at': datetime.now().isoformat()
        }


def demonstrate_complex_agent():
    """Demonstrate the complex multi-tool agent"""
    
    print("🤖 Complex Multi-Tool Agent Demo")
    print("=" * 50)
    
    # Initialize agent
    agent = ComplexMultiToolAgent("DeepDive_Master", "gpt-4")
    
    # Create diverse tasks
    tasks = [
        AgentTask(
            id="task_001",
            task_type=TaskType.PORTFOLIO_ANALYSIS,
            description="Validate and analyze a developer portfolio",
            input_data={
                'action': 'validate',
                'portfolio_data': {
                    "name": "Sarah Chen",
                    "title": "Senior Full-Stack Developer",
                    "summary": "Experienced developer with expertise in modern web technologies and AI integration.",
                    "contact": {
                        "email": "sarah.chen@example.com",
                        "linkedin": "https://linkedin.com/in/sarah-chen"
                    },
                    "skills": [
                        {"name": "Python", "level": "advanced", "years_experience": 5, "certified": True},
                        {"name": "React", "level": "intermediate", "years_experience": 3, "certified": False}
                    ],
                    "experience": [
                        {
                            "company": "Tech Corp",
                            "position": "Senior Developer",
                            "start_date": "2022-01-01",
                            "is_current": True,
                            "description": "Leading development of AI-powered applications"
                        }
                    ]
                }
            }
        ),
        AgentTask(
            id="task_002",
            task_type=TaskType.TEXT_ANALYSIS,
            description="Analyze customer feedback for sentiment and insights",
            input_data={
                'text': "The new AI features are absolutely amazing! They work perfectly and have saved us so much time. Highly recommend!",
                'analysis_types': ['sentiment', 'word_count', 'readability']
            }
        ),
        AgentTask(
            id="task_003",
            task_type=TaskType.CALCULATION,
            description="Calculate ROI for a machine learning project",
            input_data={
                'expression': '(150000 - 80000) / 80000 * 100'
            }
        ),
        AgentTask(
            id="task_004",
            task_type=TaskType.DATA_PROCESSING,
            description="Process and transform JSON user data",
            input_data={
                'data': '{"users": [{"name": "john", "score": 85}, {"name": "jane", "score": 92}]}',
                'operation': 'transform',
                'format': 'json'
            }
        )
    ]
    
    # Process tasks
    print("\\n📋 Processing Complex Tasks:")
    results = []
    
    for i, task in enumerate(tasks):
        user_id = f"user_{i+1}"
        print(f"\\n   Task {i+1}: {task.task_type} - {task.description[:50]}...")
        
        result = agent.process_task(task, user_id)
        results.append(result)
        
        if result['success']:
            print(f"   ✅ Completed in {result['execution_time']:.3f}s")
            print(f"   📊 Evaluation: {result['evaluation_scores']}")
            print(f"   🛠️  Tools used: {result['result'].get('tools_used', [])}")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    # Run experiment analysis
    print("\\n🧪 A/B Testing Analysis:")
    for experiment_name in agent.observability.experiments.keys():
        analysis = agent.observability.run_experiment_analysis(experiment_name)
        print(f"   {experiment_name}: Winning variant {analysis['winning_variant']}")
    
    # Generate comprehensive report
    print("\\n📊 Agent Performance Report:")
    report = agent.generate_agent_report()
    
    print(f"   Agent: {report['agent_name']}")
    print(f"   Tasks processed: {report['performance_metrics']['total_tasks']}")
    print(f"   Success rate: {report['performance_metrics']['success_rate']:.1f}%")
    print(f"   Avg execution time: {report['performance_metrics']['avg_execution_time']}s")
    print(f"   Tool usage: {report['performance_metrics']['tool_usage_statistics']}")
    print(f"   Active experiments: {report['active_experiments']}")
    
    print("\\n🎯 Week 3 Deep Dive Features Demonstrated:")
    print("• ✅ Structured Output: Pydantic models for portfolio validation")
    print("• ✅ Advanced Tools: Enhanced calculator, text analysis, data processing")
    print("• ✅ Tool Chaining: Multiple tools working together")
    print("• ✅ A/B Testing: Response style and tool selection experiments")
    print("• ✅ Comprehensive Observability: Tracking, evaluation, analytics")
    print("• ✅ Error Handling: Graceful failure and recovery")
    print("• ✅ Performance Metrics: Execution time and success tracking")
    print("• ✅ Complex Task Processing: Multi-type task handling")
    
    return agent, results, report


if __name__ == "__main__":
    agent, results, report = demonstrate_complex_agent()