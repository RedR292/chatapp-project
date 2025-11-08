import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

export default function Header({
  title = 'ChatApp',
  subtitle = 'Light & modern',
}) {
  const { mode, effective, toggle } = useTheme();

  return (
    <header className="flex items-center justify-between p-4 bg-panel shadow-sm">
      <div>
        <h1 className="text-xl font-semibold text-slate-800">{title}</h1>
        <p className="text-sm text-slate-500">{subtitle}</p>
      </div>
      <div className="flex items-center gap-3">
        <button
          className="px-3 py-1 text-sm rounded-md bg-primary text-white hoverable"
          aria-label="New chat"
        >
          New Chat
        </button>
        <button
          onClick={toggle}
          aria-pressed={effective === 'dark'}
          className="p-2 rounded-md bg-slate-100 text-slate-600 hoverable"
          aria-label="Toggle theme"
        >
          {effective === 'dark' ? '☀️ Light' : '🌙 Dark'}
          {mode === 'system' ? ' · System' : ''}
        </button>
      </div>
    </header>
  );
}
