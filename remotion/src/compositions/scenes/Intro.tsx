import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const GOLD = "#c9a84c";
const WHITE = "#ebebf0";

export const Intro: React.FC = () => {
  const frame = useCurrentFrame(); // 0–89

  const taglineOpacity = interpolate(frame, [10, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const taglineY = interpolate(frame, [10, 40], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const dividerWidth = interpolate(frame, [35, 65], [0, 240], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const dividerOpacity = interpolate(frame, [35, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const subtitleOpacity = interpolate(frame, [50, 75], [0, 1], {
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
        gap: 24,
      }}
    >
      <div
        style={{
          opacity: taglineOpacity,
          transform: `translateY(${taglineY}px)`,
          textAlign: "center",
          padding: "0 80px",
        }}
      >
        <p
          style={{
            fontFamily: "Arial Black, Impact, sans-serif",
            fontSize: 96,
            fontWeight: 900,
            color: WHITE,
            margin: 0,
            lineHeight: 1.1,
            textTransform: "uppercase",
            letterSpacing: "-2px",
          }}
        >
          Who's your
          <br />
          <span style={{ color: GOLD }}>Mt. Rushmore?</span>
        </p>
      </div>

      <div
        style={{
          width: dividerWidth,
          height: 2,
          backgroundColor: GOLD,
          opacity: dividerOpacity,
        }}
      />

      <p
        style={{
          opacity: subtitleOpacity,
          fontFamily: "Arial, sans-serif",
          fontSize: 32,
          color: GOLD,
          margin: 0,
          letterSpacing: "6px",
          textTransform: "uppercase",
        }}
      >
        ▲ RUSHMORE
      </p>
    </AbsoluteFill>
  );
};
