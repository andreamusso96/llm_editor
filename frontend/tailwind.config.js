/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // This tells Tailwind to scan these files in your src folder
  ],
  theme: {
    extend: {}, // You can extend Tailwind's default theme here
  },
  plugins: [], // You can add Tailwind plugins here
}