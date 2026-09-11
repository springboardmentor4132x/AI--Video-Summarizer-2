import os
from sqlalchemy.orm import Session
from app.models import TranscriptChunk

def recursive_text_splitter(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> list[str]:
    """
    Lightweight Recursive Character Text Splitter.
    Splits by paragraph, then sentence, then space, respecting chunk_size and maintaining context via overlap.
    """
    if not text:
        return []

    separators = ["\n\n", "\n", ". ", " ", ""]
    
    # Find the largest separator we can use that exists in the text
    sep = ""
    for s in separators:
        if s == "" or s in text:
            sep = s
            break

    splits = text.split(sep) if sep else list(text)
    
    chunks = []
    current_chunk = ""
    
    for piece in splits:
        if len(current_chunk) + len(piece) + len(sep) <= chunk_size:
            current_chunk += piece + sep
        else:
            # We reached max capacity. Save current_chunk.
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            # Start the next chunk, carrying over exactly chunk_overlap characters from the end of current_chunk
            overlap_prefix = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
            current_chunk = overlap_prefix + piece + sep
            
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def process_and_store_embeddings(transcript_text: str, video_id: int, user_id: int, db: Session):
    """
    Takes a transcript, splits it via recursive text splitting, embeds chunks via 
    all-MiniLM-L6-v2, and persists them into pgvector via PostgreSQL.
    """
    # Do NOT embed silent files or Whisper error strings
    if not transcript_text or "No spoken audio track" in transcript_text or "Error loading local Whisper" in transcript_text:
        print(f"[Embedding Service] Invalid or empty transcript for video_id {video_id}. Skipping embedding.")
        return

    # 1. Prevent duplicate chunk/embedding generation
    existing = db.query(TranscriptChunk).filter(TranscriptChunk.video_id == video_id).first()
    if existing:
        print(f"[Embedding Service] Embeddings already exist for video_id {video_id}. Skipping duplicate generation.")
        return

    print(f"\n[Embedding Service] Starting chunking and embedding for video_id {video_id}...")
    
    try:
        os.environ["HF_HOME"] = r"D:\temp\hf_cache"
        from sentence_transformers import SentenceTransformer
        
        # Load embedding model directly on CPU targeting D: drive cache
        print(f"[Embedding Service] Loading all-MiniLM-L6-v2...")
        model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=r"D:\temp\hf_cache")
        
        # 2. Chunk transcript recursively
        chunks = recursive_text_splitter(transcript_text, chunk_size=1000, chunk_overlap=150)
        print(f"[Embedding Service] Transcript split into {len(chunks)} overlapping chunks.")
        
        # 3. Generate Embeddings & Assemble models
        db_chunks = []
        for i, chunk_text in enumerate(chunks):
            # Encode correctly gives a NumPy array. Convert to Python list for pgvector.
            embedding_vector = model.encode(chunk_text).tolist()
            
            chunk_model = TranscriptChunk(
                video_id=video_id,
                user_id=user_id,
                chunk_text=chunk_text,
                chunk_index=i,
                embedding=embedding_vector
            )
            db_chunks.append(chunk_model)
            
        # 4. Save to PostgreSQL Vector table
        db.add_all(db_chunks)
        db.commit()
        print(f"[Embedding Service] Successfully stored {len(db_chunks)} dimensionally-aligned chunks in PostgeSQL pgvector.")

    except Exception as e:
        # Gracefully handle failure so it doesn't crash or invalidate the successfully generated transcript
        db.rollback()
        print(f"[Embedding Service] Error generating/saving embeddings: {e}")

import numpy as np

def search_transcript_similarity(query: str, video_id: int, user_id: int, db: Session, top_k: int = 5):
    """
    Sanjana's Similarity and Importance Scoring implementation!
    Bypasses pgvector by manually computing Cosine Similarity using NumPy on PostgreSQL ARRAY(Float).
    """
    os.environ["HF_HOME"] = r"D:\temp\hf_cache"
    from sentence_transformers import SentenceTransformer
    
    # Load model entirely offline
    model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=r"D:\temp\hf_cache")
    query_embedding = model.encode(query)
    
    chunks = db.query(TranscriptChunk).filter(
        TranscriptChunk.video_id == video_id, 
        TranscriptChunk.user_id == user_id
    ).all()
    
    if not chunks:
        return []
        
    results = []
    
    # Compute Cosine Similarity Formula natively in NumPy
    query_norm = np.linalg.norm(query_embedding)
    if query_norm == 0:
        return []
        
    for chunk in chunks:
        if not chunk.embedding:
            continue
            
        chunk_emb = np.array(chunk.embedding)
        chunk_norm = np.linalg.norm(chunk_emb)
        
        if chunk_norm == 0:
            continue
            
        similarity = np.dot(query_embedding, chunk_emb) / (query_norm * chunk_norm)
        
        # Calculate Sanjana's Importance Score (Percentage representation)
        importance_score = round(float(similarity) * 100, 2)
        
        results.append({
            "chunk_index": chunk.chunk_index,
            "text": chunk.chunk_text,
            "similarity": round(float(similarity), 4),
            "importance_score": importance_score
        })
        
    # Sort natively by highest importance first
    results.sort(key=lambda x: x["importance_score"], reverse=True)
    return results[:top_k]
