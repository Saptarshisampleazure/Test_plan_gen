/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: {
          950: '#070b14',
          900: '#0b1220',
          850: '#101827',
          800: '#162033',
        },
        cyanbrand: {
          400: '#22d3ee',
          500: '#06b6d4',
        },
      },
      boxShadow: {
        glow: '0 20px 60px rgba(34, 211, 238, 0.12)',
        panel: '0 18px 45px rgba(2, 6, 23, 0.45)',
      },
      backgroundImage: {
        'qa-grid':
          'linear-gradient(rgba(148,163,184,.06) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,.06) 1px, transparent 1px)',
      },
      animation: {
        'pulse-soft': 'pulseSoft 2.2s ease-in-out infinite',
      },
      keyframes: {
        pulseSoft: {
          '0%, 100%': { opacity: 0.7, transform: 'scale(1)' },
          '50%': { opacity: 1, transform: 'scale(1.04)' },
        },
      },
    },
  },
  plugins: [],
}
