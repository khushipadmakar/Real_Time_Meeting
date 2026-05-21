# Real-Time AI Meeting Platform

A production-style platform that captures meeting audio in real time, transcribes it with Whisper, and runs ML + GenAI pipelines to produce summaries, action items, sentiment analysis, topic clusters, and contextual Q&A over meeting history.

---

## Architecture

```
Browser Mic → WebSocket → Whisper Transcription
                              ↓
                    Kafka Streaming Pipeline
                              ↓
              ┌───────────────┼───────────────┐
           ML Pipeline    GenAI Pipeline    RAG Pipeline
         (sentiment,      (summary,        (ChromaDB +
          clustering,      action items,    embeddings +
          anomaly)         follow-up)       retrieval)
                              ↓
                      React Dashboard
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + SQLAlchemy (async) + SQLite |
| Transcription | OpenAI Whisper (local) |
| Streaming | Apache Kafka (confluent-kafka) |
| ML | scikit-learn (KMeans, TF-IDF, IsolationForest) |
| GenAI | OpenAI GPT-4o-mini (structured outputs) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB (persistent) |
| Frontend | React 18 + Recharts + MUI |
| Testing | pytest + pytest-asyncio |
| CI/CD | GitHub Actions |

---

## Project Structure

```
realtime_meeting_AI_platform/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings (pydantic-settings)
│   ├── database.py              # Async SQLAlchemy engine
│   ├── models/
│   │   ├── db_models.py         # SQLAlchemy ORM models
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── routers/
│   │   ├── meetings.py          # CRUD for meetings
│   │   ├── transcripts.py       # Transcript ingestion + audio upload
│   │   ├── analytics.py         # Full ML+GenAI processing pipeline
│   │   ├── rag.py               # RAG query, follow-up email, explain
│   │   └── agent.py             # AI agent analysis
│   ├── services/
│   │   ├── transcription.py     # Whisper transcription
│   │   ├── audio_stream.py      # WebSocket audio handler
│   │   ├── speaker_tracker.py   # Energy-based speaker diarization
│   │   ├── genai.py             # LLM: summary, actions, Q&A, email
│   │   └── agent.py             # Agentic workflow (escalation, reminders)
│   ├── ml/
│   │   ├── sentiment.py         # Lexicon-based sentiment scorer
│   │   ├── topic_clustering.py  # TF-IDF + KMeans clustering
│   │   ├── speaker_analysis.py  # Participation metrics
│   │   ├── anomaly_detection.py # IsolationForest engagement anomalies
│   │   └── engagement.py        # 0-100 engagement score
│   ├── kafka/
│   │   ├── producer.py          # publish_event()
│   │   └── consumers.py         # 5 topic consumers (background threads)
│   └── rag/
│       ├── embeddings.py        # sentence-transformers embed
│       ├── vector_store.py      # ChromaDB index + retrieve + chunk
│       └── retrieval.py         # rag_query() full pipeline
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── audio-processor.js   # AudioWorklet PCM processor
│   └── src/
│       ├── App.js
│       ├── api.js               # Axios API calls
│       └── components/
│           ├── Dashboard.jsx    # Main layout + meeting management
│           ├── AudioCapture.jsx # Mic → WebSocket streaming
│           ├── SpeakerPanel.jsx # Bar chart + speaker table
│           ├── SentimentChart.jsx # Line chart over time
│           ├── ActionItems.jsx  # Priority-tagged action list
│           ├── TopicClusters.jsx # Topic tag cloud
│           └── RAGQuery.jsx     # Ask questions over meeting history
├── tests/
│   ├── test_ml.py               # sentiment, clustering, speaker, anomaly
│   ├── test_rag.py              # chunking, embeddings, similarity
│   ├── test_api.py              # all REST endpoints
│   ├── test_kafka.py            # producer/consumer (mocked)
│   └── test_genai.py            # summarization, actions, RAG (mocked LLM)
├── .github/workflows/ci.yml     # GitHub Actions CI/CD
├── docker-compose.yml           # Kafka + backend + frontend
├── requirements.txt
└── .env.example
```

---

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd realtime_meeting_AI_platform
cp .env.example .env
# Edit .env — set OPENAI_API_KEY
```

### 2. Start Kafka (Docker — KRaft mode, no Zookeeper)

```bash
docker-compose up -d kafka
```

### 3. Run the backend

```bash
pip install -r requirements.txt
cd realtime_meeting_AI_platform
uvicorn backend.main:app --reload --port 9000
```

### 4. Run the frontend

