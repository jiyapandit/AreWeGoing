/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"DM Serif Display"', "serif"],
        sans: ['Inter', "system-ui", "-apple-system", "Segoe UI", "Roboto", "Arial"],
      },
      boxShadow: {
        glass: "0 20px 70px rgba(0,0,0,0.14)",
      },
    },
  },
  plugins: [],
};
