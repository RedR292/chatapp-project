import React, { useEffect, useMemo, useState } from 'react';
import './index.css';
import Header from './components/Header';
import ChatList from './components/ChatList';
import ChatWindow from './components/ChatWindow';

const SAMPLE = {
  contacts: [
    {
      id: 1,
      name: 'Alice',
      last: { text: 'See you soon!', time: '10:24' },
      messages: [
        { id: 1, text: 'Hi Alice!', time: '10:00', fromSelf: true },
        { id: 2, text: 'Hey! How are you?', time: '10:01' },
      ],
    },
    {
      id: 2,
      name: 'Bob',
      last: { text: 'Let me check', time: '09:11' },
      messages: [],
    },
    {
      id: 3,
      name: 'Design Team',
      last: { text: 'New assets uploaded', time: 'Yesterday' },
      messages: [],
    },
  ],
};

const STORAGE_KEY = 'chatapp_state_v1';

function nowTime() {
  return new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function App() {
  const [state, setState] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) {
      // ignore
    }
    return {
      contacts: SAMPLE.contacts,
      selectedId: SAMPLE.contacts[0].id,
      theme: 'light',
    };
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // ignore
    }
  }, [state]);

  useEffect(() => {
    const root = document.documentElement;
    if (state.theme === 'dark') root.classList.add('dark');
    else root.classList.remove('dark');
  }, [state.theme]);

  const contacts = state.contacts || [];
  const selected = useMemo(
    () =>
      contacts.find((c) => c.id === state.selectedId) || contacts[0] || null,
    [contacts, state.selectedId]
  );

  const selectChat = (contact) =>
    setState((s) => ({ ...s, selectedId: contact.id }));

  const sendMessage = (text) => {
    const time = nowTime();
    const msg = { id: Date.now(), text, time, fromSelf: true };
    setState((s) => {
      const contacts = s.contacts.map((c) => {
        if (c.id === s.selectedId) {
          const nextMessages = [...(c.messages || []), msg];
          return { ...c, messages: nextMessages, last: { text, time } };
        }
        return c;
      });
      return { ...s, contacts };
    });
  };

  const toggleTheme = () =>
    setState((s) => ({ ...s, theme: s.theme === 'dark' ? 'light' : 'dark' }));

  return (
    <div className="app-container min-h-screen flex flex-col bg-app">
      <Header onToggleTheme={toggleTheme} isDark={state.theme === 'dark'} />

      <div className="flex-1 flex overflow-hidden">
        <div className="hidden sm:block sm:w-80">
          <ChatList
            contacts={contacts}
            selectedId={state.selectedId}
            onSelect={selectChat}
          />
        </div>

        <div className="flex-1 flex flex-col">
          <ChatWindow
            contact={selected}
            messages={selected?.messages || []}
            onSend={sendMessage}
          />
        </div>
      </div>
    </div>
  );
}
