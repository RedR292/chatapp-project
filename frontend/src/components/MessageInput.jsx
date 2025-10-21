import React, { useState } from 'react';

export default function MessageInput({ onSend = () => {} }) {
  const [value, setValue] = useState('');

  function submit(e) {
    e.preventDefault();
    if (!value.trim()) return;
    onSend(value.trim());
    setValue('');
  }

  return (
    <form onSubmit={submit} className="p-3 bg-white border-t border-slate-100">
      <div className="flex gap-2 items-center">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Type a message"
          className="flex-1 p-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary hoverable"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-lg bg-primary text-white hoverable--accent"
        >
          Send
        </button>
      </div>
    </form>
  );
}
