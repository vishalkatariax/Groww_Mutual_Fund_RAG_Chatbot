# MF FAQ Assistant - Frontend

React + TypeScript + Vite chat interface for the Mutual Fund FAQ Assistant.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm 9+
- Backend API running on `http://localhost:8000`

### Installation & Run

```bash
# Option 1: Use the setup script
cd ../../scripts
./start_frontend.sh

# Option 2: Manual setup
cd app/frontend
npm install
npm run dev
```

The frontend will be available at **http://localhost:3000**

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatWindow.tsx       # Main chat container with auto-scroll
│   │   ├── MessageBubble.tsx    # Individual message display (user/bot)
│   │   ├── SourceLink.tsx       # Clickable source citation
│   │   ├── DisclaimerBanner.tsx # Sticky disclaimer banner
│   │   ├── ExampleQuestions.tsx # Clickable question chips
│   │   └── InputBar.tsx         # Text input + send button
│   ├── hooks/
│   │   └── useChat.ts       # Chat state management & API integration
│   ├── services/
│   │   └── api.ts           # Backend API client (axios)
│   ├── types/
│   │   └── index.ts         # TypeScript interfaces
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Entry point
│   └── index.css            # Tailwind CSS + custom styles
├── index.html               # HTML template
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── postcss.config.js        # PostCSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies
```

## 🎨 Features

### UI Components

| Component | Description | Status |
|-----------|-------------|--------|
| **DisclaimerBanner** | Sticky top banner warning "Facts-only. No investment advice." | ✅ |
| **WelcomeSection** | Hero section with assistant introduction | ✅ |
| **ExampleQuestions** | 3 clickable question chips for quick start | ✅ |
| **ChatWindow** | Scrollable message list with auto-scroll | ✅ |
| **MessageBubble** | User (blue) and bot (white) message styling | ✅ |
| **SourceLink** | Clickable source URL with icon | ✅ |
| **InputBar** | Text input with character counter | ✅ |

### Key Features

- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **Real-time Chat** - Instant message display with loading states
- ✅ **Source Citations** - Every response includes clickable source links
- ✅ **Error Handling** - Graceful error messages for API failures
- ✅ **Loading Indicators** - Animated typing dots during processing
- ✅ **Auto-scroll** - Automatically scrolls to latest message
- ✅ **Clear Chat** - Button to reset conversation
- ✅ **Character Counter** - Shows query length (max 500 chars)
- ✅ **Keyboard Shortcuts** - Press Enter to send messages
- ✅ **Type Safety** - Full TypeScript support

## 🔧 Configuration

### API Proxy

The Vite dev server proxies API requests to the backend:

```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### Environment Variables

No environment variables needed for development. The proxy handles API routing.

For production, set:

```env
VITE_API_URL=http://your-backend-api:8000
```

## 📦 Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

The build output will be in `dist/` directory.

## 🎯 UI Requirements Checklist

As per ARCHITECTURE.md Section 6.3:

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Welcome message | Static hero section on initial load | ✅ |
| 3 example questions | Clickable chips that auto-submit | ✅ |
| Disclaimer banner | Sticky top banner, always visible | ✅ |
| Source links | Clickable URLs in each response | ✅ |
| Last updated date | Appended to every response | ✅ |
| Refusal responses | Styled differently (amber warning) | ✅ |
| Loading state | Typing indicator during generation | ✅ |
| Error handling | Graceful error messages | ✅ |
| Mobile responsive | Responsive layout via Tailwind | ✅ |

## 🔌 API Integration

The frontend communicates with these backend endpoints:

```typescript
POST /api/v1/chat
  Request:  { query: string, session_id?: string }
  Response: { answer, source_url, last_updated, is_refusal, query_type }

GET /api/v1/health
  Response: { status, vector_store_docs, last_ingestion }

GET /api/v1/schemes
  Response: { schemes: [{ name, category, url }] }
```

## 🎨 Styling

### Tailwind CSS Configuration

Custom color palette:

```javascript
colors: {
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    500: '#0ea5e9',   // Primary blue
    600: '#0284c7',   // Darker blue (buttons)
    700: '#0369a1',
  },
}
```

### Component Styling

- **User messages**: Blue background (`bg-primary-600`)
- **Bot messages**: White with border (`bg-white border-gray-200`)
- **Refusal messages**: Amber warning (`bg-amber-50 border-amber-200`)
- **Loading dots**: Animated bounce effect
- **Responsive**: Mobile-first design with max-width containers

## 🐛 Troubleshooting

### Backend Not Responding

**Error**: "Failed to send message"

**Solution**:
1. Ensure backend is running: `cd ../.. && python -m uvicorn app.main:app --reload`
2. Check backend health: `curl http://localhost:8000/api/v1/health`
3. Verify CORS is enabled on backend

### Port Already in Use

**Error**: "Port 3000 is already in use"

**Solution**:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
PORT=3001 npm run dev
```

### Dependencies Not Installing

**Error**: npm install fails

**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📝 Development Notes

### Adding New Components

1. Create component in `src/components/`
2. Export from component file
3. Import in `App.tsx` or parent component
4. Use Tailwind classes for styling

### Modifying API Calls

Edit `src/services/api.ts` to add/modify endpoints.

### Updating Types

Edit `src/types/index.ts` for new TypeScript interfaces.

## 🚀 Deployment

### Static Hosting (Netlify/Vercel)

```bash
npm run build

# Deploy dist/ directory to your hosting provider
```

### Docker Deployment

See root `Dockerfile` for frontend + backend combined deployment.

## 📄 License

Part of the MF FAQ Assistant project.
