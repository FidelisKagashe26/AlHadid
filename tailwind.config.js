/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./templates/**/*.html",
    "./templates/**/**/*.html",
    "./**/*.py",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#155e2b",
          600: "#166534",
          700: "#14532d",
          800: "#0f3a22"
        },
        gold: {
          DEFAULT: "#d4af37",
          700: "#b08d1f"
        },
        ivory: "#faf8f1",
        darkbg: "#0b1612",
        darksurface: "#0f1f18",
        darkborder: "#153a2b",
        darktext: "#e6f4ee"
      },
      boxShadow: {
        soft: "0 8px 24px rgba(0,0,0,.08)"
      },
      borderRadius: {
        xl2: "14px"
      },
      fontFamily: {
        inter: ["Inter", "system-ui", "Arial", "sans-serif"],
        cairo: ["Cairo", "Inter", "system-ui", "Arial", "sans-serif"]
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
};
