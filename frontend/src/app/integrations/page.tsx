"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import IntegrationCard, { Integration, IntegrationStatus } from "@/components/IntegrationCard";

const API_URL = "http://localhost:8000";

const INTEGRATION_META: Record<string, { label: string; icon: string; description: string; setup: string }> = {
  google_calendar: {
    label: "Google Calendar",
    icon: "📅",
    description: "Dostęp do kalendarza — eventy, przypomnienia, tworzenie spotkań.",
    setup: "Wymagany plik credentials.json z Google Cloud Console (Calendar API). Przy pierwszym połączeniu otworzy się przeglądarka do autoryzacji OAuth2.",
  },
  spotify: {
    label: "Spotify",
    icon: "🎵",
    description: "Sterowanie odtwarzaniem — play/pause, następny, wyszukiwanie, głośność.",
    setup: "Wymagane Client ID i Client Secret z developer.spotify.com. Ustaw zmienne SPOTIFY_CLIENT_ID i SPOTIFY_CLIENT_SECRET w .env.",
  },
  messenger: {
    label: "Messenger",
    icon: "💬",
    description: "Odczyt nieprzeczytanych i ostatnich konwersacji z Messengera.",
    setup: "⚠️ Używa Playwright (scraping). Przy pierwszym połączeniu otwiera przeglądarkę — zaloguj się ręcznie do Facebooka. Cookies są zapisywane lokalnie.",
  },
};

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/integrations`)
      .then((r) => r.json())
      .then((list: { name: string; status: string }[]) => {
        setIntegrations(
          list.map((i) => ({
            name: i.name,
            label: INTEGRATION_META[i.name]?.label ?? i.name,
            icon: INTEGRATION_META[i.name]?.icon ?? "🔌",
            status: i.status as IntegrationStatus,
          }))
        );
      })
      .catch(() => {
        setIntegrations(
          Object.entries(INTEGRATION_META).map(([name, meta]) => ({
            name,
            label: meta.label,
            icon: meta.icon,
            status: "disconnected" as IntegrationStatus,
          }))
        );
      });
  }, []);

  const connect = async (name: string) => {
    setIntegrations((p) => p.map((i) => (i.name === name ? { ...i, status: "connecting" } : i)));
    const r = await fetch(`${API_URL}/integrations/${name}/connect`, { method: "POST" });
    const data = await r.json();
    setIntegrations((p) =>
      p.map((i) => (i.name === name ? { ...i, status: data.error ? "error" : "connected" } : i))
    );
  };

  const disconnect = async (name: string) => {
    await fetch(`${API_URL}/integrations/${name}/disconnect`, { method: "POST" });
    setIntegrations((p) => p.map((i) => (i.name === name ? { ...i, status: "disconnected" } : i)));
  };

  return (
    <div className="min-h-screen bg-bg text-textMain p-8">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/" className="text-textSub hover:text-secondary font-mono text-sm transition-colors">
            ← Powrót
          </Link>
          <h1 className="font-display font-bold text-2xl tracking-widest">INTEGRACJE</h1>
        </div>

        <div className="flex flex-col gap-6">
          {Object.entries(INTEGRATION_META).map(([name, meta]) => {
            const integration = integrations.find((i) => i.name === name) ?? {
              name,
              label: meta.label,
              icon: meta.icon,
              status: "disconnected" as IntegrationStatus,
            };
            return (
              <div key={name} className="border border-textSub/20 rounded-xl p-6 flex gap-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl">{meta.icon}</span>
                    <h2 className="font-display font-semibold text-lg">{meta.label}</h2>
                  </div>
                  <p className="text-textSub text-sm font-mono mb-3">{meta.description}</p>
                  <div className="bg-textSub/5 border border-textSub/20 rounded-lg p-3">
                    <p className="text-xs font-mono text-textSub">{meta.setup}</p>
                  </div>
                </div>
                <div className="flex items-start pt-1">
                  <IntegrationCard
                    integration={integration}
                    onConnect={connect}
                    onDisconnect={disconnect}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
