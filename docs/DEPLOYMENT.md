# Deployment Guide

## Backend - Railway

### Setup

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy Backend**
   ```bash
   # Navigate to project root
   # cd /path/to/project-root
   
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Create new project
   railway init
   
   # Link to GitHub repo
   railway connect <github-repo-url>
   ```

3. **Set Environment Variables**
   
   In Railway dashboard, add these variables:
   
   | Variable | Value | Description |
   |----------|-------|-------------|
   | `GROQ_API_KEY` | `your_groq_api_key` | Groq API key for LLM |
   | `OPENAI_API_KEY` | `optional` | Optional for dual-client |
   | `FRONTEND_URL` | `https://your-frontend.vercel.app` | Vercel frontend URL |

4. **Deploy**
   - Railway auto-deploys on push to main branch
   - Or manually: `railway up`

5. **Get Backend URL**
   - Railway provides a URL like: `https://groww-mutual-fund-rag-chatbot.railway.app`
   - Note this URL for Vercel frontend config

---

## Frontend - Vercel

### Setup

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Deploy Frontend**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Login
   vercel login
   
   # Navigate to frontend
   cd app/frontend
   
   # Deploy
   vercel
   ```

3. **Configure Environment Variables**
   
   In Vercel dashboard or CLI:
   
   | Variable | Value | Description |
   |----------|-------|-------------|
   | `VITE_API_URL` | `https://your-railway-backend.railway.app` | Railway backend URL |

4. **Update Backend CORS**
   
   After getting Vercel URL, update Railway env:
   ```
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

5. **Custom Domain (Optional)**
   - Vercel: Settings → Domains → Add custom domain
   - Railway: Settings → Networking → Add custom domain

---

## GitHub Actions (Auto-Deploy)

### Backend (Railway)

Create `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend to Railway

on:
  push:
    branches: [main]
    paths:
      - 'app/**'
      - 'config.py'
      - 'requirements.txt'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        uses: railway/action-deploy@v1
        with:
          args: up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Frontend (Vercel)

Connect in Vercel dashboard:
1. Import GitHub repo: `vishalkatariax/Groww_Mutual_Fund_RAG_Chatbot`
2. Root directory: `app/frontend`
3. Framework: `Vite`
4. Build command: `npm run build`
5. Output directory: `dist`

---

## Data Refresh Pipeline

For production, set up GitHub Actions to refresh data:

1. **Create Secrets in GitHub**
   - `GROQ_API_KEY`
   - `HF_TOKEN` (optional, for faster embeddings)

2. **Add Workflow** (already in `.github/workflows/`)

3. **Manual Refresh**
   ```bash
   railway run python scripts/run_phase_1_complete.py
   ```

---

## URLs

After deployment:

- **Backend (Railway)**: `https://groww-mutual-fund-rag-chatbot.railway.app`
- **Frontend (Vercel)**: `https://groww-mutual-fund-rag-chatbot.vercel.app`
- **API Docs**: `https://groww-mutual-fund-rag-chatbot.railway.app/docs`

---

## Troubleshooting

### Backend Issues
```bash
# Check logs
railway logs

# Open shell
railway shell

# Check env vars
railway variables
```

### Frontend Issues
```bash
# Build locally
cd app/frontend
vercel build

# Check environment
vercel env pull
```

### CORS Errors
1. Verify `FRONTEND_URL` in Railway matches Vercel URL exactly
2. Include protocol (https://)
3. No trailing slash
