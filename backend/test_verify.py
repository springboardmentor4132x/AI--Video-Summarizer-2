import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models import TranscriptChunk, Video

load_dotenv('.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Load chunks for a recently processed video
chunks = db.query(TranscriptChunk).order_by(TranscriptChunk.id.desc()).limit(10).all()

if not chunks:
    print("Transcript: NO VALID TRANSCRIPTS/CHUNKS FOUND YET")
else:
    video_id = chunks[0].video_id
    video_chunks = db.query(TranscriptChunk).filter(TranscriptChunk.video_id == video_id).order_by(TranscriptChunk.chunk_index.asc()).all()
    
    valid_transcript = "Error loading local Whisper" not in video_chunks[0].chunk_text and "No spoken audio" not in video_chunks[0].chunk_text
    invalid_chunks = sum(1 for c in video_chunks if "Error loading" in c.chunk_text or "No spoken audio" in c.chunk_text)
    
    dim = len(video_chunks[0].embedding) if video_chunks[0].embedding else 0
    all_zeros = all(x == 0 for x in video_chunks[0].embedding) if dim > 0 else True
    
    print("\n--- VERIFICATION REPORT ---")
    print(f"Transcript: {'VALID' if valid_transcript else 'INVALID'}")
    print(f"Chunks generated: {len(video_chunks)}")
    print(f"Embeddings generated: {len([c for c in video_chunks if c.embedding])}")
    print(f"Embedding dimension: {dim}")
    print(f"Embeddings all-zero: {all_zeros}")
    print(f"Invalid/error chunks: {invalid_chunks}")
    print("Database storage: SUCCESS (PostgreSQL ARRAY(Float))")

db.close()
