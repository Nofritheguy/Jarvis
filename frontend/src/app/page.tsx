"use client";

import { useState, useRef, useEffect } from "react";
import dynamic from "next/dynamic";
import StatusBar from "@/components/StatusBar";
import ConversationFeed from "@/components/ConversationFeed";
import IntegrationPanel from "@/components/IntegrationPanel";
import { useJarvis } from "./useJarvis";

const NeuralOrb = dynamic(() => import("@/components/NeuralOrb"), { ssr: false });

export default function Home() {
  const { state, audioLevel, messages, integrations, sendText, connectIntegration, disconnectIntegration } = useJarvis();
  const [input, setInput] = useState("");
  const [sessionStart, setSessionStart] = useState<Date | null>(null);

  useEffect(() => {
    setSessionStart(new Date());
  }, []);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    sendText(text);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="flex flex-col h-screen bg-bg text-textMain overflow-hidden">
      <StatusBar state={state} sessionStart={sessionStart} />

      <div className="flex flex-1 overflow-hidden">
        {/* Left — Neural Orb */}
        <div className="w-[45%] flex flex-col items-center justify-center p-6 border-r border-textSub/20 relative">
          <div className="w-full h-[420px]">
            <NeuralOrb state={state} audioLevel={audioLevel} mode="particle" />
          </div>
          <div className="mt-4 flex items-center gap-2">
            <span
              className={
                state === "listening"
                  ? "w-2 h-2 bg-green-400 rounded-full animate-pulse"
                  : state === "thinking"
                  ? "w-2 h-2 bg-purple-400 rounded-full animate-ping"
                  : state === "speaking"
                  ? "w-2 h-2 bg-secondary rounded-full animate-pulse"
                  : "w-2 h-2 bg-secondary/40 rounded-full"
              }
            />
            <span className="font-mono text-xs text-textSub uppercase tracking-widest">
              {state === "idle"
                ? 'Powiedz "Jarvis"'
                : state === "listening"
                ? "Słucham..."
                : state === "thinking"
                ? "Przetwarzam..."
                : "Mówię..."}
            </span>
          </div>
        </div>

        {/* Right — Conversation + Input */}
        <div className="flex-1 flex flex-col overflow-hidden p-6 gap-4">
          <div className="flex-1 overflow-hidden">
            <ConversationFeed messages={messages} />
          </div>

          {/* Text input */}
          <div className="flex gap-2">
            <input
              ref={inputRef}
              className="flex-1 bg-textSub/10 border border-textSub/30 rounded-lg px-4 py-2 font-mono text-sm text-textMain placeholder-textSub/50 outline-none focus:border-secondary/50 transition-colors"
              placeholder="Wpisz polecenie..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button
              onClick={handleSend}
              className="px-4 py-2 bg-primary/20 border border-primary/40 hover:bg-primary/30 rounded-lg font-mono text-sm text-primary transition-colors"
            >
              Wyślij
            </button>
          </div>
        </div>
      </div>

      {/* Bottom — Integration panel */}
      <div className="px-6 pb-4">
        <IntegrationPanel
          integrations={integrations}
          onConnect={connectIntegration}
          onDisconnect={disconnectIntegration}
        />
      </div>
    </div>
  );
}
