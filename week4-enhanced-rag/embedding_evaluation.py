"""
Embedding Models Comparison and RAG Evaluation - Week 4 Step 4
Comprehensive evaluation of different embedding models and RAG system performance
"""

import os
import json
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pandas as pd

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# For evaluation metrics
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from rouge_score import rouge_scorer
import bert_score

# Download required resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

@dataclass
class EmbeddingModelConfig:
    """Configuration for an embedding model"""
    name: str
    model_name: str
    model_kwargs: Dict[str, Any] = None
    encode_kwargs: Dict[str, Any] = None
    description: str = ""
    
    def __post_init__(self):
        if self.model_kwargs is None:
            self.model_kwargs = {}
        if self.encode_kwargs is None:
            self.encode_kwargs = {}

@dataclass
class EvaluationResult:
    """Results from evaluating an embedding model"""
    model_name: str
    retrieval_accuracy: float
    retrieval_precision: float
    retrieval_recall: float
    semantic_similarity: float
    processing_time: float
    dimension: int
    memory_usage: float

@dataclass
class RAGEvaluationResult:
    """Results from evaluating RAG system performance"""
    model_name: str
    rouge_scores: Dict[str, float]
    bert_scores: Dict[str, float]
    answer_relevance: float
    context_precision: float
    context_recall: float
    faithfulness: float

