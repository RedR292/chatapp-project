import React from 'react';

function Contact({ name, last, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left flex items-center gap-3 p-3 rounded-lg hoverable ${
        active ? 'bg-slate-100' : ''
      }`}
      aria-pressed={active}
    >
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-medium">
        {name[0]}
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-center">
          <div className="font-medium text-slate-800">{name}</div>
          <div className="text-xs text-slate-400">{last?.time}</div>
        </div>
        <div className="text-sm text-slate-500 truncate">{last?.text}</div>
      </div>
    </button>
  );
}

export default function ChatList({
  contacts = [],
  selectedId,
  onSelect = () => {},
}) {
  return (
    <aside className="w-full sm:w-80 border-r border-slate-100 bg-panel h-full">
      <div className="p-3 flex flex-col h-full">
        <div className="text-sm text-slate-500 mb-2">Chats</div>
        <div className="space-y-2 overflow-auto flex-1">
          {contacts.map((c) => (
            <Contact
              key={c.id}
              {...c}
              active={selectedId === c.id}
              onClick={() => onSelect(c)}
            />
          ))}
        </div>
      </div>
    </aside>
  );
}
