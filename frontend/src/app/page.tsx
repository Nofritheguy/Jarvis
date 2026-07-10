"use client";

import { useState, useRef, useEffect } from "react";
import dynamic from "next/dynamic";
import StatusBar from "@/components/StatusBar";
import ConversationFeed from "@/components/ConversationFeed";
import IntegrationPanel from "@/components/IntegrationPanel";
import { useJarvis } from "./useJarvis";
import clsx from "clsx";

const NeuralOrb = dynamic(() => import("@/components/NeuralOrb"), { ssr: false });

export default function Home() {
  const { state, audioLevel, messages, integrations, wsStatus, sendText, connectIntegration, disconnectIntegration } = useJarvis();
  const [input, setInput] = useState("");
  const [sessionStart, setSessionStart] = useState<Date | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { setSessionStart(new Date()); }, []);

  const handleSend = () => {
    const text = input.trim();
    if (!text || wsStatus !== "connected") return;
    sendText(text);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="flex flex-col h-screen bg-bg text-textMain overflow-hidden">
      <StatusBar state={state} sessionStart={sessionStart} wsStatus={wsStatus} />

      <div className="flex flex-1 overflow-hidden">
        {/* Left — Neural Orb */}
        <div className="w-[45%] flex flex-col items-center justify-center p-6 border-r border-textSub/20 relative">
          <div className="w-full h-[420px]">
            <NeuralOrb state={state} audioLevel={audioLevel} mode="particle" />
          </div>
          <div className="mt-4 flex items-center gap-2">
            <span className={clsx(
              "w-2 h-2 rounded-full",
              state === "listening" ? "bg-green-400 animate-pulse"
              : state === "thinking" ? "bg-purple-400 animate-ping"
              : state === "speaking" ? "bg-secondary animate-pulse"
              : "bg-secondary/40"
            )} />
            <span className="font-mono text-xs text-textSub uppercase tracking-widest">
              {state === "idle" ? 'Powiedz "Jarvis"'
                : state === "listening" ? "Słucham..."
                : state === "thinking" ? "Przetwarzam..."
                : "Mówię..."}
            </span>
          </div>
        </div>

        {/* Right — Conversation + Input */}
        <div className="flex-1 flex flex-col overflow-hidden p-6 gap-4">
          <div className="flex-1 overflow-hidden">
            <ConversationFeed messages={messages} />
          </div>

          {wsStatus === "disconnected" && (
            <p className="text-alert font-mono text-xs text-center">
              Brak połączenia z backendem — upewnij się że backend działa na porcie 8000
            </p>
          )}

          <div className="flex gap-2">
            <input
              ref={inputRef}
              disabled={wsStatus !== "connected"}
              className={clsx(
                "flex-1 border rounded-lg px-4 py-2 font-mono text-sm text-textMain placeholder-textSub/50 outline-none transition-colors",
                wsStatus === "connected"
                  ? "bg-textSub/10 border-textSub/30 focus:border-secondary/50"
                  : "bg-textSub/5 border-textSub/20 opacity-50 cursor-not-allowed"
              )}
              placeholder={wsStatus === "connecting" ? "Łączenie z backendem..." : wsStatus === "disconnected" ? "Brak połączenia" : "Wpisz polecenie..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button
              onClick={handleSend}
              disabled={wsStatus !== "connected"}
              className={clsx(
                "px-4 py-2 border rounded-lg font-mono text-sm transition-colors",
                wsStatus === "connected"
                  ? "bg-primary/20 border-primary/40 hover:bg-primary/30 text-primary"
                  : "bg-textSub/10 border-textSub/20 text-textSub opacity-50 cursor-not-allowed"
              )}
            >
              Wyślij
            </button>
          </div>
        </div>
      </div>

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
