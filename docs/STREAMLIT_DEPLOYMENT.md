# Streamlit Deployment Guide

## Overview

This application is now deployed as a single Streamlit application that combines both the frontend UI and backend RAG pipeline. This simplifies deployment and eliminates CORS issues.

## Deployment Options

### Option 1: Streamlit Cloud (Recommended)

Streamlit Cloud is the easiest way to deploy your Streamlit app.

#### Setup

1. **Create Streamlit Cloud Account**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign up with GitHub

2. **Deploy Your App**
   - Click "New app"
   - Connect your GitHub repository: `vishalkatariax/Groww_Mutual_Fund_RAG_Chatbot`
   - Configure:
     - **Main file path**: `streamlit_app.py`
     - **Python version**: `3.11`
   - Click "Deploy"

3. **Set Environment Variables**
   
   In Streamlit Cloud dashboard → Settings → Secrets, add:
   
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   LLM_PROVIDER = "groq"
   LLM_MODEL = "llama-3.1-8b-instant"
   LLM_TEMPERATURE = "0.0"
   LLM_MAX_TOKENS = "256"
   ```
   
   Or use the provided `.streamlit/secrets.toml.example` as a reference.

4. **Wait for Deployment**
   - Streamlit Cloud will automatically build and deploy
   - First deployment may take 5-10 minutes
   - Subsequent deployments are faster

### Option 2: Self-Hosted Deployment

Deploy on your own server using Docker or directly with Python.

#### Docker Deployment

1. **Create Dockerfile** (if not exists)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install chromium

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Build and Run**
```bash
docker build -t mf-faq-assistant .
docker run -p 8501:8501 --env-file .env mf-faq-assistant
```

#### Direct Python Deployment

1. **Install Dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

2. **Set Environment Variables**
```bash
export GROQ_API_KEY="your_api_key"
export LLM_PROVIDER="groq"
export LLM_MODEL="llama-3.1-8b-instant"
```

3. **Run Streamlit**
```bash
streamlit run streamlit_app.py
```

## Environment Variables

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `GROQ_API_KEY` | `your_groq_api_key` | Groq API key for LLM |
| `LLM_PROVIDER` | `groq` | LLM provider (groq or openai) |
| `LLM_MODEL` | `llama-3.1-8b-instant` | Model name for generation |
| `LLM_TEMPERATURE` | `0.0` | Temperature for LLM generation |
| `LLM_MAX_TOKENS` | `256` | Maximum tokens in response |

### Optional Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | `your_openai_api_key` | OpenAI API key for dual-client |
| `HF_TOKEN` | `your_hf_token` | Hugging Face token for faster downloads |

## Getting API Keys

### Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to Streamlit Cloud secrets

### OpenAI API Key (Optional)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key and add it to Streamlit Cloud secrets

## Configuration Files

### `.streamlit/config.toml`
Customizes the Streamlit app appearance and behavior:
- Theme colors
- Server settings
- Browser settings

### `packages.txt`
System dependencies for Streamlit Cloud:
- Chromium (for Playwright web scraping)

### `requirements.txt`
Python dependencies including:
- Streamlit
- RAG pipeline dependencies
- LLM client libraries

## Data Management

### Data Refresh Pipeline

The data refresh pipeline continues to work via GitHub Actions:

1. **GitHub Actions Workflow**
   - Located in `.github/workflows/data-refresh.yml`
   - Runs automatically on schedule
   - Scrapes latest data from Groww
   - Updates the corpus in the repository

2. **Manual Refresh**
   - Run the refresh script locally
   - Push changes to GitHub
   - Streamlit Cloud will automatically redeploy with updated data

## Deployment URLs

After successful deployment to Streamlit Cloud:

- **App URL**: `https://your-app-name.streamlit.app`
- **Example**: `https://groww-mf-faq-assistant.streamlit.app`

## Troubleshooting

### Build Failures

