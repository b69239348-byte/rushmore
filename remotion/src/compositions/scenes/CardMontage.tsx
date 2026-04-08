import React from "react";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame } from "remotion";

const CARDS = [
  { src: staticFile("card-players.png"), label: "YOUR PLAYERS" },
  { src: staticFile("card-teams.png"), label: "YOUR TEAMS" },
  { src: staticFile("card-bracket.png"), label: "YOUR BRACKET" },
];

const CARD_DURATION = 50;
const TRANSITION = 8;

export const CardMontage: React.FC = () => {
  const frame = useCurrentFrame(); // 0–149

  return (
    <AbsoluteFill style={{ backgroundColor: "#07080f" }}>
      {CARDS.map((card, i) => {
        const start = i * CARD_DURATION;
        const end = start + CARD_DURATION;

        const opacity = interpolate(
          frame,
          [start, start + TRANSITION, end - TRANSITION, end],
          [0, 1, 1, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        const scale = interpolate(
          frame,
          [start, start + TRANSITION],
          [1.04, 1.0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        if (opacity <= 0) return null;

        return (
          <AbsoluteFill key={card.src} style={{ opacity }}>
            <img
              src={card.src}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${scale})`,
              }}
            />
            <div
              style={{
                position: "absolute",
                bottom: 80,
                left: 0,
                right: 0,
                textAlign: "center",
              }}
            >
              <p
                style={{
                  fontFamily: "Arial Black, Impact, sans-serif",
                  fontSize: 40,
                  fontWeight: 900,
                  color: "rgba(235,235,240,0.85)",
                  margin: 0,
                  letterSpacing: 4,
                  textShadow: "0 2px 20px rgba(0,0,0,0.8)",
                }}
              >
                {card.label}
              </p>
            </div>
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};
