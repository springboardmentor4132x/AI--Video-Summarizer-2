import os
from pathlib import Path

def generate_video_summary(file_path: str, filename: str, file_type: str = "mp4") -> dict:
    """
    Generate AI video summary + Speech-to-Text transcript using ONLY OFFLINE LOCAL MODELS.
    Uses OpenAI Whisper + HuggingFace Transformers.
    """
    # Force heavy ML model downloads into D: drive to prevent C: drive crashes!
    os.environ["HF_HOME"] = r"D:\temp\hf_cache"
    os.makedirs(r"D:\temp\hf_cache", exist_ok=True)
    os.makedirs(r"D:\temp\whisper_cache", exist_ok=True)
    
    try:
        import whisper
        from transformers import pipeline
    except ImportError as e:
        raise RuntimeError(f"Missing ML dependency: {e}. You must run this using the D:\\clipmind_venv environment.")

    print(f"\n[AI Offline Engines] Loading Local Whisper 'base' Model (D: Drive)...")
    # Load Whisper (downloads ~140MB base model to D: if missing)
    model = whisper.load_model("base", download_root=r"D:\temp\whisper_cache")
    
    print(f"[AI Offline Engines] Transcribing audio natively using FFmpeg & Whisper...")
    result = model.transcribe(str(file_path), fp16=False)
    transcript = result.get("text", "").strip()
    
    if not transcript:
        return {
            "summary": "No spoken dialogue detected. Visual review required.",
            "takeaways": ["Silent video.", "No audio track.", "Metadata preserved."],
            "transcript": "[No spoken audio track detected in this video file]"
        }

    print(f"[AI Offline Engines] Loading Offline HuggingFace Summarizer...")
    # Load manual models directly to bypass broken pipeline registry
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
        summarizer_model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")
    except Exception as e:
        print(f"Transformers Model Load Error: {e}")
        return {
            "summary": "Offline Models failed to load.",
            "takeaways": ["Model error.", "Check PyTorch installation.", str(e)[:30]],
            "transcript": transcript
        }
    
    print(f"[AI Offline Engines] Chunking and summarizing local transcript...")
    words = transcript.split()
    chunks = [" ".join(words[index:index + 400]) for index in range(0, len(words), 400)]
    
    chunk_summaries = []
    for chunk in chunks:
        if chunk:
            l = len(chunk.split())
            if l < 20: 
                chunk_summaries.append(chunk)
                continue
            
            inputs = tokenizer(chunk, max_length=1024, return_tensors="pt", truncation=True)
            max_len = min(60, max(20, l - 5))
            summary_ids = summarizer_model.generate(inputs["input_ids"], max_length=max_len, min_length=15, do_sample=False)
            sum_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            chunk_summaries.append(sum_text)
            
    detailed = " ".join(chunk_summaries)
    
    if len(detailed.split()) > 20:
        inputs = tokenizer(detailed[:2048], max_length=1024, return_tensors="pt", truncation=True)
        summary_ids = summarizer_model.generate(inputs["input_ids"], max_length=50, min_length=15, do_sample=False)
        short = tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()
    else:
        short = detailed.strip()
        
    # Formulate 3 distinct takeaways from the local summaries
    takeaways = [
        (chunk_summaries[0].split(".")[0][:80] + "...") if len(chunk_summaries) > 0 else "Content processed.",
        (chunk_summaries[1].split(".")[0][:80] + "...") if len(chunk_summaries) > 1 else "Key phrases identified.",
        (chunk_summaries[-1].split(".")[0][:80] + "...") if len(chunk_summaries) > 2 else "Final conclusion drawn."
    ]

    print(f"[AI Offline Engines] Processing Complete! Returning results to frontend.")
    return {
        "summary": f"{short}|||{detailed}",  # short|||detailed split on retrieval
        "takeaways": takeaways[:3],
        "transcript": transcript
    }

