/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      colors: {
        bee: {
          yellow: "#f5c518",
          dark: "#0f0f13",
          card: "#1e1e28",
        },
      },
    },
  },
  plugins: [],
};
