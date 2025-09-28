/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'ai-primary': '#3B82F6',
        'ai-secondary': '#8B5CF6',
        'ai-accent': '#10B981',
        'ai-chat': '#F3F4F6',
        'ai-code': '#1F2937',
      },
      animation: {
        'typing': 'typing 1.5s infinite',
        'pulse-slow': 'pulse 3s infinite',
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}
