"""
translate_utils.py
--------------------
Module 2 ka extra feature: transcript ko doosri languages mein translate karna.
 
deep-translator library free hai (Google Translate ke web endpoint ko use
karta hai) — koi API key ya paid subscription nahi chahiye, bas internet
connection chahiye (Whisper/embeddings ki tarah yeh offline nahi hai).
"""
 
from deep_translator import GoogleTranslator
 
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "mr": "Marathi",
    "gu": "Gujarati",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "kn": "Kannada",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ar": "Arabic",
}
 
_MAX_CHUNK_CHARS = 4500  # Google Translate ke free endpoint ki practical limit ke andar
 
 
def _split_into_chunks(text: str, max_chars: int = _MAX_CHUNK_CHARS):
    """Text ko sentence boundaries par todte hue chunks banata hai
    (isse translation ek baar mein fail nahi hoti aur quality bhi behtar rehti hai)."""
    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current = ""
    for sentence in sentences:
        piece = sentence if sentence.endswith(".") else sentence + ". "
        if len(current) + len(piece) > max_chars and current:
            chunks.append(current.strip())
            current = piece
        else:
            current += piece
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text]
 
 
def translate_text(text: str, target_lang: str) -> str:
    """Poora transcript text translate karta hai, chunk-by-chunk."""
    if not text or not text.strip():
        return ""
 
    if target_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language code: {target_lang}")
 
    translator = GoogleTranslator(source="auto", target=target_lang)
    chunks = _split_into_chunks(text)
 
    translated_chunks = [translator.translate(chunk) for chunk in chunks]
    return " ".join(t for t in translated_chunks if t)
 





