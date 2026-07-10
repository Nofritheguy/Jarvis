"use client";

import IntegrationCard, { Integration } from "./IntegrationCard";

interface IntegrationPanelProps {
  integrations: Integration[];
  onConnect: (name: string) => void;
  onDisconnect: (name: string) => void;
}

export default function IntegrationPanel({ integrations, onConnect, onDisconnect }: IntegrationPanelProps) {
  return (
    <div className="border-t border-textSub/20 pt-3">
      <p className="text-xs font-display font-semibold text-textSub uppercase tracking-widest mb-3">
        Integracje
      </p>
      <div className="flex gap-3 overflow-x-auto pb-1">
        {integrations.map((int) => (
          <IntegrationCard
            key={int.name}
            integration={int}
            onConnect={onConnect}
            onDisconnect={onDisconnect}
          />
        ))}
      </div>
    </div>
  );
}
