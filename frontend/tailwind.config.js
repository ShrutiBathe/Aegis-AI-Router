/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: '#0F172A',
          soft: '#141F38',
          deep: '#0A0F1D',
        },
        primary: {
          DEFAULT: '#3B82F6',
          soft: '#60A5FA',
        },
        secondary: {
          DEFAULT: '#8B5CF6',
          soft: '#A78BFA',
        },
        accent: '#22D3EE',
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
        ink: {
          DEFAULT: '#E2E8F0',
          muted: '#94A3B8',
          faint: '#64748B',
        },
        line: 'rgba(148,163,184,0.12)',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        card: '16px',
        chip: '999px',
      },
      backgroundImage: {
        'grad-primary': 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
        'grad-glow': 'radial-gradient(circle at 50% 0%, rgba(139,92,246,0.25), transparent 60%)',
      },
      boxShadow: {
        glass: '0 8px 32px rgba(0,0,0,0.35)',
        glow: '0 0 24px rgba(59,130,246,0.35)',
      },
      keyframes: {
        pulseNode: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(59,130,246,0.5)' },
          '50%': { boxShadow: '0 0 0 8px rgba(59,130,246,0)' },
        },
        flowDash: {
          to: { strokeDashoffset: -24 },
        },
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
      animation: {
        pulseNode: 'pulseNode 1.6s ease-in-out infinite',
        flowDash: 'flowDash 1s linear infinite',
        floatSlow: 'floatSlow 6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
