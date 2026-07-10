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

export type WsStatus = "connecting" | "connected" | "disconnected";

export function useJarvis() {
  const [state, setState] = useState<OrbState>("idle");
  const [audioLevel, setAudioLevel] = useState(0);
  const [messages, setMessages] = useState<Message[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>(DEFAULT_INTEGRATIONS);
  const [wsStatus, setWsStatus] = useState<WsStatus>("connecting");

  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  // Stable setter — never changes reference
  const addMessage = useCallback((msg: Omit<Message, "id" | "timestamp">) => {
    setMessages((prev) => [...prev, { ...msg, id: makeId(), timestamp: new Date() }]);
  }, []);

  useEffect(() => {
    mountedRef.current = true;

    function openWs() {
      if (!mountedRef.current) return;

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;
      setWsStatus("connecting");

      ws.onopen = () => {
        if (!mountedRef.current) { ws.close(); return; }
        setWsStatus("connected");
        if (retryRef.current) { clearTimeout(retryRef.current); retryRef.current = null; }
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setWsStatus("disconnected");
        retryRef.current = setTimeout(openWs, 3000);
      };

      ws.onerror = () => {
        // onclose fires after onerror, handles retry
      };

      ws.onmessage = (e) => {
        if (!mountedRef.current) return;
        let data: Record<string, unknown>;
        try { data = JSON.parse(e.data); } catch { return; }
        switch (data.type) {
          case "state_change":   setState(data.state as OrbState); break;
          case "audio_level":   setAudioLevel(data.level as number); break;
          case "transcript":    addMessage({ role: "user", text: data.text as string }); break;
          case "tool_call":     addMessage({ role: "tool_call", text: JSON.stringify(data.args), toolName: data.tool as string }); break;
          case "tool_result":   addMessage({ role: "tool_result", text: data.result as string, toolName: data.tool as string }); break;
          case "response":      addMessage({ role: "assistant", text: data.text as string }); break;
          case "integration_status":
            setIntegrations((prev) =>
              prev.map((i) => i.name === data.name ? { ...i, status: data.status as IntegrationStatus } : i)
            );
            break;
        }
      };
    }

    openWs();

    fetch(`${API_URL}/integrations`)
      .then((r) => r.json())
      .then((list: { name: string; status: string }[]) => {
        if (!mountedRef.current) return;
        setIntegrations((prev) =>
          prev.map((i) => {
            const found = list.find((x) => x.name === i.name);
            return found ? { ...i, status: found.status as IntegrationStatus } : i;
          })
        );
      })
      .catch(() => {});

    return () => {
      mountedRef.current = false;
      if (retryRef.current) clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // intentionally empty — runs once on mount

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

  return { state, audioLevel, messages, integrations, wsStatus, sendText, connectIntegration, disconnectIntegration };
}
