# MF FAQ Assistant - Orchestration Guide

This directory contains orchestration scripts and configurations for running the MF FAQ Assistant application.

## 📁 Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `start_dev.sh` | Development startup script | Daily development work |
| `run_full_pipeline.py` | Run all Phase 1 subphases | Initial setup or data refresh |
| `docker-compose.yml` | Production deployment | Deploying to production |
| `run_phase_1_complete.py` | Run Phase 1.1 + 1.2 only | Quick data ingestion |

---

## 🚀 Quick Start

### **Development Mode**

Start both backend and frontend with hot-reload:

```bash
./scripts/start_dev.sh
```

**Options:**
```bash
./scripts/start_dev.sh              # Start both servers
./scripts/start_dev.sh --backend    # Start only backend
./scripts/start_dev.sh --frontend   # Start only frontend
./scripts/start_dev.sh --help       # Show help
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Stop:** Press `Ctrl+C`

---

## 📊 Data Pipeline

### **Run Full Pipeline (All Phases)**

```bash
python3 scripts/run_full_pipeline.py
```

### **Run Specific Phase**

```bash
python3 scripts/run_full_pipeline.py --phase 1.1  # Data ingestion only
python3 scripts/run_full_pipeline.py --phase 1.2  # Chunking & embedding only
python3 scripts/run_full_pipeline.py --phase 1.3  # RAG testing only
```

### **Quick Data Refresh (Phases 1.1 + 1.2)**

```bash
python3 scripts/run_phase_1_complete.py
```

**What it does:**
1. Scrapes 5 HDFC fund pages from Groww
2. Parses and cleans HTML content
3. Chunks documents into 83 segments
4. Generates embeddings using BGE-Small-EN
5. Stores in ChromaDB vector store

---

## 🐳 Docker Deployment

### **Production Setup**

1. **Set environment variables:**
```bash
export GROQ_API_KEY=your_groq_key
export OPENAI_API_KEY=your_openai_key  # Only needed if using OpenAI embeddings
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

4. **Stop services:**
```bash
docker-compose down
```

**Services:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- ChromaDB: http://localhost:8001

### **Development Mode with Docker**

Uncomment the `frontend-dev` service in `docker-compose.yml`:

```bash
docker-compose up frontend-dev backend
```

---

## 🔧 Individual Scripts

### **Phase-Specific Runners**

```bash
python3 scripts/run_phase_1_1.py  # Corpus collection
python3 scripts/run_phase_1_2.py  # Chunking & embedding
python3 scripts/run_phase_1_3.py  # RAG setup
python3 scripts/run_phase_1_4.py  # Compliance
python3 scripts/run_phase_1_5.py  # Testing
```

### **Verification**

```bash
python3 scripts/verify_groq.py  # Verify Groq API integration
```

---

## 📋 Typical Workflows

### **First-Time Setup**

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd app/frontend && npm install && cd ../..

# 2. Run data pipeline
python3 scripts/run_full_pipeline.py

# 3. Start development servers
./scripts/start_dev.sh
```

### **Daily Development**

```bash
# Just start servers (data already exists)
./scripts/start_dev.sh
```

### **Refresh Data**

```bash
# Re-scrape and re-embed all documents
python3 scripts/run_phase_1_complete.py

# Or run full pipeline with testing
python3 scripts/run_full_pipeline.py
```

### **Deploy to Production**

```bash
# Build and start with Docker
export GROQ_API_KEY=your_key
docker-compose up -d --build
```

---

## 🐛 Troubleshooting

### **Port Already in Use**

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Find process using port 3000
lsof -ti:3000 | xargs kill -9
```

### **Python Cache Issues**

```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### **ChromaDB Issues**

```bash
# Reset ChromaDB (deletes all embeddings)
rm -rf data/chroma_db/*

# Re-run pipeline
python3 scripts/run_phase_1_complete.py
```

---

## 📝 Notes

- **BGE-Small-EN**: Local embedding model (~130MB), no API key required
- **Groq**: LLM provider for response generation (free tier available)
- **ChromaDB**: Embedded vector database, runs locally
- **Hot Reload**: Both backend and frontend auto-reload on file changes

---

## 🤝 Need Help?

- API Documentation: http://localhost:8000/docs
- Project README: `../README.md`
- Architecture: `../ARCHITECTURE.md`
