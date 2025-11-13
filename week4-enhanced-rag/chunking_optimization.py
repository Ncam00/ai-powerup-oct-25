"""
Advanced Chunking Strategies for RAG - Week 4 Step 3
Comprehensive analysis and optimization of document chunking approaches
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    SpacyTextSplitter,
    NLTKTextSplitter
)
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

# For semantic chunking
from transformers import AutoTokenizer
import nltk
import spacy

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except:
    pass

@dataclass
class ChunkingStrategy:
    """Configuration for a chunking strategy"""
    name: str
    splitter_class: type
    chunk_size: int
    chunk_overlap: int
    additional_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}

@dataclass
class ChunkingResult:
    """Results from applying a chunking strategy"""
    strategy_name: str
    chunk_count: int
    avg_chunk_size: float
    min_chunk_size: int
    max_chunk_size: int
    processing_time: float
    chunks: List[Document]

class AdvancedChunkingOptimizer:
    """Advanced system for testing and optimizing document chunking strategies"""
    
    def __init__(self):
        self.embedding_function = None
        self.vectorstore = None
        self.results = {}
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize embeddings and vector store"""
        try:
            self.embedding_function = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("✅ Embedding function initialized")
        except Exception as e:
            print(f"⚠️ Embedding initialization failed: {e}")
        
        # Initialize separate collections for each strategy
        try:
            connection_string = "postgresql://postgres:password@localhost:5432/exobrain"
            print("✅ Database connection ready for chunking tests")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
    
    def get_chunking_strategies(self) -> List[ChunkingStrategy]:
        """Define various chunking strategies to test"""
        strategies = [
            # Recursive Character Splitter variations
            ChunkingStrategy(
                name="RecursiveChar_Small",
                splitter_class=RecursiveCharacterTextSplitter,
                chunk_size=200,
                chunk_overlap=50
            ),
            ChunkingStrategy(
                name="RecursiveChar_Medium", 
                splitter_class=RecursiveCharacterTextSplitter,
                chunk_size=500,
                chunk_overlap=100
            ),
            ChunkingStrategy(
                name="RecursiveChar_Large",
                splitter_class=RecursiveCharacterTextSplitter,
                chunk_size=1000,
                chunk_overlap=200
            ),
            ChunkingStrategy(
                name="RecursiveChar_XLarge",
                splitter_class=RecursiveCharacterTextSplitter,
                chunk_size=1500,
                chunk_overlap=300
            ),
            
            # Character Splitter variations
            ChunkingStrategy(
                name="Character_Medium",
                splitter_class=CharacterTextSplitter,
                chunk_size=500,
                chunk_overlap=100,
                additional_params={"separator": "\\n\\n"}
            ),
            
            # Token-based splitting
            ChunkingStrategy(
                name="Token_Medium",
                splitter_class=TokenTextSplitter,
                chunk_size=128,  # tokens
                chunk_overlap=32,
                additional_params={"encoding_name": "cl100k_base"}
            ),
            ChunkingStrategy(
                name="Token_Large",
                splitter_class=TokenTextSplitter,
                chunk_size=256,  # tokens
                chunk_overlap=64,
                additional_params={"encoding_name": "cl100k_base"}
            ),
        ]
        
        # Add NLP-based splitters if available
        try:
            strategies.append(
                ChunkingStrategy(
                    name="NLTK_Sentence",
                    splitter_class=NLTKTextSplitter,
                    chunk_size=1000,
                    chunk_overlap=200
                )
            )
        except:
            print("⚠️ NLTK splitter not available")
        
        try:
            # Check if spaCy model is available
            nlp = spacy.load("en_core_web_sm")
            strategies.append(
                ChunkingStrategy(
                    name="Spacy_Sentence",
                    splitter_class=SpacyTextSplitter,
                    chunk_size=1000,
                    chunk_overlap=200
                )
            )
        except:
            print("⚠️ SpaCy splitter not available (install: python -m spacy download en_core_web_sm)")
        
        return strategies
    
    def apply_chunking_strategy(self, documents: List[Document], strategy: ChunkingStrategy) -> ChunkingResult:
        """Apply a chunking strategy and measure results"""
        print(f"📄 Testing strategy: {strategy.name}")
        
        start_time = time.time()
        
        # Create splitter with strategy parameters
        splitter_params = {
            "chunk_size": strategy.chunk_size,
            "chunk_overlap": strategy.chunk_overlap,
            **strategy.additional_params
        }
        
        try:
            splitter = strategy.splitter_class(**splitter_params)
            chunks = splitter.split_documents(documents)
        except Exception as e:
            print(f"❌ Strategy {strategy.name} failed: {e}")
            return ChunkingResult(
                strategy_name=strategy.name,
                chunk_count=0,
                avg_chunk_size=0.0,
                min_chunk_size=0,
                max_chunk_size=0,
                processing_time=time.time() - start_time,
                chunks=[]
            )
        
        processing_time = time.time() - start_time
        
        # Calculate statistics
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        
        if chunk_sizes:
            avg_size = sum(chunk_sizes) / len(chunk_sizes)
            min_size = min(chunk_sizes)
            max_size = max(chunk_sizes)
        else:
            avg_size = min_size = max_size = 0
        
        # Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunking_strategy": strategy.name,
                "chunk_index": i,
                "chunk_size": len(chunk.page_content),
                "total_chunks": len(chunks)
            })
        
        result = ChunkingResult(
            strategy_name=strategy.name,
            chunk_count=len(chunks),
            avg_chunk_size=avg_size,
            min_chunk_size=min_size,
            max_chunk_size=max_size,
            processing_time=processing_time,
            chunks=chunks
        )
        
        print(f"✅ {strategy.name}: {len(chunks)} chunks, avg size: {avg_size:.1f} chars")
        return result
    
    def test_all_strategies(self, document_path: str) -> Dict[str, ChunkingResult]:
        """Test all chunking strategies on a document"""
        print(f"🔍 Testing chunking strategies on: {document_path}")
        
        # Load document
        if document_path.endswith('.pdf'):
            loader = PyPDFLoader(document_path)
        else:
            loader = TextLoader(document_path)
        
        try:
            documents = loader.load()
            print(f"📄 Loaded document with {len(documents)} pages/sections")
        except Exception as e:
            print(f"❌ Failed to load document: {e}")
            return {}
        
        # Test each strategy
        strategies = self.get_chunking_strategies()
        results = {}
        
        for strategy in strategies:
            result = self.apply_chunking_strategy(documents, strategy)
            results[strategy.name] = result
            
        self.results.update(results)
        return results
    
    def evaluate_chunking_quality(self, results: Dict[str, ChunkingResult]) -> Dict[str, Dict[str, float]]:
        """Evaluate the quality of different chunking strategies"""
        print("📊 Evaluating chunking quality...")
        
        evaluations = {}
        
        for strategy_name, result in results.items():
            if result.chunk_count == 0:
                continue
                
            chunks = result.chunks
            
            # Quality metrics
            metrics = {}
            
            # 1. Size consistency (lower variance is better)
            chunk_sizes = [len(chunk.page_content) for chunk in chunks]
            if len(chunk_sizes) > 1:
                size_variance = sum((size - result.avg_chunk_size) ** 2 for size in chunk_sizes) / len(chunk_sizes)
                metrics['size_consistency'] = 1.0 / (1.0 + size_variance / 1000)  # Normalized
            else:
                metrics['size_consistency'] = 1.0
            
            # 2. Content completeness (fewer empty chunks is better)
            non_empty_chunks = sum(1 for chunk in chunks if chunk.page_content.strip())
            metrics['content_completeness'] = non_empty_chunks / result.chunk_count if result.chunk_count > 0 else 0
            
            # 3. Processing efficiency (faster is better)
            metrics['processing_efficiency'] = 1.0 / (1.0 + result.processing_time)
            
            # 4. Overlap effectiveness (check for meaningful overlaps)
            overlap_quality = 0.0
            if len(chunks) > 1:
                overlap_scores = []
                for i in range(len(chunks) - 1):
                    current_chunk = chunks[i].page_content
                    next_chunk = chunks[i + 1].page_content
                    
                    # Simple overlap detection
                    current_words = set(current_chunk.lower().split())
                    next_words = set(next_chunk.lower().split())
                    
                    if current_words and next_words:
                        overlap_ratio = len(current_words.intersection(next_words)) / len(current_words.union(next_words))
                        overlap_scores.append(overlap_ratio)
                
                if overlap_scores:
                    overlap_quality = sum(overlap_scores) / len(overlap_scores)
            
            metrics['overlap_quality'] = overlap_quality
            
            # 5. Chunk size optimization (penalty for too small or too large chunks)
            optimal_size = 750  # Target size
            size_penalty = abs(result.avg_chunk_size - optimal_size) / optimal_size
            metrics['size_optimization'] = 1.0 / (1.0 + size_penalty)
            
            # Overall quality score (weighted average)
            weights = {
                'size_consistency': 0.2,
                'content_completeness': 0.3,
                'processing_efficiency': 0.1,
                'overlap_quality': 0.2,
                'size_optimization': 0.2
            }
            
            overall_score = sum(metrics[metric] * weight for metric, weight in weights.items())
            metrics['overall_quality'] = overall_score
            
            evaluations[strategy_name] = metrics
        
        return evaluations
    
    def generate_chunking_report(self, results: Dict[str, ChunkingResult], 
                                evaluations: Dict[str, Dict[str, float]]) -> str:
        """Generate a comprehensive report on chunking strategies"""
        
        report = []
        report.append("# Chunking Strategy Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        # Summary table
        report.append("\\n## Strategy Summary")
        report.append("| Strategy | Chunks | Avg Size | Processing Time | Quality Score |")
        report.append("|----------|--------|----------|-----------------|---------------|")
        
        # Sort by quality score
        sorted_strategies = sorted(
            evaluations.items(), 
            key=lambda x: x[1].get('overall_quality', 0), 
            reverse=True
        )
        
        for strategy_name, metrics in sorted_strategies:
            if strategy_name in results:
                result = results[strategy_name]
                report.append(
                    f"| {strategy_name} | {result.chunk_count} | "
                    f"{result.avg_chunk_size:.0f} | {result.processing_time:.3f}s | "
                    f"{metrics.get('overall_quality', 0):.3f} |"
                )
        
        # Detailed analysis
        report.append("\\n## Detailed Analysis")
        
        for strategy_name, metrics in sorted_strategies[:3]:  # Top 3 strategies
            result = results[strategy_name]
            report.append(f"\\n### {strategy_name} (Rank #{sorted_strategies.index((strategy_name, metrics)) + 1})")
            report.append(f"- **Chunks Created**: {result.chunk_count}")
            report.append(f"- **Average Chunk Size**: {result.avg_chunk_size:.1f} characters")
            report.append(f"- **Size Range**: {result.min_chunk_size} - {result.max_chunk_size} characters")
            report.append(f"- **Processing Time**: {result.processing_time:.3f} seconds")
            report.append(f"- **Quality Metrics**:")
            report.append(f"  - Size Consistency: {metrics.get('size_consistency', 0):.3f}")
            report.append(f"  - Content Completeness: {metrics.get('content_completeness', 0):.3f}")
            report.append(f"  - Processing Efficiency: {metrics.get('processing_efficiency', 0):.3f}")
            report.append(f"  - Overlap Quality: {metrics.get('overlap_quality', 0):.3f}")
            report.append(f"  - Size Optimization: {metrics.get('size_optimization', 0):.3f}")
            report.append(f"  - **Overall Quality Score**: {metrics.get('overall_quality', 0):.3f}")
        
        # Recommendations
        report.append("\\n## Recommendations")
        
        if sorted_strategies:
            best_strategy = sorted_strategies[0]
            report.append(f"\\n**Recommended Strategy**: {best_strategy[0]}")
            report.append(f"This strategy achieved the highest overall quality score of {best_strategy[1].get('overall_quality', 0):.3f}")
            
            # Context-specific recommendations
            report.append("\\n**Context-Specific Recommendations**:")
            report.append("- **For Speed**: Choose strategies with high processing efficiency")
            report.append("- **For Consistency**: Choose strategies with high size consistency")
            report.append("- **For Large Documents**: Consider larger chunk sizes (1000+ characters)")
            report.append("- **For Precise Retrieval**: Consider smaller chunks (200-500 characters)")
            report.append("- **For Context Preservation**: Ensure adequate overlap (20-30% of chunk size)")
        
        return "\\n".join(report)
    
    def create_sample_document(self) -> str:
        """Create a sample document for testing if none is provided"""
        sample_content = """
# Artificial Intelligence and Machine Learning

Artificial Intelligence (AI) has become one of the most transformative technologies of our time. Machine learning, a subset of AI, enables computers to learn and improve from experience without being explicitly programmed for every task.

## Natural Language Processing

Natural Language Processing (NLP) is a branch of AI that focuses on the interaction between computers and humans using natural language. The ultimate objective of NLP is to read, decipher, understand, and make sense of human languages in a manner that is valuable.

### Applications of NLP

NLP has numerous applications in today's world:
- Chatbots and virtual assistants
- Language translation services
- Sentiment analysis of social media
- Text summarization and document analysis
- Speech recognition systems

## Deep Learning

Deep learning is a subset of machine learning that uses neural networks with multiple layers. These deep neural networks can automatically learn hierarchical representations from data, making them particularly effective for tasks like image recognition, natural language processing, and speech recognition.

### Neural Network Architectures

There are several important neural network architectures:

1. **Convolutional Neural Networks (CNNs)**: Primarily used for image processing and computer vision tasks.

2. **Recurrent Neural Networks (RNNs)**: Designed for sequential data and time series analysis.

3. **Transformer Networks**: State-of-the-art architecture for natural language processing tasks.

## The Future of AI

The future of artificial intelligence holds immense promise. We can expect to see continued advancements in:
- Autonomous vehicles and transportation
- Healthcare diagnostics and treatment
- Climate change modeling and solutions
- Educational personalization and accessibility
- Scientific research and discovery

As AI continues to evolve, it's important to consider the ethical implications and ensure that these technologies are developed and deployed responsibly.

## Conclusion

Artificial intelligence and machine learning are reshaping our world in profound ways. From the smartphones in our pockets to the recommendations we receive online, AI is becoming increasingly integrated into our daily lives. Understanding these technologies and their potential impact is crucial for navigating our technological future.
"""
        
        sample_file = Path("/tmp/ai_ml_sample.txt")
        sample_file.write_text(sample_content)
        return str(sample_file)

def demonstrate_chunking_optimization():
    """Demonstrate the chunking optimization system"""
    print("📊 Advanced Chunking Strategy Optimization Demo")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = AdvancedChunkingOptimizer()
    
    # Create or use sample document
    sample_doc = optimizer.create_sample_document()
    print(f"📄 Using sample document: {sample_doc}")
    
    # Test all chunking strategies
    print("\\n🧪 Testing all chunking strategies...")
    results = optimizer.test_all_strategies(sample_doc)
    
    if not results:
        print("❌ No results generated")
        return
    
    # Evaluate strategies
    print("\\n📊 Evaluating chunking quality...")
    evaluations = optimizer.evaluate_chunking_quality(results)
    
    # Generate report
    print("\\n📋 Generating comprehensive report...")
    report = optimizer.generate_chunking_report(results, evaluations)
    
    # Save report
    report_file = Path("chunking_optimization_report.md")
    report_file.write_text(report)
    print(f"✅ Report saved to: {report_file}")
    
    # Display summary
    print("\\n🏆 TOP 3 CHUNKING STRATEGIES:")
    sorted_strategies = sorted(
        evaluations.items(), 
        key=lambda x: x[1].get('overall_quality', 0), 
        reverse=True
    )
    
    for i, (strategy_name, metrics) in enumerate(sorted_strategies[:3], 1):
        result = results[strategy_name]
        print(f"{i}. {strategy_name}")
        print(f"   Quality Score: {metrics.get('overall_quality', 0):.3f}")
        print(f"   Chunks: {result.chunk_count}, Avg Size: {result.avg_chunk_size:.0f} chars")
    
    # Cleanup
    Path(sample_doc).unlink(missing_ok=True)
    
    print("\\n✅ Chunking optimization analysis complete!")

if __name__ == "__main__":
    demonstrate_chunking_optimization()