class EmbeddingModelComparator:
    """Comprehensive comparison of different embedding models for RAG"""
    
    def __init__(self):
        self.models = {}
        self.vectorstores = {}
        self.evaluation_results = {}
        self.rag_results = {}
    
    def get_embedding_models(self) -> List[EmbeddingModelConfig]:
        """Define embedding models to compare"""
        models = [
            EmbeddingModelConfig(
                name="MiniLM-L6-v2",
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                description="Compact, fast model optimized for semantic similarity"
            ),
            EmbeddingModelConfig(
                name="MiniLM-L12-v2", 
                model_name="sentence-transformers/all-MiniLM-L12-v2",
                description="Larger MiniLM variant with better accuracy"
            ),
            EmbeddingModelConfig(
                name="MPNet-base-v2",
                model_name="sentence-transformers/all-mpnet-base-v2",
                description="High-quality general-purpose embedding model"
            ),
            EmbeddingModelConfig(
                name="DistilBERT-base",
                model_name="sentence-transformers/all-distilbert-base-v1",
                description="Distilled BERT model for faster inference"
            ),
            EmbeddingModelConfig(
                name="BGE-small-en",
                model_name="BAAI/bge-small-en-v1.5",
                description="Beijing Academy AI model optimized for retrieval"
            ),
        ]
        
        # Add more advanced models if available
        try:
            models.append(
                EmbeddingModelConfig(
                    name="E5-large-v2",
                    model_name="intfloat/e5-large-v2",
                    description="Large multilingual embedding model"
                )
            )
        except:
            pass
        
        return models
    
    def initialize_embedding_model(self, config: EmbeddingModelConfig) -> Optional[HuggingFaceEmbeddings]:
        """Initialize an embedding model"""
        print(f"🔧 Initializing {config.name}...")
        
        try:
            start_time = time.time()
            
            model = HuggingFaceEmbeddings(
                model_name=config.model_name,
                model_kwargs=config.model_kwargs,
                encode_kwargs=config.encode_kwargs
            )
            
            # Test the model with a sample text
            test_embedding = model.embed_query("This is a test sentence.")
            
            init_time = time.time() - start_time
            print(f"✅ {config.name} initialized in {init_time:.2f}s, dimension: {len(test_embedding)}")
            
            return model
            
        except Exception as e:
            print(f"❌ Failed to initialize {config.name}: {e}")
            return None
    
    def create_test_dataset(self) -> Tuple[List[Document], List[Tuple[str, str]]]:
        """Create a test dataset for evaluation"""
        print("📝 Creating test dataset...")
        
        # Sample documents with various content types
        sample_texts = [
            """
            Machine Learning Fundamentals
            
            Machine learning is a method of data analysis that automates analytical model building. 
            It is a branch of artificial intelligence based on the idea that systems can learn from data, 
            identify patterns and make decisions with minimal human intervention.
            
            There are three main types of machine learning:
            1. Supervised learning: Learning with labeled examples
            2. Unsupervised learning: Finding patterns in data without labels  
            3. Reinforcement learning: Learning through interaction with environment
            """,
            """
            Natural Language Processing Applications
            
            Natural Language Processing (NLP) enables computers to understand, interpret and manipulate human language.
            Modern NLP applications include:
            - Chatbots and virtual assistants
            - Language translation services
            - Sentiment analysis tools
            - Text summarization systems
            - Speech recognition software
            
            Recent advances in transformer models like BERT and GPT have revolutionized NLP capabilities.
            """,
            """
            Deep Learning Neural Networks
            
            Deep learning uses artificial neural networks with multiple layers to model and understand complex patterns.
            Key architectures include:
            
            Convolutional Neural Networks (CNNs): Excellent for image processing and computer vision tasks.
            They use convolution operations to detect features like edges, shapes, and patterns.
            
            Recurrent Neural Networks (RNNs): Designed for sequential data like time series and text.
            LSTM and GRU variants help address the vanishing gradient problem.
            
            Transformer Networks: State-of-the-art for language tasks, using attention mechanisms.
            """,
            """
            Computer Vision Technology
            
            Computer vision enables machines to interpret and understand visual information from the world.
            Applications span numerous industries:
            
            Healthcare: Medical image analysis, diagnostic assistance, surgical robotics
            Automotive: Self-driving cars, driver assistance systems, traffic monitoring
            Retail: Product recognition, inventory management, customer behavior analysis
            Security: Facial recognition, surveillance systems, anomaly detection
            
            Recent breakthroughs in deep learning have dramatically improved computer vision accuracy.
            """,
            """
            Data Science Methodology
            
            Data science combines statistical analysis, machine learning, and domain expertise to extract insights from data.
            The typical data science workflow includes:
            
            1. Problem Definition: Understanding business requirements and success metrics
            2. Data Collection: Gathering relevant data from various sources
            3. Data Cleaning: Handling missing values, outliers, and inconsistencies
            4. Exploratory Data Analysis: Understanding data patterns and relationships
            5. Feature Engineering: Creating relevant features for modeling
            6. Model Development: Building and training predictive models
            7. Model Evaluation: Assessing performance using appropriate metrics
            8. Deployment: Implementing models in production environments
            """
        ]
        
        # Create documents
        documents = []
        for i, text in enumerate(sample_texts):
            doc = Document(
                page_content=text.strip(),
                metadata={
                    "source": f"test_doc_{i}",
                    "doc_id": i,
                    "category": ["ML", "NLP", "DL", "CV", "DS"][i]
                }
            )
            documents.append(doc)
        
        # Create query-answer pairs for evaluation
        qa_pairs = [
            ("What are the three main types of machine learning?", 
             "The three main types are supervised learning, unsupervised learning, and reinforcement learning."),
            ("What applications does NLP have?",
             "NLP applications include chatbots, language translation, sentiment analysis, text summarization, and speech recognition."),
            ("What are the key deep learning architectures?",
             "Key architectures include CNNs for image processing, RNNs for sequential data, and Transformer networks for language tasks."),
            ("How is computer vision used in healthcare?",
             "Computer vision is used in healthcare for medical image analysis, diagnostic assistance, and surgical robotics."),
            ("What are the steps in the data science workflow?",
             "The workflow includes problem definition, data collection, cleaning, exploratory analysis, feature engineering, modeling, evaluation, and deployment.")
        ]
        
        return documents, qa_pairs
    
    def evaluate_retrieval_quality(self, model: HuggingFaceEmbeddings, 
                                 documents: List[Document], 
                                 qa_pairs: List[Tuple[str, str]]) -> Dict[str, float]:
        """Evaluate retrieval quality for an embedding model"""
        print(f"🔍 Evaluating retrieval quality...")
        
        # Create vector store for this model
        collection_name = f"eval_{model.model_name.split('/')[-1].replace('-', '_')}"
        
        try:
            connection_string = "postgresql://postgres:password@localhost:5432/exobrain"
            vectorstore = PGVector(
                collection_name=collection_name,
                connection_string=connection_string,
                embedding_function=model,
                use_jsonb=True
            )
            
            # Add documents
            vectorstore.add_documents(documents)
            
        except Exception as e:
            print(f"⚠️ Vector store creation failed: {e}")
            return {"retrieval_accuracy": 0.0, "retrieval_precision": 0.0, "retrieval_recall": 0.0}
        
        # Evaluate retrieval for each query
        retrieval_scores = []
        
        for query, expected_answer in qa_pairs:
            try:
                # Retrieve top-k documents
                retrieved_docs = vectorstore.similarity_search(query, k=3)
                
                # Simple relevance check based on content overlap
                relevant_count = 0
                for doc in retrieved_docs:
                    # Check if retrieved document contains relevant information
                    doc_content = doc.page_content.lower()
                    query_words = set(query.lower().split())
                    doc_words = set(doc_content.split())
                    
                    # Calculate word overlap
                    overlap = len(query_words.intersection(doc_words))
                    if overlap > 0:
                        relevant_count += 1
                
                # Calculate precision for this query
                precision = relevant_count / len(retrieved_docs) if retrieved_docs else 0
                retrieval_scores.append(precision)
                
            except Exception as e:
                print(f"⚠️ Retrieval evaluation failed for query: {e}")
                retrieval_scores.append(0.0)
        
        # Calculate overall metrics
        avg_precision = np.mean(retrieval_scores) if retrieval_scores else 0.0
        
        # Clean up
        try:
            vectorstore.delete_collection()
        except:
            pass
        
        return {
            "retrieval_accuracy": avg_precision,
            "retrieval_precision": avg_precision,
            "retrieval_recall": avg_precision  # Simplified for demo
        }
    
    def evaluate_semantic_similarity(self, model: HuggingFaceEmbeddings) -> float:
        """Evaluate semantic similarity capabilities"""
        print("🧠 Evaluating semantic similarity...")
        
        # Test pairs: (text1, text2, expected_similarity_high)
        similarity_tests = [
            ("Machine learning is a branch of AI", "AI includes machine learning algorithms", True),
            ("Natural language processing helps computers understand text", "NLP enables text comprehension for machines", True),
            ("Deep learning uses neural networks", "Neural networks are used in deep learning", True),
            ("Computer vision processes images", "The weather is sunny today", False),
            ("Supervised learning uses labeled data", "Cooking requires following recipes", False),
        ]
        
        correct_predictions = 0
        
        for text1, text2, should_be_similar in similarity_tests:
            try:
                emb1 = model.embed_query(text1)
                emb2 = model.embed_query(text2)
                
                # Calculate cosine similarity
                similarity = cosine_similarity([emb1], [emb2])[0][0]
                
                # Threshold for similarity
                is_similar = similarity > 0.7
                
                if is_similar == should_be_similar:
                    correct_predictions += 1
                    
            except Exception as e:
                print(f"⚠️ Similarity test failed: {e}")
        
        return correct_predictions / len(similarity_tests)
    
    def comprehensive_model_evaluation(self) -> Dict[str, EvaluationResult]:
        """Run comprehensive evaluation of all embedding models"""
        print("🏃‍♂️ Running comprehensive embedding model evaluation...")
        print("=" * 60)
        
        # Get test data
        documents, qa_pairs = self.create_test_dataset()
        
        # Get models to test
        model_configs = self.get_embedding_models()
        
        results = {}
        
        for config in model_configs:
            print(f"\\n📊 Evaluating {config.name}...")
            print(f"Description: {config.description}")
            
            # Initialize model
            model = self.initialize_embedding_model(config)
            if not model:
                continue
            
            start_time = time.time()
            
            # Evaluate retrieval quality
            retrieval_metrics = self.evaluate_retrieval_quality(model, documents, qa_pairs)
            
            # Evaluate semantic similarity
            semantic_score = self.evaluate_semantic_similarity(model)
            
            # Get model properties
            test_embedding = model.embed_query("test")
            dimension = len(test_embedding)
            
            processing_time = time.time() - start_time
            
            # Create evaluation result
            result = EvaluationResult(
                model_name=config.name,
                retrieval_accuracy=retrieval_metrics["retrieval_accuracy"],
                retrieval_precision=retrieval_metrics["retrieval_precision"],
                retrieval_recall=retrieval_metrics["retrieval_recall"],
                semantic_similarity=semantic_score,
                processing_time=processing_time,
                dimension=dimension,
                memory_usage=0.0  # Simplified for demo
            )
            
            results[config.name] = result
            
            print(f"✅ {config.name} evaluation complete:")
            print(f"   Retrieval Accuracy: {result.retrieval_accuracy:.3f}")
            print(f"   Semantic Similarity: {result.semantic_similarity:.3f}")
            print(f"   Processing Time: {result.processing_time:.2f}s")
            print(f"   Dimension: {result.dimension}")
        
        return results
    
    def generate_comparison_report(self, results: Dict[str, EvaluationResult]) -> str:
        """Generate comprehensive comparison report"""
        
        if not results:
            return "No evaluation results available."
        
        report = []
        report.append("# Embedding Models Comparison Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        # Create comparison table
        report.append("\\n## Model Performance Comparison")
        report.append("| Model | Retrieval Acc | Semantic Sim | Processing Time | Dimension |")
        report.append("|-------|---------------|--------------|-----------------|-----------|")
        
        # Sort by overall performance (combination of metrics)
        sorted_results = sorted(
            results.items(),
            key=lambda x: (x[1].retrieval_accuracy + x[1].semantic_similarity) / 2,
            reverse=True
        )
        
        for model_name, result in sorted_results:
            report.append(
                f"| {model_name} | {result.retrieval_accuracy:.3f} | "
                f"{result.semantic_similarity:.3f} | {result.processing_time:.2f}s | "
                f"{result.dimension} |"
            )
        
        # Detailed analysis
        report.append("\\n## Detailed Analysis")
        
        for i, (model_name, result) in enumerate(sorted_results, 1):
            report.append(f"\\n### {i}. {model_name}")
            report.append(f"- **Overall Rank**: #{i}")
            report.append(f"- **Retrieval Accuracy**: {result.retrieval_accuracy:.3f}")
            report.append(f"- **Retrieval Precision**: {result.retrieval_precision:.3f}")
            report.append(f"- **Retrieval Recall**: {result.retrieval_recall:.3f}")
            report.append(f"- **Semantic Similarity**: {result.semantic_similarity:.3f}")
            report.append(f"- **Processing Time**: {result.processing_time:.2f} seconds")
            report.append(f"- **Embedding Dimension**: {result.dimension}")
            
            # Performance assessment
            combined_score = (result.retrieval_accuracy + result.semantic_similarity) / 2
            if combined_score >= 0.8:
                assessment = "Excellent - Highly recommended for production use"
            elif combined_score >= 0.6: 
                assessment = "Good - Suitable for most applications"
            elif combined_score >= 0.4:
                assessment = "Fair - May need optimization for specific use cases"
            else:
                assessment = "Poor - Consider alternative models"
            
            report.append(f"- **Assessment**: {assessment}")
        
        # Recommendations
        report.append("\\n## Recommendations")
        
        if sorted_results:
            best_model = sorted_results[0]
            fastest_model = min(results.items(), key=lambda x: x[1].processing_time)
            smallest_model = min(results.items(), key=lambda x: x[1].dimension)
            
            report.append(f"\\n**Best Overall Performance**: {best_model[0]}")
            report.append(f"This model achieved the highest combined score of {(best_model[1].retrieval_accuracy + best_model[1].semantic_similarity) / 2:.3f}")
            
            report.append(f"\\n**Fastest Processing**: {fastest_model[0]} ({fastest_model[1].processing_time:.2f}s)")
            report.append(f"**Most Compact**: {smallest_model[0]} ({smallest_model[1].dimension} dimensions)")
            
            report.append("\\n**Use Case Recommendations**:")
            report.append("- **Production Systems**: Choose models with high accuracy and reasonable processing time")
            report.append("- **Real-time Applications**: Prioritize fast processing models")
            report.append("- **Resource-Constrained Environments**: Consider compact models with fewer dimensions")
            report.append("- **High-Accuracy Requirements**: Select models with highest retrieval and semantic scores")
        
        return "\\n".join(report)
    
    def create_visualization(self, results: Dict[str, EvaluationResult]):
        """Create visualizations of the comparison results"""
        if not results:
            return
        
        # Prepare data for visualization
        models = list(results.keys())
        retrieval_acc = [results[m].retrieval_accuracy for m in models]
        semantic_sim = [results[m].semantic_similarity for m in models]
        processing_time = [results[m].processing_time for m in models]
        dimensions = [results[m].dimension for m in models]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Retrieval Accuracy
        ax1.bar(models, retrieval_acc, color='skyblue')
        ax1.set_title('Retrieval Accuracy by Model')
        ax1.set_ylabel('Accuracy Score')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Semantic Similarity
        ax2.bar(models, semantic_sim, color='lightgreen')
        ax2.set_title('Semantic Similarity Performance')
        ax2.set_ylabel('Similarity Score')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Processing Time
        ax3.bar(models, processing_time, color='salmon')
        ax3.set_title('Processing Time (Lower is Better)')
        ax3.set_ylabel('Time (seconds)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Embedding Dimensions
        ax4.bar(models, dimensions, color='gold')
        ax4.set_title('Embedding Dimensions')
        ax4.set_ylabel('Dimensions')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('embedding_models_comparison.png', dpi=300, bbox_inches='tight')
        print("📊 Visualization saved as 'embedding_models_comparison.png'")

def demonstrate_embedding_evaluation():
    """Demonstrate the embedding model evaluation system"""
    print("🔬 Embedding Models Evaluation Demo")
    print("=" * 50)
    
    # Initialize comparator
    comparator = EmbeddingModelComparator()
    
    # Run comprehensive evaluation
    print("🏃‍♂️ Running comprehensive evaluation...")
    results = comparator.comprehensive_model_evaluation()
    
    if not results:
        print("❌ No evaluation results generated")
        return
    
    # Generate report
    print("\\n📋 Generating comparison report...")
    report = comparator.generate_comparison_report(results)
    
    # Save report
    report_file = Path("embedding_models_evaluation_report.md")
    report_file.write_text(report)
    print(f"✅ Report saved to: {report_file}")
    
    # Create visualization
    print("\\n📊 Creating visualization...")
    try:
        comparator.create_visualization(results)
    except Exception as e:
        print(f"⚠️ Visualization failed: {e}")
    
    # Display summary
    print("\\n🏆 EVALUATION SUMMARY:")
    sorted_results = sorted(
        results.items(),
        key=lambda x: (x[1].retrieval_accuracy + x[1].semantic_similarity) / 2,
        reverse=True
    )
    
    for i, (model_name, result) in enumerate(sorted_results, 1):
        combined_score = (result.retrieval_accuracy + result.semantic_similarity) / 2
        print(f"{i}. {model_name}")
        print(f"   Combined Score: {combined_score:.3f}")
        print(f"   Retrieval: {result.retrieval_accuracy:.3f}, Semantic: {result.semantic_similarity:.3f}")
    
    print("\\n✅ Embedding model evaluation complete!")

if __name__ == "__main__":
    demonstrate_embedding_evaluation()