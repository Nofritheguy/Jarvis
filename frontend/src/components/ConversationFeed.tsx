"use client";

import { useEffect, useRef } from "react";
import clsx from "clsx";

export interface Message {
  id: string;
  role: "user" | "assistant" | "tool_call" | "tool_result";
  text: string;
  toolName?: string;
  timestamp: Date;
}

interface ConversationFeedProps {
  messages: Message[];
}

export default function ConversationFeed({ messages }: ConversationFeedProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col gap-3 overflow-y-auto h-full pr-1">
      {messages.length === 0 && (
        <p className="text-textSub font-mono text-sm mt-4">Czekam na polecenie...</p>
      )}
      {messages.map((msg) => (
        <div key={msg.id} className={clsx("flex flex-col gap-1", msg.role === "user" ? "items-end" : "items-start")}>
          {msg.role === "user" && (
            <div className="bg-primary/20 border border-primary/30 rounded-lg px-4 py-2 max-w-[80%]">
              <p className="font-mono text-sm text-textMain">{msg.text}</p>
            </div>
          )}
          {msg.role === "assistant" && (
            <div className="bg-secondary/10 border border-secondary/20 rounded-lg px-4 py-2 max-w-[85%]">
              <p className="font-mono text-sm text-textMain">{msg.text}</p>
            </div>
          )}
          {msg.role === "tool_call" && (
            <div className="flex items-center gap-2 text-textSub text-xs font-mono">
              <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <span>
                [{msg.toolName}] {msg.text}
              </span>
            </div>
          )}
          {msg.role === "tool_result" && (
            <div className="bg-textSub/10 border border-textSub/20 rounded px-3 py-1 max-w-[85%]">
              <p className="font-mono text-xs text-textSub">{msg.text}</p>
            </div>
          )}
          <span className="text-[10px] text-textSub/50 font-mono">
            {msg.timestamp.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" })}
          </span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
