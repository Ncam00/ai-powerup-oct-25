import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

from fastapi import FastAPI, HTTPException
from langchain_experimental.data_anonymizer import PresidioReversibleAnonymizer
from pydantic import BaseModel

app = FastAPI(title="Text Anonymiser Service")

# Configuration
DATA_DIR = Path("./data/mappings")
DATA_DIR.mkdir(parents=True, exist_ok=True)
BATCH_TIMEOUT = 30  # seconds
MAX_WORKERS = 10

# Create the anonymizer once at module level - this prevents model download issues
# We'll manage sessions by storing/restoring the deanonymizer_mapping
anonymizer = PresidioReversibleAnonymizer(
    add_default_faker_operators=False,
    analyzed_fields=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "US_SSN", "DATE_TIME", "IP_ADDRESS", "LOCATION", "ORGANIZATION"]
)

# Global state for sessions
session_mappings: Dict[str, Dict] = {}
session_data: Dict[str, Dict[str, str]] = {}
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)


class SessionData(TypedDict):
    """Session data structure."""
    replacements: Dict[str, str]
    timestamp: str


class AnonymiseRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    specific_names: Optional[List[str]] = None


class AnonymiseBatchRequest(BaseModel):
    texts: List[str]
    session_id: Optional[str] = None
    specific_names: Optional[List[str]] = None


class AnonymiseResponse(BaseModel):
    anonymised_text: str
    session_id: str


class AnonymiseBatchResponse(BaseModel):
    anonymised_texts: List[str]
    session_id: str


class DeanonymiseRequest(BaseModel):
    anonymised_text: str
    session_id: str


class DeanonymiseMatchRequest(BaseModel):
    match_result: dict
    session_id: str


class DeanonymiseResponse(BaseModel):
    original_text: str


def load_session_mapping(session_id: str):
    """Load session mapping from disk or memory."""
    # Check memory first
    if session_id in session_mappings:
        # Can't directly set deanonymizer_mapping, so we update it
        anonymizer.deanonymizer_mapping.clear()
        anonymizer.deanonymizer_mapping.update(session_mappings[session_id])
        return
    
    # Try to load from disk
    mapping_file = DATA_DIR / f"{session_id}.json"
    if mapping_file.exists():
        with open(mapping_file, 'r') as f:
            data = json.load(f)
            session_mappings[session_id] = data.get('deanonymizer_mapping', {})
            session_data[session_id] = data.get('session_data', {})
            anonymizer.deanonymizer_mapping.clear()
            anonymizer.deanonymizer_mapping.update(session_mappings[session_id])
    else:
        # New session
        session_mappings[session_id] = {}
        session_data[session_id] = {}
        anonymizer.reset_deanonymizer_mapping()


def save_session_mapping(session_id: str):
    """Save current anonymizer mapping to session."""
    # Store in memory
    session_mappings[session_id] = anonymizer.deanonymizer_mapping.copy()
    
    # Save to disk
    mapping_file = DATA_DIR / f"{session_id}.json"
    data = {
        'deanonymizer_mapping': session_mappings[session_id],
        'session_data': session_data.get(session_id, {}),
        'timestamp': datetime.utcnow().isoformat()
    }
    with open(mapping_file, 'w') as f:
        json.dump(data, f, indent=2)


