# Vercel Deployment Guide

## Overview

This project uses Vercel for frontend deployment. The backend is deployed on Render, and Vercel handles API proxying to the backend.

## Frontend Deployment (Vercel)

### Setup

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Deploy Frontend via Vercel Dashboard**
   
   **Option A: Using Vercel Dashboard (Recommended)**
   - Go to Vercel Dashboard → Add New → Project
   - Import your GitHub repository: `vishalkatariax/Groww_Mutual_Fund_RAG_Chatbot`
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `app/frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
   - Click **Deploy**

   **Option B: Using Vercel CLI**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Login
   vercel login
   
   # Deploy from project root (vercel.json specifies rootDirectory)
   vercel
   ```

3. **Configure Environment Variables**
   
   In Vercel dashboard → Settings → Environment Variables, add:
   
   | Variable | Value | Description |
   |----------|-------|-------------|
   | `VITE_API_URL` | `https://your-render-backend.onrender.com` | Render backend URL |

   **Important:** Set this variable in both **Production** and **Preview** environments.

4. **Update Backend CORS**
   
   After getting your Vercel URL, update your Render backend environment:
   ```
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

## Vercel Configuration Files

### Root `vercel.json` (Optional)
The root `vercel.json` is optional since the frontend has its own configuration. If you want to deploy from the root:

```json
{
  "rootDirectory": "app/frontend",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite"
}
```

### Frontend `vercel.json` (app/frontend/vercel.json)
This file is already configured for the frontend:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://mf-faq-assistant-backend.onrender.com/api/$1"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET, POST, OPTIONS" },
        { "key": "Access-Control-Allow-Headers", "value": "Content-Type, Authorization" }
      ]
    }
  ]
}
```

## API Proxying

Vercel rewrites API requests to the Render backend:

- Frontend requests to `/api/*` are proxied to `https://mf-faq-assistant-backend.onrender.com/api/*`
- This avoids CORS issues and keeps the backend URL hidden from the frontend code

**To update the backend URL:**
1. Edit `app/frontend/vercel.json`
2. Update the `destination` in the rewrites section
3. Redeploy to Vercel

## Custom Domain (Optional)

1. **Vercel Custom Domain**
   - Go to Vercel Dashboard → Your Project → Settings → Domains
   - Add your custom domain (e.g., `faq.yourdomain.com`)
   - Configure DNS records as instructed by Vercel

2. **Update CORS**
   - After setting custom domain, update `FRONTEND_URL` in Render backend
   - Update `VITE_API_URL` in Vercel if needed

## Environment Variables

### Required Variables

| Variable | Value | Where to Set |
|----------|-------|--------------|
| `VITE_API_URL` | `https://your-render-backend.onrender.com` | Vercel Dashboard → Environment Variables |

### How to Get Backend URL

1. Deploy your backend to Render first
2. Copy the Render URL (e.g., `https://mf-faq-assistant-backend.onrender.com`)
3. Set it as `VITE_API_URL` in Vercel

## Deployment URLs

After successful deployment:

- **Frontend (Vercel)**: `https://your-project.vercel.app`
- **Backend (Render)**: `https://mf-faq-assistant-backend.onrender.com`
- **API Docs**: `https://mf-faq-assistant-backend.onrender.com/docs`

## Troubleshooting

### Build Failures

```bash
# Build locally to test
cd app/frontend
npm install
npm run build

# Check for TypeScript errors
npm run build
```

### API Connection Issues

1. Verify `VITE_API_URL` is set correctly in Vercel
2. Check if backend is deployed and accessible
3. Verify CORS settings in backend (`FRONTEND_URL` environment variable)
4. Check Vercel rewrites in `app/frontend/vercel.json`

### Environment Variable Issues

```bash
# Pull environment variables locally
cd app/frontend
vercel env pull .env.local

# Check current environment
vercel env ls
```

### Preview Deployments

Vercel automatically creates preview deployments for each pull request. Ensure:
- Environment variables are set for **Preview** environment
- Backend URL is accessible from preview deployments

## CI/CD with GitHub Actions

Vercel automatically deploys on push to main branch when connected via GitHub. No additional GitHub Actions workflow is needed.

For custom deployment logic, you can use Vercel's GitHub integration or create a workflow that triggers Vercel's API.

## Performance Optimization

### Enable Caching

Vercel automatically caches static assets. For additional optimization:

1. **Cache API responses** (if applicable)
2. **Use Vercel Edge Functions** for dynamic content
3. **Enable Vercel Analytics** for performance monitoring

### Image Optimization

If you add images later, use Vercel's Image Optimization:
```jsx
import Image from 'next/image';

<Image 
  src="/path/to/image.jpg" 
  alt="Description" 
  width={500} 
  height={300} 
/>
```

## Monitoring and Logs

### View Logs

1. Go to Vercel Dashboard → Your Project
2. Click on the deployment
3. View **Build Logs** for build issues
4. View **Function Logs** for runtime issues

### Analytics

Enable Vercel Analytics:
1. Go to Vercel Dashboard → Your Project → Analytics
2. Install the analytics package if needed
3. Monitor performance and user behavior

## Security Best Practices

1. **Never commit `.env` files** - Use Vercel environment variables
2. **Use HTTPS** - Vercel provides automatic SSL
3. **Set proper CORS headers** - Configure in backend
4. **Monitor API usage** - Check Render and Vercel dashboards
5. **Rotate API keys** - Regularly update sensitive keys

## Cost

- **Vercel Hobby Plan**: Free (sufficient for this project)
  - 100GB bandwidth per month
  - Unlimited deployments
  - Automatic SSL
  - Edge network

## Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Community**: [vercel.com/community](https://vercel.com/community)
- **Project Issues**: Check GitHub Issues for this repository
