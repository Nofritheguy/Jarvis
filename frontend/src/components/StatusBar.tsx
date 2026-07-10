"use client";

import clsx from "clsx";
import { OrbState } from "./NeuralOrb";

interface StatusBarProps {
  state: OrbState;
  sessionStart: Date | null;
}

const STATE_LABELS: Record<OrbState, string> = {
  idle: "GOTOWY",
  listening: "SŁUCHAM",
  thinking: "MYŚLĘ",
  speaking: "MÓWIĘ",
};

const STATE_COLORS: Record<OrbState, string> = {
  idle: "text-secondary",
  listening: "text-green-400",
  thinking: "text-purple-400",
  speaking: "text-secondary",
};

export default function StatusBar({ state, sessionStart }: StatusBarProps) {
  const sessionTime = sessionStart
    ? sessionStart.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" })
    : "--:--";

  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-textSub/20">
      <div className="flex items-center gap-3">
        <span className="font-display font-bold text-xl tracking-widest text-textMain">JARVIS</span>
        <span className="text-textSub font-mono text-xs">v2.0</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span
            className={clsx(
              "w-2 h-2 rounded-full",
              state === "idle" ? "bg-secondary" : "bg-green-400 animate-pulse"
            )}
          />
          <span className={clsx("font-mono text-xs font-semibold", STATE_COLORS[state])}>
            {STATE_LABELS[state]}
          </span>
        </div>
        <span className="text-textSub font-mono text-xs">sesja: {sessionTime}</span>
      </div>
    </div>
  );
}
