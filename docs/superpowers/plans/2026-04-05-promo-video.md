# Promo Video (Remotion) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A 15-second 1080×1920 (9:16) promo video for Rushmore built with Remotion — Clean & Premium style with 4 scenes: intro text, builder UI mockup, card montage, outro with logo + CTA. Exports as MP4 ready for X, Instagram, TikTok.

**Architecture:** Remotion project in `rushmore/remotion/`. Four scene components (`Intro`, `BuilderScene`, `CardMontage`, `Outro`) composed in `PromoVideo.tsx` using Remotion's `<Sequence>` API. Assets (card screenshots, logo) live in `remotion/public/`. Rendered to MP4 via `npx remotion render`.

**Tech Stack:** Remotion 4.x, React 18, TypeScript, Node.js 18+

---

## Prerequisites (before starting)

Before Task 1, capture these assets manually and place them in `rushmore/remotion/public/`:

| File | What to capture |
|------|----------------|
| `card-players.png` | Screenshot of a finished player card (full 1080×1920 or scaled) |
| `card-teams.png` | Screenshot of a finished team card |
| `card-bracket.png` | Screenshot of a finished bracket card |
| `logo.png` | Rushmore mountain logo (copy from `assets/og-image.png` or export clean) |

For card screenshots: build a card in the app, right-click the preview → Save Image.

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `remotion/` | Create dir | Remotion project root |
| `remotion/package.json` | Create | Dependencies + render scripts |
| `remotion/tsconfig.json` | Create | TypeScript config |
| `remotion/remotion.config.ts` | Create | Remotion config (format, fps) |
| `remotion/src/Root.tsx` | Create | Register PromoVideo composition |
| `remotion/src/compositions/PromoVideo.tsx` | Create | Main composition, sequences all scenes |
| `remotion/src/compositions/scenes/Intro.tsx` | Create | 0–3s: "Who's your Mt. Rushmore?" |
| `remotion/src/compositions/scenes/BuilderScene.tsx` | Create | 3–7s: builder UI mockup with animation |
| `remotion/src/compositions/scenes/CardMontage.tsx` | Create | 7–12s: 3 card images in cuts |
| `remotion/src/compositions/scenes/Outro.tsx` | Create | 12–15s: logo + URL + CTA |

---

### Task 1: Scaffold Remotion project

**Files:**
- Create: `remotion/package.json`
- Create: `remotion/tsconfig.json`
- Create: `remotion/remotion.config.ts`

- [ ] **Step 1: Create `remotion/` directory and install dependencies**

```bash
mkdir -p /Users/razor/projects/rushmore/remotion/src/compositions/scenes
mkdir -p /Users/razor/projects/rushmore/remotion/public
cd /Users/razor/projects/rushmore/remotion
npm init -y
npm install remotion @remotion/cli react react-dom
npm install --save-dev typescript @types/react @types/react-dom
```

- [ ] **Step 2: Create `remotion/package.json` scripts**

Edit `remotion/package.json` — replace the `scripts` section:

```json
{
  "name": "rushmore-promo",
  "version": "1.0.0",
  "scripts": {
    "preview": "npx remotion studio src/index.ts",
    "render": "npx remotion render src/index.ts PromoVideo out/promo.mp4 --codec=h264"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "remotion": "^4.0.0",
    "@remotion/cli": "^4.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  }
}
```

- [ ] **Step 3: Create `remotion/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "module": "commonjs",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "jsx": "react"
  },
  "include": ["src"]
}
```

- [ ] **Step 4: Create `remotion/remotion.config.ts`**

```typescript
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
```

- [ ] **Step 5: Create `remotion/src/index.ts`** (entry point for Remotion)

```typescript
import { registerRoot } from "remotion";
import { RemotionRoot } from "./Root";

registerRoot(RemotionRoot);
```

- [ ] **Step 6: Commit scaffold**

```bash
cd /Users/razor/projects/rushmore
git add remotion/
git commit -m "feat: scaffold Remotion project in remotion/"
```

---

### Task 2: Root + PromoVideo composition

**Files:**
- Create: `remotion/src/Root.tsx`
- Create: `remotion/src/compositions/PromoVideo.tsx`

