"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { OrbState } from "@/components/NeuralOrb";
import { Message } from "@/components/ConversationFeed";
import { Integration, IntegrationStatus } from "@/components/IntegrationCard";

const WS_URL = "ws://localhost:8000/ws";
const API_URL = "http://localhost:8000";

const DEFAULT_INTEGRATIONS: Integration[] = [
  { name: "google_calendar", label: "Google Calendar", icon: "📅", status: "disconnected" },
  { name: "spotify", label: "Spotify", icon: "🎵", status: "disconnected" },
  { name: "messenger", label: "Messenger", icon: "💬", status: "disconnected" },
];

function makeId() {
  return Math.random().toString(36).slice(2);
}

export function useJarvis() {
  const [state, setState] = useState<OrbState>("idle");
  const [audioLevel, setAudioLevel] = useState(0);
  const [messages, setMessages] = useState<Message[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>(DEFAULT_INTEGRATIONS);
  const wsRef = useRef<WebSocket | null>(null);

  const addMessage = useCallback((msg: Omit<Message, "id" | "timestamp">) => {
    setMessages((prev) => [...prev, { ...msg, id: makeId(), timestamp: new Date() }]);
  }, []);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      switch (data.type) {
        case "state_change":
          setState(data.state as OrbState);
          break;
        case "audio_level":
          setAudioLevel(data.level);
          break;
        case "transcript":
          addMessage({ role: "user", text: data.text });
          break;
        case "tool_call":
          addMessage({ role: "tool_call", text: JSON.stringify(data.args), toolName: data.tool });
          break;
        case "tool_result":
          addMessage({ role: "tool_result", text: data.result, toolName: data.tool });
          break;
        case "response":
          addMessage({ role: "assistant", text: data.text });
          break;
        case "integration_status":
          setIntegrations((prev) =>
            prev.map((i) => (i.name === data.name ? { ...i, status: data.status as IntegrationStatus } : i))
          );
          break;
      }
    };

    // Load integration statuses
    fetch(`${API_URL}/integrations`)
      .then((r) => r.json())
      .then((list: { name: string; status: string }[]) => {
        setIntegrations((prev) =>
          prev.map((i) => {
            const found = list.find((x) => x.name === i.name);
            return found ? { ...i, status: found.status as IntegrationStatus } : i;
          })
        );
      })
      .catch(() => {});

    return () => ws.close();
  }, [addMessage]);

  const sendText = useCallback((text: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "user_text", text }));
    }
  }, []);

  const connectIntegration = useCallback(async (name: string) => {
    setIntegrations((prev) => prev.map((i) => (i.name === name ? { ...i, status: "connecting" } : i)));
    await fetch(`${API_URL}/integrations/${name}/connect`, { method: "POST" });
  }, []);

  const disconnectIntegration = useCallback(async (name: string) => {
    await fetch(`${API_URL}/integrations/${name}/disconnect`, { method: "POST" });
    setIntegrations((prev) => prev.map((i) => (i.name === name ? { ...i, status: "disconnected" } : i)));
  }, []);

  return { state, audioLevel, messages, integrations, sendText, connectIntegration, disconnectIntegration };
}
