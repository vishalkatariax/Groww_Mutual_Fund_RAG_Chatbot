# Deployment Guide

## Backend - Render

### Setup

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Backend**
   - Go to Render Dashboard → New → Web Service
   - Connect your GitHub repository: `vishalkatariax/Groww_Mutual_Fund_RAG_Chatbot`
   - Select branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   
   In Render dashboard → Environment section, add these variables:
   
   | Variable | Value | Description |
   |----------|-------|-------------|
   | `GROQ_API_KEY` | `your_groq_api_key` | Groq API key for LLM |
   | `OPENAI_API_KEY` | `optional` | Optional for dual-client |
   | `FRONTEND_URL` | `https://your-frontend.vercel.app` | Vercel frontend URL |
   | `LLM_PROVIDER` | `groq` | LLM provider (groq or openai) |
   | `LLM_MODEL` | `llama-3.1-8b-instant` | Model to use |
   | `LLM_TEMPERATURE` | `0.0` | Temperature for generation |
   | `LLM_MAX_TOKENS` | `256` | Max tokens in response |

4. **Deploy**
   - Render auto-deploys on push to main branch
   - Or manually trigger from Render dashboard

5. **Get Backend URL**
   - Render provides a URL like: `https://groww-mutual-fund-rag-chatbot.onrender.com`
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
   | `VITE_API_URL` | `https://groww-mutual-fund-rag-chatbot.onrender.com` | Render backend URL |

4. **Update Backend CORS**
   
   After getting Vercel URL, update Render env:
   ```
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

5. **Custom Domain (Optional)**
   - Vercel: Settings → Domains → Add custom domain
   - Render: Settings → Custom Domains → Add custom domain

---

## GitHub Actions (Auto-Deploy)

### Backend (Render)

Render automatically deploys on push to main branch when connected via GitHub. No additional GitHub Actions workflow is needed.

If you need custom deployment logic, you can use Render's native GitHub integration or create a workflow that triggers Render's API.

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
   - Run the refresh script locally and push changes to GitHub
   - Render will auto-deploy the updated data

---

## URLs

After deployment:

- **Backend (Render)**: `https://groww-mutual-fund-rag-chatbot.onrender.com`
- **Frontend (Vercel)**: `https://groww-mutual-fund-rag-chatbot-ne6prvmfj.vercel.app`
- **API Docs**: `https://groww-mutual-fund-rag-chatbot.onrender.com/docs`

---

## Troubleshooting

### Backend Issues
- Check logs in Render Dashboard → Logs tab
- View deployment events in Render Dashboard → Events tab
- SSH into the container: Render Dashboard → Shell (if available on your plan)
- Verify environment variables in Render Dashboard → Environment section

### Frontend Issues
```bash
# Build locally
cd app/frontend
vercel build

# Check environment
vercel env pull
```

### CORS Errors
1. Verify `FRONTEND_URL` in Render matches Vercel URL exactly
2. Include protocol (https://)
3. No trailing slash