- [ ] **Step 1: Create `remotion/src/Root.tsx`**

```typescript
import { Composition } from "remotion";
import { PromoVideo } from "./compositions/PromoVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PromoVideo"
        component={PromoVideo}
        durationInFrames={450}   // 15s @ 30fps
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
```

- [ ] **Step 2: Create `remotion/src/compositions/PromoVideo.tsx`**

```typescript
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
```

- [ ] **Step 3: Commit**

```bash
cd /Users/razor/projects/rushmore
git add remotion/src/
git commit -m "feat: add Root and PromoVideo composition skeleton"
```

---

### Task 3: Intro scene (0–3s)

**Files:**
- Create: `remotion/src/compositions/scenes/Intro.tsx`

- [ ] **Step 1: Create `Intro.tsx`**

```typescript
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const GOLD = "#c9a84c";
const WHITE = "#ebebf0";

export const Intro: React.FC = () => {
  const frame = useCurrentFrame(); // 0–89

  // Tagline fades in over frames 10–40
  const taglineOpacity = interpolate(frame, [10, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Tagline slides up slightly as it fades in
  const taglineY = interpolate(frame, [10, 40], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Gold divider fades in frames 35–60
  const dividerOpacity = interpolate(frame, [35, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Subtitle fades in frames 50–75
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
      {/* Main tagline */}
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

      {/* Gold divider */}
      <div
        style={{
          width: interpolate(frame, [35, 65], [0, 240], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          height: 2,
          backgroundColor: GOLD,
          opacity: dividerOpacity,
        }}
      />

      {/* Subtitle */}
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
```

- [ ] **Step 2: Preview in browser to verify Intro**

```bash
cd /Users/razor/projects/rushmore/remotion
npm run preview
```

Open `http://localhost:3001` (or the URL shown). Scrub to frame 0–89. Verify text fades in smoothly, gold divider grows left to right.

- [ ] **Step 3: Commit**

```bash
cd /Users/razor/projects/rushmore
git add remotion/src/compositions/scenes/Intro.tsx
git commit -m "feat: add Intro scene (0-3s) to promo video"
```

---

### Task 4: BuilderScene (3–7s)

**Files:**
- Create: `remotion/src/compositions/scenes/BuilderScene.tsx`

- [ ] **Step 1: Create `BuilderScene.tsx`**

This scene shows a mock-up of the Rushmore builder UI — a dark panel with player "chips" dropping into slots, animated from above.

