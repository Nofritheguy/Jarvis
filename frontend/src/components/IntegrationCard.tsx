"use client";

import clsx from "clsx";

export type IntegrationStatus = "disconnected" | "connecting" | "connected" | "error";

export interface Integration {
  name: string;
  label: string;
  icon: string;
  status: IntegrationStatus;
  detail?: string;
}

interface IntegrationCardProps {
  integration: Integration;
  onConnect: (name: string) => void;
  onDisconnect: (name: string) => void;
}

const STATUS_COLORS: Record<IntegrationStatus, string> = {
  connected: "text-green-400",
  connecting: "text-yellow-400",
  disconnected: "text-textSub",
  error: "text-alert",
};

const STATUS_LABELS: Record<IntegrationStatus, string> = {
  connected: "Połączono",
  connecting: "Łączenie...",
  disconnected: "Rozłączono",
  error: "Błąd",
};

export default function IntegrationCard({ integration, onConnect, onDisconnect }: IntegrationCardProps) {
  const { name, label, icon, status, detail } = integration;

  return (
    <div
      className={clsx(
        "border rounded-xl p-4 flex flex-col gap-2 min-w-[180px]",
        status === "connected" ? "border-secondary/40 bg-secondary/5" : "border-textSub/30 bg-textSub/5"
      )}
    >
      <div className="flex items-center gap-2">
        <span className="text-2xl">{icon}</span>
        <span className="font-display font-semibold text-sm text-textMain">{label}</span>
      </div>
      <div className={clsx("flex items-center gap-1.5 text-xs font-mono", STATUS_COLORS[status])}>
        <span
          className={clsx(
            "w-1.5 h-1.5 rounded-full",
            status === "connected" ? "bg-green-400" : status === "connecting" ? "bg-yellow-400 animate-pulse" : "bg-textSub"
          )}
        />
        {STATUS_LABELS[status]}
      </div>
      {detail && <p className="text-xs text-textSub font-mono truncate">{detail}</p>}
      <button
        onClick={() => status === "connected" ? onDisconnect(name) : onConnect(name)}
        disabled={status === "connecting"}
        className={clsx(
          "mt-1 text-xs px-3 py-1 rounded border font-mono transition-colors",
          status === "connected"
            ? "border-alert/40 text-alert hover:bg-alert/10"
            : "border-secondary/40 text-secondary hover:bg-secondary/10",
          status === "connecting" && "opacity-50 cursor-not-allowed"
        )}
      >
        {status === "connected" ? "Odłącz" : "Połącz"}
      </button>
    </div>
  );
}
