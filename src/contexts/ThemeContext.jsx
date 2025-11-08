import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext();

const STORAGE_KEY = 'chatapp_theme_v1';

// themeMode represents user preference: 'system' | 'light' | 'dark'
export function ThemeProvider({ children }) {
  const [mode, setMode] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return raw;
    } catch (e) {
      // ignore
    }
    // default to system if no value saved
    return 'system';
  });

  // derive effective theme from mode + system preference
  const getSystemPref = () =>
    window.matchMedia &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';

  useEffect(() => {
    // persist the user's chosen mode
    try {
      localStorage.setItem(STORAGE_KEY, mode);
    } catch (e) {
      // ignore
    }

    const effective = mode === 'system' ? getSystemPref() : mode;
    const root = document.documentElement;
    if (effective === 'dark') root.classList.add('dark');
    else root.classList.remove('dark');

    // if system mode, listen for changes
    let mql;
    if (mode === 'system' && window.matchMedia) {
      mql = window.matchMedia('(prefers-color-scheme: dark)');
      const handler = (e) => {
        const now = e.matches ? 'dark' : 'light';
        if (now === 'dark') root.classList.add('dark');
        else root.classList.remove('dark');
      };
      if (mql.addEventListener) mql.addEventListener('change', handler);
      else mql.addListener(handler);
      return () => {
        if (mql.removeEventListener) mql.removeEventListener('change', handler);
        else mql.removeListener(handler);
      };
    }
  }, [mode]);

  const toggle = () => setMode((m) => (m === 'dark' ? 'light' : 'dark'));

  const effective = mode === 'system' ? getSystemPref() : mode;

  return (
    <ThemeContext.Provider value={{ mode, setMode, toggle, effective }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}

export default ThemeContext;
