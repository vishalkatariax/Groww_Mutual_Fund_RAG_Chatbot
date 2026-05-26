/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Stitch RAG Chat UI Design System Colors
        background: {
          DEFAULT: '#10141a', // Deep navy-black
          dim: '#10141a',
          bright: '#353940',
          low: '#0a0e14',
        },
        surface: {
          DEFAULT: '#1c2026',
          low: '#181c22',
          container: '#161B22', // Card background
          high: '#262a31',
          highest: '#31353c',
          tint: '#c6c0ff',
        },
        primary: {
          DEFAULT: '#5B4DCF', // Primary action color
          container: '#5b4dcf',
          fixed: '#e4dfff',
          fixedDim: '#c6c0ff',
          onFixed: '#150066',
          onFixedVariant: '#3f2db3',
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#5B4DCF',
          600: '#4B3DBF',
          700: '#3B2DAF',
        },
        secondary: {
          DEFAULT: '#bfc6db',
          container: '#42495a',
        },
        tertiary: {
          DEFAULT: '#a2c9ff',
          container: '#0063af',
        },
        border: {
          DEFAULT: '#30363D', // Subtle border
          variant: '#474554',
          outline: '#928f9f',
        },
        text: {
          primary: '#E6EDF3', // Off-white for primary text
          secondary: '#8B949E', // Muted gray for secondary text
        },
        functional: {
          success: '#58A6FF', // Azure for links/success
          error: '#F85149',
          warning: '#D29922',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      fontSize: {
        'headline-lg': ['24px', { lineHeight: '32px', letterSpacing: '-0.02em', fontWeight: '600' }],
        'headline-md': ['20px', { lineHeight: '28px', letterSpacing: '-0.01em', fontWeight: '600' }],
        'body-lg': ['16px', { lineHeight: '24px', fontWeight: '400' }],
        'body-md': ['14px', { lineHeight: '20px', fontWeight: '400' }],
        'label-lg': ['14px', { lineHeight: '20px', letterSpacing: '0.01em', fontWeight: '600' }],
        'label-md': ['12px', { lineHeight: '16px', letterSpacing: '0.02em', fontWeight: '500' }],
      },
      borderRadius: {
        'sm': '0.25rem',
        'DEFAULT': '0.5rem',
        'md': '0.75rem',
        'lg': '1rem',
        'xl': '1.5rem',
        'full': '9999px',
      },
      spacing: {
        'gutter': '16px',
        'margin-desktop': '24px',
        'margin-mobile': '16px',
      },
      maxWidth: {
        'chat': '800px',
      },
    },
  },
  plugins: [],
}