def preprocess_text_with_custom_names(text: str, session_id: str, specific_names: Optional[List[str]] = None) -> str:
    """Replace specific names with placeholders before anonymization."""
    if not specific_names:
        return text
        
    processed_text = text
    replacements = session_data.get(session_id, {})
    
    for i, name in enumerate(specific_names):
        if name in text:
            # Handle different variations of the name
            variations = [
                name,  # Full name
                name.split()[0] if ' ' in name else name,  # First word only
                name[:len(name)//2] if len(name) > 4 else name,  # Partial name
                ''.join([word[0].upper() for word in name.split()]) if ' ' in name else name[0].upper()  # Acronym
            ]
            
            placeholder = f"PLACEHOLDER_{i}"
            
            # Replace all variations
            for variation in variations:
                if variation in processed_text and variation:
                    processed_text = processed_text.replace(variation, placeholder)
                    replacements[placeholder] = name
    
    session_data[session_id] = replacements
    return processed_text


def postprocess_text(text: str, session_id: str) -> str:
    """Restore placeholders to original names."""
    processed_text = text
    replacements = session_data.get(session_id, {})
    
    # Restore placeholders
    for placeholder, original in replacements.items():
        processed_text = processed_text.replace(placeholder, original)
    
    return processed_text


def anonymise_single(text: str, session_id: str, specific_names: Optional[List[str]] = None) -> str:
    """Anonymise a single text with session management."""
    # Load session mapping
    load_session_mapping(session_id)
    
    # Preprocess with custom names
    processed_text = preprocess_text_with_custom_names(text, session_id, specific_names)
    
    # Anonymise
    anonymised = anonymizer.anonymize(processed_text)
    
    # Save updated mapping
    save_session_mapping(session_id)
    
    return anonymised


@app.post("/anonymise", response_model=AnonymiseResponse)
async def anonymise(request: AnonymiseRequest):
    """Anonymise a single text."""
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        anonymised_text = anonymise_single(
            request.text, 
            session_id,
            request.specific_names
        )
        
        return AnonymiseResponse(
            anonymised_text=anonymised_text,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/anonymise_batch", response_model=AnonymiseBatchResponse)
async def anonymise_batch(request: AnonymiseBatchRequest):
    """Anonymise multiple texts in batch."""
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Process in parallel with timeout
        futures = []
        for text in request.texts:
            future = executor.submit(
                anonymise_single, 
                text, 
                session_id,
                request.specific_names
            )
            futures.append(future)
        
        anonymised_texts = []
        for future in futures:
            try:
                result = future.result(timeout=BATCH_TIMEOUT)
                anonymised_texts.append(result)
            except TimeoutError:
                raise HTTPException(status_code=504, detail="Batch processing timeout")
        
        return AnonymiseBatchResponse(
            anonymised_texts=anonymised_texts,
            session_id=session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deanonymise", response_model=DeanonymiseResponse)
async def deanonymise(request: DeanonymiseRequest):
    """Restore anonymised text to original."""
    try:
        # Load session mapping
        load_session_mapping(request.session_id)
        
        # Deanonymise
        original_text = anonymizer.deanonymize(request.anonymised_text)
        
        # Postprocess
        original_text = postprocess_text(original_text, request.session_id)
        
        return DeanonymiseResponse(original_text=original_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deanonymise-match", response_model=DeanonymiseResponse)
async def deanonymise_match(request: DeanonymiseMatchRequest):
    """Deanonymise a match result object."""
    try:
        # Load session mapping
        load_session_mapping(request.session_id)
        
        # Extract text from match result - could be in different fields
        anonymised_text = ""
        if "reasoning" in request.match_result:
            anonymised_text = request.match_result["reasoning"]
        elif "question" in request.match_result:
            anonymised_text = request.match_result["question"]
        else:
            anonymised_text = request.match_result.get("text", "")
        
        # Deanonymise
        original_text = anonymizer.deanonymize(anonymised_text)
        
        # Postprocess
        original_text = postprocess_text(original_text, request.session_id)
        
        return DeanonymiseResponse(original_text=original_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Clean up session data."""
    # Remove from memory
    if session_id in session_mappings:
        del session_mappings[session_id]
    if session_id in session_data:
        del session_data[session_id]
    
    # Remove from disk
    mapping_file = DATA_DIR / f"{session_id}.json"
    if mapping_file.exists():
        mapping_file.unlink()
    
    return {"message": f"Session {session_id} deleted"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "active_sessions": len(session_mappings)}