```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

### 5. Run with Docker Compose (full stack)

```bash
docker-compose up --build
```

---

## API Reference

### Meetings

| Method | Endpoint | Description |
|---|---|---|
| POST | `/meetings/` | Create a new meeting |
| GET | `/meetings/` | List all meetings |
| GET | `/meetings/{id}` | Get meeting details |
| POST | `/meetings/{id}/end` | End a meeting |

### Transcripts

| Method | Endpoint | Description |
|---|---|---|
| POST | `/transcripts/` | Add a transcript segment |
| GET | `/transcripts/{meeting_id}` | Get all transcripts for a meeting |
| POST | `/transcripts/upload-audio/{meeting_id}` | Upload audio file for transcription |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| POST | `/analytics/{meeting_id}/process` | Run full ML + GenAI pipeline |
| GET | `/analytics/{meeting_id}` | Get cached analytics |

### RAG

| Method | Endpoint | Description |
|---|---|---|
| POST | `/rag/query` | Ask a question over meeting history |
| POST | `/rag/followup-email` | Generate follow-up email |
| POST | `/rag/explain` | Explain a transcript segment |

### AI Agent

| Method | Endpoint | Description |
|---|---|---|
| POST | `/agent/{meeting_id}/analyze` | Run agentic analysis |

### WebSocket

```
ws://localhost:9000/ws/audio/{meeting_id}
```
Send raw PCM float32 audio frames at 16 kHz. Send text `"END"` to stop.  
Receives JSON: `{"speaker": "...", "text": "...", "timestamp": "..."}`

---

## Real-Time Meeting Flow

1. **Create a meeting** via the dashboard or `POST /meetings/`
2. **Click "Start Recording"** — browser mic streams PCM audio over WebSocket
3. **Whisper transcribes** each 3-second audio chunk in real time
4. **Transcripts appear live** in the dashboard with speaker labels
5. **Click "Process Meeting"** after the meeting ends to trigger:
   - ML pipeline: speaker stats, topic clusters, sentiment, anomaly detection
   - GenAI pipeline: summary + action item extraction
   - RAG indexing: transcript chunks embedded into ChromaDB
6. **Click "Run Agent"** for escalation decisions, unresolved topics, reminders
7. **Use the RAG query box** to ask questions like:
   - *"What decisions were made about deployment?"*
   - *"What action items were assigned to Alice?"*

---

## Kafka Topics

| Topic | Event |
|---|---|
| `meeting.transcripts` | New transcript segment |
| `meeting.speakers` | Speaker activity update |
| `meeting.summaries` | Meeting summary generated |
| `meeting.action_items` | Action items extracted |
| `meeting.alerts` | Anomaly / escalation alert |

---

## ML Pipeline Details

### Sentiment Scoring
Lexicon-based scorer using positive/negative word sets. Returns `[-1, 1]`. No external API required.

### Topic Clustering
TF-IDF vectorization → KMeans clustering. Top 3 TF-IDF terms per cluster become the topic label. Auto-reduces `k` when fewer texts than clusters.

### Speaker Analysis
Word-count-based speaking time estimation (~150 wpm), turn count, and average sentiment per speaker. Participation percentage computed across all speakers.

### Anomaly Detection
IsolationForest on `[word_count, sentiment_score]` features. Contamination = 10%. Flags unusual silence or extreme sentiment segments.

### Engagement Score
Weighted combination:
- 40% — participation balance (inverse Gini coefficient)
- 40% — average sentiment (mapped to [0,1])
- 20% — anomaly penalty

---

## RAG Pipeline Details

1. **Chunking**: Transcript split into 300-word overlapping chunks (50-word overlap)
2. **Embedding**: `all-MiniLM-L6-v2` (384-dim, runs locally, no API cost)
3. **Storage**: ChromaDB persistent store at `./data/chroma`
4. **Retrieval**: Cosine similarity search, top-k chunks
5. **Generation**: Retrieved chunks passed as context to GPT-4o-mini

---

## AI Agent Capabilities

The agent analyzes a completed meeting and returns:

```json
{
  "needs_escalation": true,
  "escalation_reason": "Unresolved deployment failures in staging",
  "unresolved_topics": ["Databricks cluster config", "CI/CD pipeline fix"],
  "missed_action_items": ["No owner assigned for staging rollback"],
  "reminders": [{"assignee": "Bob", "reminder": "Review deployment pipeline by EOD"}],
  "prioritized_followups": [
    {"task": "Fix Kafka consumer lag", "priority": "high", "reason": "Blocking production"}
  ]
}
```

---

## Testing

```bash
# Run all tests
pytest -v

# Run specific suites
pytest tests/test_ml.py -v       # ML pipeline (no external deps)
pytest tests/test_rag.py -v      # Embeddings + chunking
pytest tests/test_kafka.py -v    # Kafka (mocked)
pytest tests/test_genai.py -v    # GenAI (mocked LLM)
pytest tests/test_api.py -v      # REST endpoints
```

Tests use mocks for OpenAI, Kafka, and ChromaDB so they run without any external services.

---

## CI/CD (GitHub Actions)

Three jobs run on every push and pull request:

| Job | What it does |
|---|---|
| `test-backend` | Installs deps, runs all 5 pytest suites, validates `/health` endpoint |
| `test-frontend` | `npm install` + `npm run build` |
| `validate-vector-indexing` | Indexes chunks into ChromaDB and validates retrieval returns results |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Required for GenAI features (get from console.groq.com) |
| `GROQ_MODEL` | `llama3-70b-8192` | Groq model name |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | Groq API base URL |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker address |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | ChromaDB storage path |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/meetings.db` | SQLAlchemy DB URL |
| `WHISPER_MODEL` | `base` | Whisper model size (`tiny`, `base`, `small`, `medium`) |

---

## Notes

- **No fake data**: All summaries, action items, and answers are generated from actual transcript content via LLM
- **No hardcoded action items**: Extraction uses structured LLM output grounded in the transcript
- **Vector search is real**: ChromaDB cosine similarity over sentence-transformer embeddings
- **Kafka is optional at startup**: The app starts gracefully if Kafka is unavailable; events are silently skipped
- **Speaker diarization**: Currently energy-based (simple). Replace `SpeakerTracker` with `pyannote.audio` for production-grade diarization
