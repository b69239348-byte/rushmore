import React from "react";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame } from "remotion";

const GOLD = "#c9a84c";
const WHITE = "#ebebf0";

export const Outro: React.FC = () => {
  const frame = useCurrentFrame(); // 0–89

  const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const urlOpacity = interpolate(frame, [18, 38], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const ctaOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const lineWidth = interpolate(frame, [25, 55], [0, 280], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#07080f",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        gap: 32,
      }}
    >
      <div style={{ opacity: logoOpacity }}>
        <img
          src={staticFile("logo.png")}
          style={{ width: 160, height: 160, objectFit: "contain" }}
        />
      </div>

      <div style={{ opacity: urlOpacity, textAlign: "center" }}>
        <p
          style={{
            fontFamily: "Arial Black, Impact, sans-serif",
            fontSize: 72,
            fontWeight: 900,
            color: WHITE,
            margin: 0,
            letterSpacing: -1,
          }}
        >
          RUSHMORE<span style={{ color: GOLD }}>.APP</span>
        </p>
        <div
          style={{
            margin: "12px auto 0",
            width: lineWidth,
            height: 2,
            backgroundColor: GOLD,
          }}
        />
      </div>

      <p
        style={{
          opacity: ctaOpacity,
          fontFamily: "Arial, sans-serif",
          fontSize: 36,
          color: "rgba(235,235,240,0.6)",
          margin: 0,
          letterSpacing: 3,
          textTransform: "uppercase",
        }}
      >
        Build yours.
      </p>
    </AbsoluteFill>
  );
};
