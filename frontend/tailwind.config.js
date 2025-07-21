/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-dark': '#2f2f2f',
        'brand-dark-2': '#1e1e1e',
        // Theme colors
        primary: '#1A1A1A',   // A very dark gray for the main content
        secondary: '#222222', // A darker gray for the sidebar
        'content-secondary': '#A0A0A0', // A dimmer gray for sidebar text and icons
        'border-primary': '#333333', // A subtle border color
      }
    },
  },
  plugins: [],
} 