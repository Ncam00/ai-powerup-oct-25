"""
Week 4 RAG Evaluation Framework
Comprehensive testing and quality assessment for Retrieval Augmented Generation systems
"""

import asyncio
import time
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

# For evaluation metrics
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EVAL_MODELS_AVAILABLE = True
except ImportError:
    EVAL_MODELS_AVAILABLE = False
    print("⚠️  sentence-transformers not available for semantic evaluation")


class EvaluationMetric(Enum):
    """Available evaluation metrics for RAG systems"""
    RETRIEVAL_PRECISION = "retrieval_precision"
    RETRIEVAL_RECALL = "retrieval_recall"
    CONTEXT_RELEVANCE = "context_relevance"
    ANSWER_FAITHFULNESS = "answer_faithfulness"
    ANSWER_RELEVANCE = "answer_relevance"
    RESPONSE_TIME = "response_time"
    CONTEXT_UTILIZATION = "context_utilization"


@dataclass
class TestCase:
    """A single test case for RAG evaluation"""
    question: str
    expected_answer: str = ""
    relevant_sources: List[str] = None
    category: str = "general"
    difficulty: str = "medium"  # easy, medium, hard
    
    def __post_init__(self):
        if self.relevant_sources is None:
            self.relevant_sources = []


@dataclass
class EvaluationResult:
    """Result of a single evaluation run"""
    test_case: TestCase
    generated_answer: str
    retrieved_context: List[Dict[str, Any]]
    metrics: Dict[str, float]
    response_time: float
    trace_id: str = ""