```typescript
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
  const frame = useCurrentFrame(); // local to sequence, 0–119

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
      {/* Rank circle */}
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: "50%",
          background: `${color}33`,
          border: `1.5px solid ${color}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 16,
          fontWeight: 700,
          color: WHITE,
          fontFamily: "Arial Black, sans-serif",
          flexShrink: 0,
        }}
      />

      {/* Headshot placeholder */}
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

      {/* Name + team */}
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
  const frame = useCurrentFrame(); // 0–119

  // Panel fades in
  const panelOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Title fades in
  const titleOpacity = interpolate(frame, [5, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: DARK, padding: "120px 80px" }}>
      {/* Card title */}
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

      {/* Builder slots */}
      <div style={{ opacity: panelOpacity, display: "flex", flexDirection: "column", gap: 16 }}>
        {PLAYERS.map((p, i) => (
          <PlayerChip key={p.name} {...p} delay={i * 18 + 10} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Preview BuilderScene**

In browser at `http://localhost:3001`, scrub to frames 90–210. Verify player chips drop in one by one, smooth animation.

- [ ] **Step 3: Commit**

```bash
cd /Users/razor/projects/rushmore
git add remotion/src/compositions/scenes/BuilderScene.tsx
git commit -m "feat: add BuilderScene (3-7s) to promo video"
```

---

### Task 5: CardMontage (7–12s)

**Files:**
- Create: `remotion/src/compositions/scenes/CardMontage.tsx`

**Prerequisite:** `remotion/public/card-players.png`, `card-teams.png`, `card-bracket.png` must exist. If not, capture them now (see Prerequisites section at top of plan).

- [ ] **Step 1: Create `CardMontage.tsx`**

Each card is shown for 50 frames (~1.67s) with a quick fade transition between them.

```typescript
import React from "react";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame } from "remotion";

const CARDS = [
  { src: staticFile("card-players.png"), label: "YOUR PLAYERS" },
  { src: staticFile("card-teams.png"),   label: "YOUR TEAMS" },
  { src: staticFile("card-bracket.png"), label: "YOUR BRACKET" },
];

// Each card occupies 50 frames; transition overlap = 8 frames
const CARD_DURATION = 50;
const TRANSITION = 8;

export const CardMontage: React.FC = () => {
  const frame = useCurrentFrame(); // 0–149

  return (
    <AbsoluteFill style={{ backgroundColor: "#07080f" }}>
      {CARDS.map((card, i) => {
        const start = i * CARD_DURATION;
        const end = start + CARD_DURATION;

        // Fade in at start, fade out near end
        const opacity = interpolate(
          frame,
          [start, start + TRANSITION, end - TRANSITION, end],
          [0, 1, 1, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        // Subtle scale pulse
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
            {/* Label overlay at bottom */}
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
```

- [ ] **Step 2: Preview CardMontage**

In browser, scrub to frames 210–360. Verify all 3 card images cycle with fade transitions and labels appear at the bottom.

If card images are missing, a broken image will show — add the screenshots to `remotion/public/` first.

- [ ] **Step 3: Commit**

```bash
cd /Users/razor/projects/rushmore
git add remotion/src/compositions/scenes/CardMontage.tsx
git commit -m "feat: add CardMontage (7-12s) to promo video"
```

---

### Task 6: Outro (12–15s)

**Files:**
- Create: `remotion/src/compositions/scenes/Outro.tsx`

- [ ] **Step 1: Create `Outro.tsx`**

```typescript
import React from "react";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame } from "remotion";

const GOLD = "#c9a84c";
const WHITE = "#ebebf0";

export const Outro: React.FC = () => {
  const frame = useCurrentFrame(); // 0–89

  // Logo fades in
  const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // URL fades in after logo
  const urlOpacity = interpolate(frame, [18, 38], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // CTA fades in last
  const ctaOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Gold line grows under URL
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
      {/* Logo */}
      <div style={{ opacity: logoOpacity }}>
        <img
          src={staticFile("logo.png")}
          style={{ width: 160, height: 160, objectFit: "contain" }}
        />
      </div>

      {/* URL */}
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

        {/* Animated underline */}
        <div
          style={{
            margin: "12px auto 0",
            width: lineWidth,
            height: 2,
            backgroundColor: GOLD,
          }}
        />
      </div>

      {/* CTA */}
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
```

- [ ] **Step 2: Preview full video**

In browser, scrub through all 450 frames (0–15s). Verify all 4 scenes flow smoothly: Intro → Builder → Cards → Outro.

- [ ] **Step 3: Commit**

```bash
cd /Users/razor/projects/rushmore
git add remotion/src/compositions/scenes/Outro.tsx
git commit -m "feat: add Outro (12-15s) to promo video"
```

---

### Task 7: Render to MP4

**Files:**
- Create: `remotion/out/` (auto-created by render)

- [ ] **Step 1: Create output directory**

```bash
mkdir -p /Users/razor/projects/rushmore/remotion/out
```

- [ ] **Step 2: Render the video**

```bash
cd /Users/razor/projects/rushmore/remotion
npm run render
```

Expected: render progresses 0%→100%, ends with:
```
✓ Your video is ready. 450 frames rendered.
Output: /Users/razor/projects/rushmore/remotion/out/promo.mp4
```

- [ ] **Step 3: Verify the output**

```bash
open /Users/razor/projects/rushmore/remotion/out/promo.mp4
```

Check: 15 seconds, 9:16 format, smooth animations, readable text.

- [ ] **Step 4: Add `remotion/out/` to `.gitignore`**

Add to `/Users/razor/projects/rushmore/.gitignore`:
```
remotion/out/
remotion/node_modules/
```

- [ ] **Step 5: Final commit**

```bash
cd /Users/razor/projects/rushmore
git add .gitignore remotion/
git commit -m "feat: Remotion promo video complete — 15s 9:16 MP4"
```