**Issue**: Dependencies fail to install
```bash
# Check requirements.txt
pip install -r requirements.txt

# Verify Playwright installation
playwright install chromium
```

**Issue**: System dependencies missing
- Ensure `packages.txt` includes `chromium`
- Check Streamlit Cloud build logs

### Runtime Errors

**Issue**: API key not found
- Verify secrets are set in Streamlit Cloud dashboard
- Check variable names match exactly

**Issue**: RAG pipeline initialization fails
- Verify data files exist in `data/` directory
- Check ChromaDB database is properly initialized

**Issue**: LLM API errors
- Verify API key is valid and has credits
- Check if model is available in your region
- Monitor API rate limits

### Performance Issues

**Issue**: Slow response times
- Check if data files are too large
- Consider using smaller embedding models
- Monitor Streamlit Cloud resource limits

**Issue**: Memory errors
- Streamlit Cloud free tier has memory limits
- Consider upgrading to paid tier for production
- Optimize data loading (lazy loading)

## Monitoring and Logs

### Streamlit Cloud Logs

1. Go to your app in Streamlit Cloud
2. Click "Manage app"
3. View logs in the "Logs" section
4. Check for errors and warnings

### Local Testing

```bash
# Run locally with same environment
streamlit run streamlit_app.py

# Check logs in terminal
# Monitor for errors and performance issues
```

## Security Best Practices

1. **Never commit API keys** - Use Streamlit Cloud secrets
2. **Use HTTPS** - Streamlit Cloud provides automatic SSL
3. **Monitor API usage** - Check provider dashboards
4. **Rotate API keys** - Regularly update sensitive keys
5. **Limit data exposure** - Only expose necessary information

## Cost

### Streamlit Cloud
- **Free Tier**: Sufficient for development and light usage
  - Community support
  - Limited resources
  - No custom domain

- **Paid Tier**: For production usage
  - Priority support
  - More resources
  - Custom domain available

### API Costs
- **Groq**: Free tier available, very cost-effective
- **OpenAI**: Paid, usage-based pricing
- **Hugging Face**: Free for most models

## Performance Optimization

### Caching

Streamlit automatically caches function results. Use `@st.cache_data` for expensive operations:

```python
@st.cache_data
def load_rag_pipeline():
    return RAGPipeline()
```

### Lazy Loading

Initialize heavy resources only when needed:

```python
if st.session_state.rag_pipeline is None:
    st.session_state.rag_pipeline = RAGPipeline()
```

### Data Optimization

- Use efficient data formats (Parquet, SQLite)
- Load only necessary data
- Consider data partitioning

## Customization

### Theme Customization

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor="#667eea"
backgroundColor="#ffffff"
```

### UI Customization

Modify `streamlit_app.py` to customize:
- Layout
- Components
- Styling
- Functionality

## CI/CD

Streamlit Cloud automatically deploys on push to main branch when connected via GitHub. No additional CI/CD configuration is needed.

For custom deployment logic, you can use GitHub Actions to:
- Run tests before deployment
- Notify team of deployments
- Rollback on failure

## Support

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Project Issues**: Check GitHub Issues for this repository

## Migration from Render+Vercel

If migrating from the previous Render+Vercel setup:

1. **Archive old configs**: Moved to `.deprecated/`
2. **Update environment variables**: Use Streamlit Cloud secrets
3. **Remove CORS configuration**: No longer needed
4. **Test locally**: Verify Streamlit app works before deploying
5. **Update documentation**: Reference this guide instead

## Advantages of Streamlit Deployment

- **Simplified architecture**: Single app instead of separate frontend/backend
- **No CORS issues**: Everything runs in the same context
- **Easier deployment**: One-click deployment to Streamlit Cloud
- **Built-in UI**: Streamlit provides chat components out of the box
- **Rapid prototyping**: Easy to iterate and test changes
- **Cost-effective**: Free tier available for development