class RAGEvaluator:
    """Comprehensive evaluation framework for RAG systems"""
    
    def __init__(self):
        self.evaluation_model = None
        self.test_cases = []
        self.evaluation_results = []
        
        if EVAL_MODELS_AVAILABLE:
            print("🔧 Loading evaluation model...")
            try:
                self.evaluation_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Evaluation model loaded")
            except Exception as e:
                print(f"⚠️  Could not load evaluation model: {e}")
    
    def create_test_dataset(self) -> List[TestCase]:
        """Create a comprehensive test dataset for RAG evaluation"""
        
        test_cases = [
            # EU AI Act specific questions
            TestCase(
                question="What are the penalties for breaching the EU AI Act?",
                category="legal_penalties",
                difficulty="medium",
                relevant_sources=["eu-ai-act.html"]
            ),
            TestCase(
                question="How does the EU AI Act classify AI systems by risk level?",
                category="risk_classification",
                difficulty="medium",
                relevant_sources=["eu-ai-act.html"]
            ),
            TestCase(
                question="What are prohibited AI practices under the EU AI Act?",
                category="prohibited_practices",
                difficulty="easy",
                relevant_sources=["eu-ai-act.html"]
            ),
            
            # Complex reasoning questions
            TestCase(
                question="Compare the regulatory approaches between EU AI Act and New York recruitment laws",
                category="comparative_analysis",
                difficulty="hard",
                relevant_sources=["eu-ai-act.html", "ny-recruitment.html"]
            ),
            TestCase(
                question="What compliance requirements exist for high-risk AI systems in recruitment?",
                category="compliance_requirements",
                difficulty="hard",
                relevant_sources=["eu-ai-act.html", "ny-recruitment.html"]
            ),
            
            # Factual lookup questions
            TestCase(
                question="When does the EU AI Act come into force?",
                category="factual_lookup",
                difficulty="easy",
                relevant_sources=["eu-ai-act.html"]
            ),
            TestCase(
                question="What is the definition of artificial intelligence in the EU AI Act?",
                category="definitions",
                difficulty="easy",
                relevant_sources=["eu-ai-act.html"]
            ),
            
            # Edge cases and challenging questions
            TestCase(
                question="What happens if an AI system falls into multiple risk categories?",
                category="edge_cases",
                difficulty="hard",
                relevant_sources=["eu-ai-act.html"]
            ),
            TestCase(
                question="How do privacy principles relate to AI system requirements?",
                category="privacy_integration",
                difficulty="hard",
                relevant_sources=["AI-and-the-Information-Privacy-Principles.pdf"]
            ),
            
            # Questions requiring synthesis
            TestCase(
                question="What are the key differences between AI regulation in Europe vs other jurisdictions?",
                category="synthesis",
                difficulty="hard",
                relevant_sources=["eu-ai-act.html", "ny-recruitment.html"]
            )
        ]
        
        self.test_cases = test_cases
        print(f"📝 Created {len(test_cases)} test cases across {len(set(tc.category for tc in test_cases))} categories")
        return test_cases
    
    async def evaluate_rag_system(self, rag_system, test_cases: List[TestCase] = None) -> Dict[str, Any]:
        """Comprehensive evaluation of a RAG system"""
        
        if test_cases is None:
            test_cases = self.test_cases or self.create_test_dataset()
        
        print(f"🧪 Starting RAG evaluation with {len(test_cases)} test cases")
        
        results = []
        total_start_time = time.time()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}/{len(test_cases)}: {test_case.category}")
            print(f"Question: {test_case.question}")
            
            # Run single evaluation
            result = await self._evaluate_single_case(rag_system, test_case)
            results.append(result)
            
            # Show quick metrics
            if result.metrics:
                key_metrics = {k: v for k, v in result.metrics.items() 
                              if k in ['context_relevance', 'response_time']}
                print(f"Metrics: {key_metrics}")
        
        total_time = time.time() - total_start_time
        
        # Compile comprehensive results
        evaluation_summary = self._compile_evaluation_results(results, total_time)
        
        print(f"\n🎯 Evaluation Complete!")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average response time: {evaluation_summary['avg_response_time']:.3f}s")
        
        return evaluation_summary
    
    async def _evaluate_single_case(self, rag_system, test_case: TestCase) -> EvaluationResult:
        """Evaluate a single test case"""
        
        start_time = time.time()
        
        try:
            # Query the RAG system
            query_result = rag_system.query_with_analysis(test_case.question)
            
            response_time = time.time() - start_time
            
            if "error" in query_result:
                return EvaluationResult(
                    test_case=test_case,
                    generated_answer="",
                    retrieved_context=[],
                    metrics={"error": 1.0, "response_time": response_time},
                    response_time=response_time
                )
            
            # Calculate evaluation metrics
            metrics = self._calculate_metrics(
                test_case,
                query_result["answer"],
                query_result["context_analysis"],
                response_time
            )
            
            return EvaluationResult(
                test_case=test_case,
                generated_answer=query_result["answer"],
                retrieved_context=query_result.get("context_analysis", {}),
                metrics=metrics,
                response_time=response_time,
                trace_id=query_result.get("trace_id", "")
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            print(f"❌ Evaluation failed: {e}")
            return EvaluationResult(
                test_case=test_case,
                generated_answer="",
                retrieved_context=[],
                metrics={"error": 1.0, "response_time": response_time},
                response_time=response_time
            )
    
    def _calculate_metrics(self, test_case: TestCase, answer: str, 
                          context_analysis: Dict[str, Any], response_time: float) -> Dict[str, float]:
        """Calculate comprehensive evaluation metrics"""
        
        metrics = {
            "response_time": response_time
        }
        
        # Context relevance - based on number of chunks and sources
        if context_analysis:
            num_chunks = context_analysis.get("num_chunks", 0)
            unique_sources = context_analysis.get("unique_sources", 0)
            
            # Simple heuristics for context quality
            metrics["context_relevance"] = min(1.0, num_chunks / 5.0)  # More chunks = better coverage
            metrics["source_diversity"] = min(1.0, unique_sources / 2.0)  # Multiple sources = better
            metrics["context_utilization"] = min(1.0, len(answer) / 200.0)  # Longer answer = better utilization
        
        # Answer quality metrics (simple heuristics)
        if answer:
            # Answer completeness based on length and structure
            metrics["answer_completeness"] = min(1.0, len(answer) / 150.0)
            
            # Answer structure quality
            has_structure = any(marker in answer.lower() for marker in 
                               ["first", "second", "however", "therefore", "additionally"])
            metrics["answer_structure"] = 1.0 if has_structure else 0.5
            
            # Check for hedging language (uncertainty indicators)
            uncertainty_markers = ["might", "could", "possibly", "may", "unclear", "insufficient information"]
            uncertainty_count = sum(1 for marker in uncertainty_markers if marker in answer.lower())
            metrics["answer_confidence"] = max(0.0, 1.0 - (uncertainty_count * 0.2))
        else:
            metrics["answer_completeness"] = 0.0
            metrics["answer_structure"] = 0.0
            metrics["answer_confidence"] = 0.0
        
        # Semantic similarity (if model available)
        if self.evaluation_model and EVAL_MODELS_AVAILABLE and test_case.expected_answer:
            try:
                answer_embedding = self.evaluation_model.encode([answer])
                expected_embedding = self.evaluation_model.encode([test_case.expected_answer])
                similarity = cosine_similarity(answer_embedding, expected_embedding)[0][0]
                metrics["semantic_similarity"] = float(similarity)
            except:
                metrics["semantic_similarity"] = 0.0
        
        # Retrieval precision (if relevant sources specified)
        if test_case.relevant_sources and context_analysis:
            retrieved_sources = set(context_analysis.get("sources", []))
            expected_sources = set(test_case.relevant_sources)
            
            if retrieved_sources:
                precision = len(retrieved_sources & expected_sources) / len(retrieved_sources)
                metrics["retrieval_precision"] = precision
            else:
                metrics["retrieval_precision"] = 0.0
        
        return metrics
    
    def _compile_evaluation_results(self, results: List[EvaluationResult], 
                                   total_time: float) -> Dict[str, Any]:
        """Compile comprehensive evaluation results"""
        
        # Aggregate metrics
        all_metrics = {}
        successful_results = [r for r in results if "error" not in r.metrics]
        
        if not successful_results:
            return {"error": "All test cases failed", "total_time": total_time}
        
        # Calculate average metrics
        for metric_name in EvaluationMetric:
            metric_key = metric_name.value
            values = [r.metrics.get(metric_key, 0) for r in successful_results 
                     if metric_key in r.metrics]
            
            if values:
                all_metrics[metric_key] = {
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0.0
                }
        
        # Category breakdown
        category_performance = {}
        for result in successful_results:
            category = result.test_case.category
            if category not in category_performance:
                category_performance[category] = []
            
            # Use a composite score for category ranking
            composite_score = (
                result.metrics.get("context_relevance", 0) * 0.3 +
                result.metrics.get("answer_completeness", 0) * 0.4 +
                result.metrics.get("answer_confidence", 0) * 0.3
            )
            category_performance[category].append(composite_score)
        
        # Average category scores
        category_averages = {
            category: statistics.mean(scores) 
            for category, scores in category_performance.items()
        }
        
        # Difficulty analysis
        difficulty_performance = {}
        for result in successful_results:
            difficulty = result.test_case.difficulty
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = []
            
            composite_score = (
                result.metrics.get("context_relevance", 0) * 0.3 +
                result.metrics.get("answer_completeness", 0) * 0.4 +
                result.metrics.get("answer_confidence", 0) * 0.3
            )
            difficulty_performance[difficulty].append(composite_score)
        
        difficulty_averages = {
            difficulty: statistics.mean(scores) 
            for difficulty, scores in difficulty_performance.items()
        }
        
        # Overall system score
        overall_score = statistics.mean([
            all_metrics.get("context_relevance", {}).get("average", 0),
            all_metrics.get("answer_completeness", {}).get("average", 0),
            all_metrics.get("answer_confidence", {}).get("average", 0)
        ])
        
        return {
            "overall_score": overall_score,
            "total_test_cases": len(results),
            "successful_cases": len(successful_results),
            "failed_cases": len(results) - len(successful_results),
            "total_evaluation_time": total_time,
            "avg_response_time": statistics.mean([r.response_time for r in results]),
            "detailed_metrics": all_metrics,
            "category_performance": category_averages,
            "difficulty_performance": difficulty_averages,
            "individual_results": [
                {
                    "question": r.test_case.question,
                    "category": r.test_case.category,
                    "difficulty": r.test_case.difficulty,
                    "answer": r.generated_answer[:100] + "..." if len(r.generated_answer) > 100 else r.generated_answer,
                    "key_metrics": {k: v for k, v in r.metrics.items() 
                                   if k in ["context_relevance", "answer_completeness", "response_time"]}
                } for r in results[:5]  # Show first 5 for summary
            ]
        }
    
    def generate_evaluation_report(self, evaluation_results: Dict[str, Any]) -> str:
        """Generate a comprehensive evaluation report"""
        
        report = []
        report.append("RAG System Evaluation Report")
        report.append("=" * 50)
        report.append("")
        
        # Overall performance
        overall_score = evaluation_results.get("overall_score", 0)
        report.append(f"🎯 Overall Performance Score: {overall_score:.3f}/1.000")
        
        # Test case summary
        total = evaluation_results.get("total_test_cases", 0)
        successful = evaluation_results.get("successful_cases", 0)
        failed = evaluation_results.get("failed_cases", 0)
        
        report.append(f"📊 Test Cases: {successful}/{total} successful ({failed} failed)")
        report.append(f"⏱️  Average Response Time: {evaluation_results.get('avg_response_time', 0):.3f}s")
        report.append("")
        
        # Performance by category
        category_perf = evaluation_results.get("category_performance", {})
        if category_perf:
            report.append("📁 Performance by Category:")
            for category, score in sorted(category_perf.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {category}: {score:.3f}")
            report.append("")
        
        # Performance by difficulty
        difficulty_perf = evaluation_results.get("difficulty_performance", {})
        if difficulty_perf:
            report.append("🎚️  Performance by Difficulty:")
            for difficulty in ["easy", "medium", "hard"]:
                if difficulty in difficulty_perf:
                    score = difficulty_perf[difficulty]
                    report.append(f"  {difficulty.title()}: {score:.3f}")
            report.append("")
        
        # Detailed metrics
        detailed = evaluation_results.get("detailed_metrics", {})
        if detailed:
            report.append("📈 Detailed Metrics:")
            for metric, stats in detailed.items():
                if isinstance(stats, dict):
                    avg = stats.get("average", 0)
                    report.append(f"  {metric}: {avg:.3f} (±{stats.get('std', 0):.3f})")
            report.append("")
        
        # Recommendations
        report.append("💡 Recommendations:")
        if overall_score < 0.7:
            report.append("  - Consider improving document chunking strategy")
            report.append("  - Review and expand knowledge base coverage")
            report.append("  - Optimize retrieval parameters for better context selection")
        elif overall_score < 0.85:
            report.append("  - Fine-tune retrieval scoring thresholds")
            report.append("  - Consider ensemble retrieval methods")
            report.append("  - Add more domain-specific evaluation metrics")
        else:
            report.append("  - Excellent performance! Consider A/B testing new features")
            report.append("  - Monitor performance on new document types")
            report.append("  - Implement continuous evaluation pipeline")
        
        return "\\n".join(report)


def demo_rag_evaluation():
    """Demonstrate RAG evaluation framework"""
    
    print("Week 4 RAG Evaluation Framework Demo")
    print("=" * 60)
    
    evaluator = RAGEvaluator()
    
    # Create test dataset
    test_cases = evaluator.create_test_dataset()
    
    print(f"\n📝 Test Dataset Created:")
    print(f"Total cases: {len(test_cases)}")
    
    categories = {}
    difficulties = {}
    
    for case in test_cases:
        categories[case.category] = categories.get(case.category, 0) + 1
        difficulties[case.difficulty] = difficulties.get(case.difficulty, 0) + 1
    
    print(f"Categories: {dict(categories)}")
    print(f"Difficulties: {dict(difficulties)}")
    
    print(f"\n🔍 Sample Test Cases:")
    for i, case in enumerate(test_cases[:3]):
        print(f"{i+1}. [{case.category}] {case.question}")
    
    print(f"\n✅ Evaluation framework ready for RAG system testing")
    print(f"🎯 Features demonstrated:")
    print("  - Comprehensive test case generation")
    print("  - Multiple evaluation metrics (relevance, completeness, confidence)")
    print("  - Category and difficulty-based performance analysis")
    print("  - Automated report generation with recommendations")
    
    # Simulate evaluation results
    print(f"\n📊 Simulated Evaluation Results:")
    simulated_results = {
        "overall_score": 0.78,
        "total_test_cases": len(test_cases),
        "successful_cases": len(test_cases) - 1,
        "failed_cases": 1,
        "avg_response_time": 1.245,
        "category_performance": {
            "factual_lookup": 0.92,
            "legal_penalties": 0.85,
            "comparative_analysis": 0.65,
            "synthesis": 0.61
        },
        "difficulty_performance": {
            "easy": 0.89,
            "medium": 0.78,
            "hard": 0.67
        }
    }
    
    report = evaluator.generate_evaluation_report(simulated_results)
    print("\\n" + report)


if __name__ == "__main__":
    demo_rag_evaluation()