import React from 'react';

export function Message({ text, time, fromSelf = false }) {
  return (
    <div className={`flex ${fromSelf ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`${
          fromSelf ? 'bg-primary text-white' : 'bg-slate-100 text-slate-800'
        } max-w-[75%] p-3 rounded-lg my-1 hoverable`}
      >
        <div className="text-sm">{text}</div>
        <div className="text-xs text-slate-400 mt-1 text-right">{time}</div>
      </div>
    </div>
  );
}

export default Message;
