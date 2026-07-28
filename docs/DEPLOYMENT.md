# Deployment Guide

## Streamlit Deployment (Recommended)

This application is deployed as a single Streamlit app that combines the frontend UI and backend RAG pipeline. This simplifies deployment and eliminates CORS issues.

### Quick Start

1. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository: `vishalkatariax/Groww_Mutual_Fund_RAG_Chatbot`
   - Set main file to: `streamlit_app.py`
   - Click Deploy

2. **Set Environment Variables** in Streamlit Cloud secrets:
   - `GROQ_API_KEY`: Your Groq API key
   - `LLM_PROVIDER`: `groq`
   - `LLM_MODEL`: `llama-3.1-8b-instant`
   - `LLM_TEMPERATURE`: `0.0`
   - `LLM_MAX_TOKENS`: `256`

3. **Wait for deployment** - First deployment takes 5-10 minutes

For detailed instructions, see [STREAMLIT_DEPLOYMENT.md](./STREAMLIT_DEPLOYMENT.md)

---

## Legacy Deployments (Archived)

The following deployment configurations have been archived in `.deprecated/`:

- **Render + Vercel**: Previous setup with separate backend (Render) and frontend (Vercel)
- **Configuration files**: `render.yaml`, `vercel.json`
- **Documentation**: Render and Vercel deployment guides

These are kept for reference but are no longer maintained. Use Streamlit deployment for new deployments.
