# Render Environment Variables

## Essential Environment Variables for Render Deployment

These environment variables must be configured in your Render web service dashboard for the MF FAQ Assistant backend to function correctly.

### Required Variables

| Variable | Type | Description | Example Value |
|----------|------|-------------|---------------|
| `GROQ_API_KEY` | Secret | Groq API key for LLM inference | `gsk_...` |
| `LLM_PROVIDER` | String | LLM provider to use | `groq` |
| `LLM_MODEL` | String | Model name for generation | `llama-3.1-8b-instant` |
| `LLM_TEMPERATURE` | String | Temperature for LLM generation | `0.0` |
| `LLM_MAX_TOKENS` | String | Maximum tokens in response | `256` |
| `FRONTEND_URL` | String | URL of the deployed frontend (for CORS) | `https://your-app.vercel.app` |

### Optional Variables

| Variable | Type | Description | Example Value |
|----------|------|-------------|---------------|
| `OPENAI_API_KEY` | Secret | OpenAI API key (for dual-client setup) | `sk-...` |
| `HF_TOKEN` | Secret | Hugging Face token for faster model downloads | `hf_...` |
| `PYTHON_VERSION` | String | Python version (if not using default) | `3.11.0` |

## How to Set Environment Variables in Render

1. Go to your Render Dashboard
2. Select your web service (e.g., `mf-faq-assistant-backend`)
3. Navigate to the **Environment** tab
4. Add each variable with its corresponding value
5. For secret values (API keys), ensure they are marked as sensitive

## Getting API Keys

### Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to Render as `GROQ_API_KEY`

### OpenAI API Key (Optional)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key and add it to Render as `OPENAI_API_KEY`

### Hugging Face Token (Optional)
1. Go to [huggingface.co](https://huggingface.co)
2. Navigate to Settings → Access Tokens
3. Create a new token (read permission is sufficient)
4. Copy the token and add it to Render as `HF_TOKEN`
5. This eliminates the "unauthenticated requests to HF Hub" warning and enables faster downloads

## Variable Explanations

### LLM Configuration
- **LLM_PROVIDER**: Set to `groq` to use Groq's fast inference, or `openai` for OpenAI
- **LLM_MODEL**: The specific model to use. For Groq: `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, etc.
- **LLM_TEMPERATURE**: Controls randomness. `0.0` for deterministic responses (recommended for factual QA)
- **LLM_MAX_TOKENS**: Maximum length of generated response. `256` is sufficient for short factual answers

### CORS Configuration
- **FRONTEND_URL**: Must match your deployed Vercel frontend URL exactly, including `https://` and without trailing slash

## Security Notes

- Never commit API keys to your repository
- Use Render's secret feature for sensitive values
- Rotate API keys periodically
- Monitor API usage in your provider's dashboard

## Troubleshooting

### API Key Issues
- Verify the API key is valid and active
- Check if the key has sufficient quota/credits
- Ensure the key is copied without extra spaces

### CORS Errors
- Verify `FRONTEND_URL` matches your Vercel deployment URL exactly
- Include the protocol (`https://`)
- Do not include a trailing slash

### LLM Issues
- Verify `LLM_PROVIDER` and `LLM_MODEL` are compatible
- Check if the model is available in your region
- Monitor API rate limits in your provider's dashboard
