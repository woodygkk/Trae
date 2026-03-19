/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1', // Indigo-500-ish
        secondary: '#f3f4f6', // Gray-100
      }
    },
  },
  plugins: [],
}
