module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#4f46e5',
        accent: '#06b6d4',
        bg: '#f7fafc',
        panel: '#ffffff',
      },
    },
  },
  plugins: [
    function ({ addUtilities }) {
      const newUtils = {
        '.bg-panel': { 'background-color': 'var(--panel)' },
        '.hoverable': {
          transition: 'background-color 160ms ease, transform 120ms ease',
        },
        '.hoverable--accent': {
          transition: 'background-color 160ms ease, transform 120ms ease',
        },
      };
      addUtilities(newUtils, { variants: ['responsive', 'hover', 'focus'] });
    },
  ],
};
