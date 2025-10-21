import React from 'react';
import Message from './Message';
import MessageInput from './MessageInput';

export default function ChatWindow({
  contact,
  messages = [],
  onSend = () => {},
}) {
  return (
    <main className="flex-1 flex flex-col">
      <div className="p-4 border-b border-slate-100 flex items-center gap-3 bg-panel">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-medium">
          {contact?.name?.[0]}
        </div>
        <div>
          <div className="font-medium text-slate-800">{contact?.name}</div>
          <div className="text-sm text-slate-500">Online</div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4 bg-[length:100%_100%]">
        <div className="max-w-auto mx-4 space-y-2">
          {messages.map((msg) => (
            <Message key={msg.id} {...msg} />
          ))}
        </div>
      </div>

      <MessageInput onSend={onSend} />
    </main>
  );
}
