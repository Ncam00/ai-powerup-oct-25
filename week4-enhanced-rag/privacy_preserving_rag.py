"""
Privacy-Preserving RAG System - Week 4 Step 2
Demonstrates how to build RAG systems that respect privacy by anonymizing sensitive data
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import uuid
from datetime import datetime

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class PrivacyPreservingRAG:
    """RAG system with built-in privacy protection through anonymization"""
    
    def __init__(self, anonymizer_url: str = "http://localhost:9000"):
        self.anonymizer_url = anonymizer_url
        self.vectorstore = None
        self.embedding_function = None
        self.session_mappings = {}  # Track anonymization mappings per session
        
        # Initialize embeddings
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize vector store
        self.initialize_vectorstore()
    
    def initialize_vectorstore(self):
        """Initialize the vector database for anonymized documents"""
        try:
            connection_string = "postgresql://postgres:password@localhost:5432/exobrain"
            
            self.vectorstore = PGVector(
                collection_name="privacy_preserved_documents",
                connection_string=connection_string,
                embedding_function=self.embedding_function,
                use_jsonb=True
            )
            print("✅ Privacy-preserving vector store initialized")
        except Exception as e:
            print(f"⚠️ Vector store initialization failed: {e}")
            self.vectorstore = None
    
    def is_anonymizer_available(self) -> bool:
        """Check if the anonymizer service is running"""
        try:
            response = requests.get(f"{self.anonymizer_url}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def anonymize_text(self, text: str, session_id: str = None) -> Tuple[str, str]:
        """Anonymize text using the anonymizer service"""
        if not self.is_anonymizer_available():
            print("⚠️ Anonymizer service not available - using original text")
            return text, session_id or str(uuid.uuid4())
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            response = requests.post(
                f"{self.anonymizer_url}/anonymise",
                json={
                    "text": text,
                    "session_id": session_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                anonymized_text = result.get("anonymised_text", text)
                used_session_id = result.get("session_id", session_id)
                
                print(f"✅ Text anonymized for session {used_session_id}")
                return anonymized_text, used_session_id
            else:
                print(f"⚠️ Anonymization failed: {response.text}")
                return text, session_id
                
        except Exception as e:
            print(f"⚠️ Anonymization error: {e}")
            return text, session_id
    
    def deanonymize_text(self, anonymized_text: str, session_id: str) -> str:
        """Restore original text from anonymized version"""
        if not self.is_anonymizer_available():
            return anonymized_text
        
        try:
            response = requests.post(
                f"{self.anonymizer_url}/deanonymise",
                json={
                    "anonymised_text": anonymized_text,
                    "session_id": session_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("original_text", anonymized_text)
            else:
                print(f"⚠️ Deanonymization failed: {response.text}")
                return anonymized_text
                
        except Exception as e:
            print(f"⚠️ Deanonymization error: {e}")
            return anonymized_text
    
    def process_document_with_privacy(self, file_path: str) -> List[Document]:
        """Process a document with privacy preservation"""
        print(f"📄 Processing document with privacy protection: {file_path}")
        
        # Load document
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        
        documents = loader.load()
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        splits = text_splitter.split_documents(documents)
        
        # Anonymize each chunk
        anonymized_documents = []
        session_id = str(uuid.uuid4())
        
        for i, doc in enumerate(splits):
            anonymized_content, _ = self.anonymize_text(doc.page_content, session_id)
            
            # Create new document with anonymized content
            anonymized_doc = Document(
                page_content=anonymized_content,
                metadata={
                    **doc.metadata,
                    "original_source": doc.metadata.get("source", file_path),
                    "anonymization_session": session_id,
                    "chunk_id": i,
                    "privacy_protected": True,
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            anonymized_documents.append(anonymized_doc)
        
        # Store session mapping
        self.session_mappings[session_id] = {
            "file_path": file_path,
            "chunk_count": len(splits),
            "created_at": datetime.now().isoformat()
        }
        
        print(f"✅ Processed {len(anonymized_documents)} chunks with privacy protection")
        return anonymized_documents
    
    def add_documents_to_vectorstore(self, documents: List[Document]):
        """Add anonymized documents to the vector store"""
        if not self.vectorstore:
            print("⚠️ Vector store not available")
            return
        
        try:
            self.vectorstore.add_documents(documents)
            print(f"✅ Added {len(documents)} anonymized documents to vector store")
        except Exception as e:
            print(f"❌ Failed to add documents: {e}")
    
    def privacy_aware_search(self, query: str, k: int = 3) -> List[Tuple[Document, str]]:
        """Search with privacy awareness - returns both anonymized results and session IDs"""
        if not self.vectorstore:
            return []
        
        # First, anonymize the query to match anonymized content
        query_session_id = str(uuid.uuid4())
        anonymized_query, _ = self.anonymize_text(query, query_session_id)
        
        print(f"🔍 Searching with anonymized query: {anonymized_query[:100]}...")
        
        try:
            # Search in anonymized content
            docs = self.vectorstore.similarity_search(anonymized_query, k=k)
            
            # Return documents with their session IDs for potential deanonymization
            results = []
            for doc in docs:
                session_id = doc.metadata.get("anonymization_session")
                results.append((doc, session_id))
            
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def create_privacy_aware_rag_chain(self, model_name: str = "gemini-pro"):
        """Create a RAG chain that handles privacy appropriately"""
        
        if not os.getenv("GOOGLE_API_KEY"):
            print("⚠️ Google API key not found")
            return None
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
        )
        
        prompt = ChatPromptTemplate.from_template("""
