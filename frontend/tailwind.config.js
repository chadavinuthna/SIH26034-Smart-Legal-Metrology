/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#0A192F',
          dark: '#0F2537',
          blue: '#1E3A8A',
          lightBlue: '#E0E7FF',
          gold: '#B45309',
          goldLight: '#FEF3C7',
          accent: '#D97706',
          bg: '#F8FAFC',
          card: '#FFFFFF',
          border: '#E2E8F0',
          muted: '#64748B',
          text: '#0F172A',
        },
        pass: {
          DEFAULT: '#10B981',
          dark: '#059669',
          light: '#ECFDF5',
          border: '#A7F3D0',
          text: '#065F46',
        },
        fail: {
          DEFAULT: '#EF4444',
          dark: '#DC2626',
          light: '#FEF2F2',
          border: '#FECACA',
          text: '#991B1B',
        },
        review: {
          DEFAULT: '#F59E0B',
          dark: '#D97706',
          light: '#FFFBEB',
          border: '#FDE68A',
          text: '#92400E',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
