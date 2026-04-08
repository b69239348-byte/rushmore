import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { Intro } from "./scenes/Intro";
import { BuilderScene } from "./scenes/BuilderScene";
import { CardMontage } from "./scenes/CardMontage";
import { Outro } from "./scenes/Outro";

// Frame layout @ 30fps:
// Intro:         0–90   (3s)
// BuilderScene:  90–210 (4s)
// CardMontage:   210–360 (5s)
// Outro:         360–450 (3s)

export const PromoVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#07080f" }}>
      <Sequence from={0} durationInFrames={90}>
        <Intro />
      </Sequence>
      <Sequence from={90} durationInFrames={120}>
        <BuilderScene />
      </Sequence>
      <Sequence from={210} durationInFrames={150}>
        <CardMontage />
      </Sequence>
      <Sequence from={360} durationInFrames={90}>
        <Outro />
      </Sequence>
    </AbsoluteFill>
  );
};
