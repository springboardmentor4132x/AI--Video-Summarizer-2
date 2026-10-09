# 🚀 ClipMind: AI Video Studio

Watch less. Understand more. ClipMind is a full-stack, AI-powered video summarization platform designed to extract audio, generate highly-accurate transcripts, and write structured study notes so students, creators, and educators can skip to exactly what matters.

---

## 🎯 Problem Statement (PS)
In the modern educational and content creation era, individuals consume hours of long-form video content daily. The core problem is **inefficiency**: watching a 45-minute lecture or tutorial to find 2 minutes of relevant information is incredibly time-consuming. Students struggle to create organized study notes while watching, and content creators lack fast ways to analyze and chapter their own lengthy uploads.

## 💡 Our Solution
ClipMind solves this by utilizing massive, state-of-the-art AI models (OpenAI Whisper & HuggingFace Transformers) to automatically watch the video for you. 
By uploading a video to our secure platform, ClipMind intelligently rips the audio, transcribes it word-for-word, semantically analyzes the text, and produces detailed, chapterized summaries and study notes. We deployed this into a highly-scalable Hybrid Cloud Architecture, delivering the speed of a Vercel-hosted Next.js frontend with the raw mathematical power of a Google Cloud Platform (GCP) GPU-enabled backend.

---

## ⚙️ Core Technical Features & Implementation

### 1. Robust Video Upload & Metadata Extraction
- **Logic:** Videos uploaded via the React UI are securely transmitted directly to the Google Cloud Virtual Machine.
- **Implementation:** FFmpeg (`ffprobe`) runs natively on the heavy Linux server to extract rich metadata (duration, resolution, file size) flawlessly before processing even begins.

### 2. High-Fidelity Audio Transcription (Offline Whisper STT)
- **Logic:** We specifically avoided expensive cloud APIs by running the Speech-to-Text inference directly on our own server.
- **Implementation:** Integrated `openai-whisper` inside a completely containerized Docker environment. It automatically extracts the `.mp3` audio track, maps the waveform to text, and aligns timestamp chunks accurately to seconds.

### 3. Extractive NLP Summarization (TF-IDF & Transformers)
- **Logic:** Transcripts are often hundreds of pages long. We process the raw text into distinct embeddings.
- **Implementation:** Using `sentence-transformers` and `scikit-learn`, the text is tokenized, vectorized, and scored for semantic importance. The Top-K most crucial sentences are clustered into a "Short" and "Detailed" summary output. 

### 4. Semantic Search & Intelligent Chapters
- **Logic:** Users need to quickly jump to the exact second a topic was mentioned.
- **Implementation:** The transcription chunks are stored inside a PostgreSQL database using `pgvector`. This allows lightning-fast cosine similarity lookups when a user queries for a specific concept.

### 5. Multi-Language AI Translation
- **Logic:** Education must be accessible to students worldwide.
- **Implementation:** Integrated `argostranslate` natively inside the Python environment to translate the massive, complex generated summaries into multiple dialects in real-time.

---

## 📸 Platform Walkthrough & Gallery

### 1. The Landing Page
![Landing Page](https://via.placeholder.com/800x400.png?text=Landing+Page)
*A stunning, highly-responsive entrance. It instantly communicates the value proposition to educators and students, offering direct routes to Create an Account or securely Sign in via our JWT authentication layer.*

### 2. Live Analytics Studio
![Analytics Dashboard](https://via.placeholder.com/800x400.png?text=Live+Analytics+Studio)
*Our command center. This provides a real-time mathematical breakdown of platform health. It tracks total videos, successful AI pipelines, and average video duration. We utilized specialized Donut and Line charts to visually display the exact processing trends over 7, 30, and 90 days.*

### 3. Key Insights & Activity Feed
![Insights & Feed](https://via.placeholder.com/800x400.png?text=Insights+and+Activity+Feed)
*On the right side of the dashboard, users see a chronological history of their exact uploads along with AI-generated insights indicating total uptime, success rates, and pipeline stability.*

### 4. Processing Library
![Library Options](https://via.placeholder.com/800x400.png?text=Video+Library)
*The central hub for all uploaded media. It dynamically fetches the high-resolution thumbnails generated natively by FFmpeg and clearly displays the processing status (Uploaded -> Processing -> Completed).*

### 5. AI Summary Generation
![AI Summary](https://via.placeholder.com/800x400.png?text=AI+Summary+Page)
*The end result of our heavy ML backend. On the left, it provides a punchy, one-sentence Short Summary. On the right, it provides a deeply detailed, extractive summary analyzing the entire context of the video.*
