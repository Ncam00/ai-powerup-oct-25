"""
Week 3 Deep Dive: Advanced Langfuse Observability Patterns
Exploring custom metadata, evaluation frameworks, A/B testing, and analytics
"""

import os
import uuid
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import random

# Mock Langfuse classes for demonstration (since we don't have API keys)
class MockLangfuseCallback:
    """Mock Langfuse callback for demonstration"""
    
    def __init__(self, secret_key: str, public_key: str, **kwargs):
        self.secret_key = secret_key
        self.public_key = public_key
        self.session_id = kwargs.get('session_id', str(uuid.uuid4()))
        self.user_id = kwargs.get('user_id', 'demo_user')
        self.traces = []
        self.observations = []
        
    def start_trace(self, name: str, metadata: Dict[str, Any] = None):
        trace_data = {
            'id': str(uuid.uuid4()),
            'name': name,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'metadata': metadata or {},
            'start_time': datetime.now(),
            'observations': []
        }
        self.traces.append(trace_data)
        return trace_data
    
    def add_observation(self, trace_id: str, observation_type: str, data: Dict[str, Any]):
        observation = {
            'id': str(uuid.uuid4()),
            'trace_id': trace_id,
            'type': observation_type,
            'data': data,
            'timestamp': datetime.now()
        }
        self.observations.append(observation)
        return observation


class ExperimentType(str, Enum):
    """Types of experiments for A/B testing"""
    PROMPT_VARIANT = "prompt_variant"
    MODEL_COMPARISON = "model_comparison"
    TOOL_SELECTION = "tool_selection"
    PARAMETER_TUNING = "parameter_tuning"


@dataclass
class ExperimentConfig:
    """Configuration for A/B testing experiments"""
    name: str
    experiment_type: ExperimentType
    variants: List[Dict[str, Any]]
    traffic_split: List[float]  # Should sum to 1.0
    success_metrics: List[str]
    metadata: Dict[str, Any] = None


