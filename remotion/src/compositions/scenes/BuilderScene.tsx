import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const GOLD = "#c9a84c";
const DARK = "#07080f";
const SURFACE = "#0f1522";
const BORDER = "rgba(255,255,255,0.10)";
const WHITE = "#ebebf0";
const GRAY = "#8888a0";

const PLAYERS = [
  { name: "L. JAMES", team: "LAL", color: "#552583" },
  { name: "M. JORDAN", team: "CHI", color: "#CE1141" },
  { name: "K. BRYANT", team: "LAL", color: "#552583" },
  { name: "S. O'NEAL", team: "LAL", color: "#552583" },
];

const PlayerChip: React.FC<{ name: string; team: string; color: string; delay: number }> = ({
  name, team, color, delay,
}) => {
  const frame = useCurrentFrame();

  const enterY = interpolate(frame, [delay, delay + 20], [-80, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = interpolate(frame, [delay, delay + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        transform: `translateY(${enterY}px)`,
        opacity,
        display: "flex",
        alignItems: "center",
        gap: 16,
        background: SURFACE,
        border: `1px solid ${BORDER}`,
        borderLeft: `3px solid ${color}`,
        borderRadius: 12,
        padding: "16px 24px",
        width: "100%",
      }}
    >
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: "50%",
          background: `${color}33`,
          border: `1.5px solid ${color}`,
          flexShrink: 0,
        }}
      />
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: "50%",
          background: `${color}22`,
          border: `1.5px solid ${color}55`,
          flexShrink: 0,
        }}
      />
      <div style={{ flex: 1 }}>
        <p style={{ margin: 0, color: WHITE, fontSize: 28, fontWeight: 700, fontFamily: "Arial Black, sans-serif" }}>
          {name}
        </p>
        <p style={{ margin: 0, color: GRAY, fontSize: 20, fontFamily: "Arial, sans-serif" }}>
          {team}
        </p>
      </div>
    </div>
  );
};

export const BuilderScene: React.FC = () => {
  const frame = useCurrentFrame();

  const panelOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleOpacity = interpolate(frame, [5, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: DARK, padding: "120px 80px" }}>
      <div style={{ opacity: titleOpacity, marginBottom: 40 }}>
        <p
          style={{
            margin: 0,
            fontFamily: "Arial Black, Impact, sans-serif",
            fontSize: 56,
            fontWeight: 900,
            color: WHITE,
            textTransform: "uppercase",
            letterSpacing: 2,
          }}
        >
          MY MT. RUSHMORE
        </p>
        <p style={{ margin: "8px 0 0", color: GOLD, fontSize: 24, letterSpacing: 4, fontFamily: "Arial, sans-serif" }}>
          ▲ ALL-TIME GREATS
        </p>
      </div>

      <div style={{ opacity: panelOpacity, display: "flex", flexDirection: "column", gap: 16 }}>
        {PLAYERS.map((p, i) => (
          <PlayerChip key={p.name} {...p} delay={i * 18 + 10} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
