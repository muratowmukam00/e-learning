/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#3758F9',
        secondary: '#13C296',
        'blue-dark': '#2847D8',
        dark: '#090E34',
        'dark-2': '#1D2144',
        'dark-3': '#31374A',
        'dark-6': '#9CA3AF',
        'dark-700': '#171C35',
        'body-color': '#637381',
        'gray-1': '#F9FAFB',
        'gray-7': '#CED4DA',
      },
      boxShadow: {
        'testimonial': '0px 60px 120px -20px rgba(45, 74, 170, 0.1)',
        'pricing': '0px 39px 23px -27px rgba(0, 0, 0, 0.04)',
      }
    },
  },
  plugins: [],
}