class AdvancedObservabilityManager:
    """Advanced observability manager with comprehensive tracking"""
    
    def __init__(self, project_name: str = "ai_deep_dive"):
        self.project_name = project_name
        self.langfuse = MockLangfuseCallback("mock_secret", "mock_public")
        self.experiments = {}
        self.evaluation_results = []
        self.custom_metrics = {}
        
    def create_experiment(self, config: ExperimentConfig):
        """Create a new A/B testing experiment"""
        self.experiments[config.name] = {
            'config': config,
            'results': [],
            'created_at': datetime.now(),
            'active': True
        }
        
        print(f"🧪 Created experiment: {config.name}")
        print(f"   Type: {config.experiment_type}")
        print(f"   Variants: {len(config.variants)}")
        print(f"   Traffic split: {config.traffic_split}")
    
    def get_experiment_variant(self, experiment_name: str, user_id: str = None) -> Dict[str, Any]:
        """Get variant for A/B testing based on user ID"""
        if experiment_name not in self.experiments:
            raise ValueError(f"Experiment {experiment_name} not found")
        
        config = self.experiments[experiment_name]['config']
        
        # Use user_id for consistent assignment, fallback to random
        if user_id:
            hash_value = hash(user_id) % 100
        else:
            hash_value = random.randint(0, 99)
        
        # Determine variant based on traffic split
        cumulative = 0
        for i, split in enumerate(config.traffic_split):
            cumulative += split * 100
            if hash_value < cumulative:
                variant = config.variants[i]
                variant['variant_id'] = i
                return variant
        
        # Fallback to last variant
        variant = config.variants[-1]
        variant['variant_id'] = len(config.variants) - 1
        return variant
    
    def track_conversation(self, 
                          conversation_id: str,
                          user_input: str, 
                          ai_response: str,
                          model_used: str,
                          tools_used: List[str] = None,
                          custom_metadata: Dict[str, Any] = None):
        """Track a conversation with comprehensive metadata"""
        
        # Create trace
        trace = self.langfuse.start_trace(
            name="conversation",
            metadata={
                "conversation_id": conversation_id,
                "model": model_used,
                "tools_used": tools_used or [],
                "custom": custom_metadata or {},
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Add user input observation
        self.langfuse.add_observation(
            trace['id'],
            "user_input",
            {
                "content": user_input,
                "token_count": len(user_input.split()),
                "character_count": len(user_input)
            }
        )
        
        # Add AI response observation
        self.langfuse.add_observation(
            trace['id'],
            "ai_response", 
            {
                "content": ai_response,
                "token_count": len(ai_response.split()),
                "character_count": len(ai_response),
                "model": model_used,
                "response_time": random.uniform(0.5, 3.0)  # Simulated
            }
        )
        
        # Track custom metrics
        self._update_custom_metrics(conversation_id, user_input, ai_response, model_used)
        
        return trace['id']
    
    def _update_custom_metrics(self, conversation_id: str, user_input: str, ai_response: str, model: str):
        """Update custom metrics for analytics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.custom_metrics:
            self.custom_metrics[today] = {
                'total_conversations': 0,
                'total_tokens': 0,
                'models_used': {},
                'avg_response_length': 0,
                'user_engagement': []
            }
        
        metrics = self.custom_metrics[today]
        metrics['total_conversations'] += 1
        metrics['total_tokens'] += len(user_input.split()) + len(ai_response.split())
        
        if model in metrics['models_used']:
            metrics['models_used'][model] += 1
        else:
            metrics['models_used'][model] = 1
        
        # Calculate engagement score (simple heuristic)
        engagement_score = min(len(user_input) / 10, 10)  # Max 10
        metrics['user_engagement'].append(engagement_score)
        
        # Update average response length
        response_lengths = [len(ai_response)]
        if hasattr(self, '_response_lengths'):
            self._response_lengths.append(len(ai_response))
        else:
            self._response_lengths = [len(ai_response)]
        
        metrics['avg_response_length'] = sum(self._response_lengths) / len(self._response_lengths)
    
    def evaluate_conversation(self, 
                            trace_id: str,
                            evaluation_criteria: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate conversation quality with custom criteria"""
        
        results = {}
        
        # Simulated evaluation scores
        for criterion, weight in evaluation_criteria.items():
            if criterion == "relevance":
                score = random.uniform(0.7, 1.0)
            elif criterion == "helpfulness":
                score = random.uniform(0.6, 0.95)
            elif criterion == "clarity":
                score = random.uniform(0.8, 1.0)
            elif criterion == "accuracy":
                score = random.uniform(0.75, 1.0)
            else:
                score = random.uniform(0.5, 1.0)
            
            results[criterion] = round(score, 3)
        
        # Store evaluation result
        evaluation_result = {
            'trace_id': trace_id,
            'criteria': evaluation_criteria,
            'scores': results,
            'overall_score': round(sum(results.values()) / len(results), 3),
            'evaluated_at': datetime.now()
        }
        
        self.evaluation_results.append(evaluation_result)
        
        return results
    
    def run_experiment_analysis(self, experiment_name: str) -> Dict[str, Any]:
        """Analyze A/B testing experiment results"""
        
        if experiment_name not in self.experiments:
            return {"error": f"Experiment {experiment_name} not found"}
        
        experiment = self.experiments[experiment_name]
        config = experiment['config']
        
        # Simulate experiment results
        variant_results = []
        for i, variant in enumerate(config.variants):
            # Simulate metrics for each variant
            sample_size = random.randint(100, 500)
            
            variant_result = {
                'variant_id': i,
                'variant_config': variant,
                'sample_size': sample_size,
                'metrics': {}
            }
            
            # Generate metrics based on success criteria
            for metric in config.success_metrics:
                if metric == "conversion_rate":
                    base_rate = 0.15
                    variance = random.uniform(-0.05, 0.05)
                    variant_result['metrics'][metric] = max(0, base_rate + variance)
                elif metric == "satisfaction_score":
                    base_score = 4.2
                    variance = random.uniform(-0.3, 0.3)
                    variant_result['metrics'][metric] = max(1, min(5, base_score + variance))
                elif metric == "response_time":
                    base_time = 2.5
                    variance = random.uniform(-0.5, 0.5)
                    variant_result['metrics'][metric] = max(0.5, base_time + variance)
                else:
                    variant_result['metrics'][metric] = random.uniform(0.5, 1.0)
            
            variant_results.append(variant_result)
        
        # Determine winning variant
        if "conversion_rate" in config.success_metrics:
            winning_variant = max(variant_results, key=lambda x: x['metrics']['conversion_rate'])
        else:
            # Use first metric as tiebreaker
            primary_metric = config.success_metrics[0]
            winning_variant = max(variant_results, key=lambda x: x['metrics'][primary_metric])
        
        analysis = {
            'experiment_name': experiment_name,
            'experiment_type': config.experiment_type,
            'variant_results': variant_results,
            'winning_variant': winning_variant['variant_id'],
            'statistical_significance': random.choice([True, False]),
            'analyzed_at': datetime.now().isoformat()
        }
        
        return analysis
    
    def generate_analytics_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive analytics dashboard"""
        
        dashboard = {
            'overview': {
                'total_traces': len(self.langfuse.traces),
                'total_observations': len(self.langfuse.observations),
                'active_experiments': len([e for e in self.experiments.values() if e['active']]),
                'evaluation_count': len(self.evaluation_results)
            },
            'daily_metrics': self.custom_metrics,
            'experiment_summary': {},
            'evaluation_summary': {},
            'top_insights': []
        }
        
        # Experiment summary
        for name, experiment in self.experiments.items():
            dashboard['experiment_summary'][name] = {
                'type': experiment['config'].experiment_type,
                'variants': len(experiment['config'].variants),
                'status': 'active' if experiment['active'] else 'completed'
            }
        
        # Evaluation summary
        if self.evaluation_results:
            avg_scores = {}
            for result in self.evaluation_results:
                for criterion, score in result['scores'].items():
                    if criterion not in avg_scores:
                        avg_scores[criterion] = []
                    avg_scores[criterion].append(score)
            
            dashboard['evaluation_summary'] = {
                criterion: {
                    'average': round(sum(scores) / len(scores), 3),
                    'min': round(min(scores), 3),
                    'max': round(max(scores), 3)
                }
                for criterion, scores in avg_scores.items()
            }
        
        # Generate insights
        insights = [
            "📈 User engagement has increased by 12% this week",
            "🎯 Experiment 'prompt_optimization' shows 15% improvement in conversion",
            "⚡ Average response time is 2.3 seconds across all conversations",
            "🔍 'Helpfulness' scores are consistently above 0.85",
            "🧪 A/B testing reveals users prefer shorter, more direct responses"
        ]
        dashboard['top_insights'] = random.sample(insights, 3)
        
        return dashboard
    
    def export_data_for_analysis(self, format_type: str = "json") -> str:
        """Export observability data for external analysis"""
        
        export_data = {
            'project': self.project_name,
            'exported_at': datetime.now().isoformat(),
            'traces': [
                {
                    'id': trace['id'],
                    'name': trace['name'],
                    'session_id': trace['session_id'],
                    'user_id': trace['user_id'],
                    'metadata': trace['metadata'],
                    'start_time': trace['start_time'].isoformat()
                }
                for trace in self.langfuse.traces
            ],
            'observations': [
                {
                    'id': obs['id'],
                    'trace_id': obs['trace_id'],
                    'type': obs['type'],
                    'data': obs['data'],
                    'timestamp': obs['timestamp'].isoformat()
                }
                for obs in self.langfuse.observations
            ],
            'evaluations': [
                {
                    'trace_id': eval_result['trace_id'],
                    'scores': eval_result['scores'],
                    'overall_score': eval_result['overall_score'],
                    'evaluated_at': eval_result['evaluated_at'].isoformat()
                }
                for eval_result in self.evaluation_results
            ],
            'experiments': {
                name: {
                    'config': {
                        'name': exp['config'].name,
                        'type': exp['config'].experiment_type,
                        'variants': exp['config'].variants,
                        'traffic_split': exp['config'].traffic_split
                    },
                    'created_at': exp['created_at'].isoformat(),
                    'active': exp['active']
                }
                for name, exp in self.experiments.items()
            }
        }
        
        if format_type == "json":
            return json.dumps(export_data, indent=2, default=str)
        else:
            return str(export_data)


def demonstrate_advanced_observability():
    """Demonstrate advanced observability patterns"""
    
    print("📈 Advanced Observability Patterns Demo")
    print("=" * 50)
    
    # Initialize observability manager
    obs_manager = AdvancedObservabilityManager("week3_deep_dive")
    
    # 1. Create A/B Testing Experiment
    print("\n1. Creating A/B Testing Experiment:")
    experiment_config = ExperimentConfig(
        name="prompt_optimization",
        experiment_type=ExperimentType.PROMPT_VARIANT,
        variants=[
            {"prompt_style": "detailed", "max_tokens": 500},
            {"prompt_style": "concise", "max_tokens": 200},
            {"prompt_style": "conversational", "max_tokens": 300}
        ],
        traffic_split=[0.4, 0.3, 0.3],
        success_metrics=["conversion_rate", "satisfaction_score", "response_time"],
        metadata={"created_by": "ai_team", "purpose": "optimize_user_engagement"}
    )
    
    obs_manager.create_experiment(experiment_config)
    
    # Test variant assignment
    print("\\n   Testing variant assignment:")
    for user_id in ["user_123", "user_456", "user_789"]:
        variant = obs_manager.get_experiment_variant("prompt_optimization", user_id)
        print(f"   User {user_id}: Variant {variant['variant_id']} ({variant['prompt_style']})")
    
    # 2. Track Multiple Conversations
    print("\\n2. Tracking Conversations with Custom Metadata:")
    conversations = [
        {
            "id": "conv_001",
            "user_input": "How do I implement a binary search algorithm?",
            "ai_response": "Here's a step-by-step implementation of binary search in Python...",
            "model": "gpt-4",
            "tools": ["code_generator", "syntax_highlighter"],
            "metadata": {"topic": "algorithms", "difficulty": "intermediate"}
        },
        {
            "id": "conv_002", 
            "user_input": "What's the weather like?",
            "ai_response": "I don't have access to real-time weather data, but I can help you find weather information...",
            "model": "gpt-3.5-turbo",
            "tools": ["web_search"],
            "metadata": {"topic": "weather", "difficulty": "basic"}
        }
    ]
    
    trace_ids = []
    for conv in conversations:
        trace_id = obs_manager.track_conversation(
            conv["id"], conv["user_input"], conv["ai_response"], 
            conv["model"], conv["tools"], conv["metadata"]
        )
        trace_ids.append(trace_id)
        print(f"   Tracked conversation {conv['id']}: {trace_id[:8]}...")
    
    # 3. Evaluate Conversations
    print("\\n3. Evaluating Conversation Quality:")
    evaluation_criteria = {
        "relevance": 0.3,
        "helpfulness": 0.25,
        "clarity": 0.25,
        "accuracy": 0.2
    }
    
    for i, trace_id in enumerate(trace_ids):
        scores = obs_manager.evaluate_conversation(trace_id, evaluation_criteria)
        print(f"   Conversation {i+1} scores: {scores}")
    
    # 4. Run Experiment Analysis
    print("\\n4. A/B Testing Analysis:")
    analysis = obs_manager.run_experiment_analysis("prompt_optimization")
    print(f"   Winning variant: {analysis['winning_variant']}")
    print(f"   Statistical significance: {analysis['statistical_significance']}")
    
    for result in analysis['variant_results']:
        print(f"   Variant {result['variant_id']}: {result['metrics']}")
    
    # 5. Generate Analytics Dashboard
    print("\\n5. Analytics Dashboard:")
    dashboard = obs_manager.generate_analytics_dashboard()
    
    print(f"   Overview: {dashboard['overview']}")
    print(f"   Active experiments: {dashboard['experiment_summary']}")
    print(f"   Evaluation summary: {dashboard['evaluation_summary']}")
    print("   Top insights:")
    for insight in dashboard['top_insights']:
        print(f"   • {insight}")
    
    # 6. Data Export
    print("\\n6. Data Export for Analysis:")
    export_data = obs_manager.export_data_for_analysis()
    print(f"   Exported {len(obs_manager.langfuse.traces)} traces and {len(obs_manager.langfuse.observations)} observations")
    print(f"   Export size: {len(export_data)} characters")
    
    print("\\n📊 Advanced Observability Features Demonstrated:")
    print("• A/B testing with traffic splitting")
    print("• Custom metadata tracking and analytics")
    print("• Conversation evaluation with multiple criteria")
    print("• Experiment analysis and statistical significance")
    print("• Comprehensive analytics dashboards")
    print("• Data export for external analysis tools")
    print("• Performance metrics and user engagement tracking")


if __name__ == "__main__":
    demonstrate_advanced_observability()