You are a privacy-aware AI assistant. You have access to anonymized documents from a knowledge base.

IMPORTANT PRIVACY GUIDELINES:
1. The provided context contains anonymized data where sensitive information has been replaced with placeholders
2. Do NOT attempt to guess or reveal the original identities behind anonymized data
3. Focus on the factual content and insights while respecting privacy
4. If asked about specific people or organizations mentioned in the context, explain that the data has been anonymized for privacy
5. Provide helpful responses based on the anonymized content

CONTEXT (Privacy-Protected):
{context}

QUESTION: {question}

RESPONSE:""")
        
        def get_privacy_aware_context(inputs):
            """Retrieve context while maintaining privacy awareness"""
            query = inputs["question"]
            
            # Search for relevant anonymized documents
            search_results = self.privacy_aware_search(query, k=3)
            
            if not search_results:
                return {"context": "No relevant information found in the knowledge base.", "question": query}
            
            # Format context from anonymized documents
            context_pieces = []
            for i, (doc, session_id) in enumerate(search_results, 1):
                source = doc.metadata.get("original_source", "Unknown")
                content = doc.page_content
                
                context_pieces.append(f"[Anonymized Source {i}: {Path(source).name}]\\n{content}")
            
            context = "\\n\\n".join(context_pieces)
            
            return {"context": context, "question": query}
        
        # Create the chain
        chain = (
            RunnablePassthrough() |
            get_privacy_aware_context |
            prompt |
            llm |
            StrOutputParser()
        )
        
        return chain

# Example usage and demonstration
def demonstrate_privacy_rag():
    """Demonstrate the privacy-preserving RAG system"""
    print("🔒 Privacy-Preserving RAG System Demo")
    print("=" * 50)
    
    # Initialize the system
    privacy_rag = PrivacyPreservingRAG()
    
    # Check if anonymizer is available
    if privacy_rag.is_anonymizer_available():
        print("✅ Anonymizer service is available")
    else:
        print("⚠️ Anonymizer service not available - demo will use original text")
    
    # Create a sample document with sensitive information
    sample_text = """
    John Smith, CEO of Tech Solutions Inc., announced today that the company will be expanding operations.
    Mr. Smith can be reached at john.smith@techsolutions.com or by phone at (555) 123-4567.
    The company's headquarters at 123 Main Street, New York, NY will serve as the base for the new operations.
    Sarah Johnson, the CTO, will lead the technical aspects of the expansion.
    """
    
    # Save sample document
    sample_file = Path("/tmp/sample_sensitive_doc.txt")
    sample_file.write_text(sample_text)
    
    print(f"\\n📄 Original document content:")
    print(sample_text)
    
    # Process document with privacy protection
    print(f"\\n🔒 Processing document with privacy protection...")
    anonymized_docs = privacy_rag.process_document_with_privacy(str(sample_file))
    
    print(f"\\n📄 Anonymized document content (first chunk):")
    if anonymized_docs:
        print(anonymized_docs[0].page_content)
    
    # Add to vector store
    if anonymized_docs:
        privacy_rag.add_documents_to_vectorstore(anonymized_docs)
    
    # Demonstrate search
    print(f"\\n🔍 Testing privacy-aware search...")
    test_query = "Who is the CEO of the company?"
    results = privacy_rag.privacy_aware_search(test_query)
    
    if results:
        print(f"Found {len(results)} results:")
        for i, (doc, session_id) in enumerate(results, 1):
            print(f"Result {i} (Session: {session_id[:8]}...):")
            print(f"Content: {doc.page_content[:200]}...")
    
    # Create and test RAG chain
    print(f"\\n🤖 Testing privacy-aware RAG chain...")
    chain = privacy_rag.create_privacy_aware_rag_chain()
    
    if chain:
        try:
            response = chain.invoke({"question": "What can you tell me about the company expansion?"})
            print(f"\\nRAG Response:")
            print(response)
        except Exception as e:
            print(f"❌ RAG chain failed: {e}")
    
    # Cleanup
    sample_file.unlink(missing_ok=True)
    
    print(f"\\n✅ Privacy-preserving RAG demonstration complete!")

if __name__ == "__main__":
    demonstrate_privacy_rag()