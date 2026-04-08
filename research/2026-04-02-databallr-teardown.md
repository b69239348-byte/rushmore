# Site Teardown: databallr

**URL:** https://databallr.com  
**Platform:** React (Vite) + HeroUI + Tailwind CSS  
**Date analyzed:** 2026-04-02

---

## Tech Stack (Confirmed from Source)

| Technology | Evidence | Purpose |
|---|---|---|
| React | `index-Bd3WpDTc.js` enthält React-Runtime (Fiber, hooks, reconciler) | UI-Framework |
| Vite | Asset-Hashing im Dateinamen (`index-Bd3WpDTc.js`) | Build-Tool |
| HeroUI (NextUI) | `heroui-*` CSS-Variablen (`--heroui-primary`, `--heroui-border-width-medium` etc.) | Component Library |
| Tailwind CSS | Komplettes Utility-Class-System im CSS-Bundle | Styling |
| DM Sans | `font-family: 'DM Sans'` im `<head>` via Google Fonts | Primäre Schrift |
| Lato | `.font-numeric { font-family: Lato }` | Zahlen / Stats |
| Netlify | `netlify-rum-container` Script, deploy metadata | Hosting |
| Ahrefs Analytics | `analytics.ahrefs.com` Script | Web Analytics |

**Kein GSAP, kein ScrollTrigger, keine Scroll-Animationen** — rein React-komponentenbasiert.

---

## Design System

### Farben (CSS Custom Properties — HSL)

```css
:root {
  --background: 220 24% 14%;        /* #1b212c — Haupthintergrund */
  --foreground: 0 0% 98%;           /* #fafafa — Text */
  --card: 220 24% 18%;              /* Karten */
  --card-foreground: 0 0% 98%;
  --popover: 220 26% 22%;           /* Dropdowns */
  --primary: 42 100% 67%;           /* #F5C842 — Gold-Orange (Hauptakzent) */
  --primary-foreground: 220 24% 10%;
  --secondary: 198 93% 60%;         /* #4cc9f0 — Cyan (Sekundärakzent) */
  --secondary-foreground: 220 24% 10%;
  --muted: 220 20% 22%;
  --muted-foreground: 220 10% 72%;
  --accent: 220 20% 30%;
  --border: 220 18% 22%;
  --input: 220 20% 26%;
  --ring: 42 100% 67%;              /* Gleich wie Primary */
  --radius: 1rem;
}
```

### Zusätzliche Brand-Farben (Hex, aus dem CSS)

| Verwendung | Wert |
|---|---|
| Hintergrund dunkel | `#1D2432` |
| Hintergrund dunkler | `#2B2F35` |
| Primary Gold | `#F5C842` |
| Akzent Cyan | `#00E5FF` |
| Akzent Cyan (soft) | `#4cc9f0` |
| Akzent Magenta | `#f72585` |
| Akzent Lila | `#9b87f5` |

### Typografie

| Rolle | Font | Gewicht | Besonderheit |
|---|---|---|---|
| Primär (alles) | DM Sans | 400, 500, 700, 800 | Google Fonts |
| Numerisch / Stats | Lato | 400, 700 | `font-feature-settings: "tnum" "lnum"`, `letter-spacing: .03em` |
| Fallback | `ui-sans-serif, system-ui, sans-serif` | — | Standard-Stack |

### Spacing-System

Tailwind-Standard: `0 / .125rem / .25rem / .375rem / .5rem / .75rem / 1rem / 1.25rem / 1.5rem / 2rem / 2.5rem / 3rem / 6rem`

### Border-Radius

```css
--radius: 1rem;
/* Utility-Klassen: .rounded (.25rem), .rounded-lg (.5rem), .rounded-xl (.75rem), .rounded-2xl (1rem), .rounded-full */
```

---

## Animationen & Keyframes

```css
@keyframes appearance-in {
  0%   { opacity: 0; transform: scale(.95); }
  60%  { opacity: .75; transform: scale(1.05); }
  100% { opacity: 1; transform: scale(1); }
}

@keyframes blink {
  0%, 100% { opacity: .2; }
  20%       { opacity: 1; }
}

@keyframes drip-expand {
  0%   { opacity: .2; transform: scale(0); }
  100% { opacity: 0; transform: scale(2); }
}

@keyframes fade-out {
  0%   { opacity: 1; }
  100% { opacity: .15; }
}

@keyframes spin / spinner-spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  50% { opacity: .5; }
}

@keyframes ping {
  75%, 100% { transform: scale(2); opacity: 0; }
}

@keyframes sway {
  0%, 100% { transform: translate(0); }
  50%       { transform: translateY(-150%); }
}

@keyframes indeterminate-bar {
  0%   { transform: translate(-50%) scaleX(.2); }
  100% { transform: translate(100%) scaleX(1); }
}
```

Alle Animationen sind **HeroUI-Component-Animationen** (Loader, Spinner, Button-Ripple) — keine eigenen Page-Animationen.

---

## Was ist klonbar?

| Element | Klonbarkeit | Aufwand |
|---|---|---|
| **Design-Token-System** (Farben, Radius, Spacing) | ✅ Direkt übertragbar | Niedrig |
| **HeroUI-Component-Library** | ✅ Open Source, npm installierbar | Niedrig |
| **Dark Theme Setup** | ✅ Identisch mit unserem Setup möglich | Niedrig |
| **Zahlen-Font-Trick** (Lato + tnum/lnum) | ✅ Sofort nutzbar | Minimal |
| **Gold/Orange Primary + Cyan Secondary** | ✅ Exakt kopierbar als CSS vars | Minimal |
| **Karten-Layout-Patterns** | ✅ Standard HeroUI Cards | Niedrig |
| **Daten-Tabellen** | ✅ HeroUI Table-Komponenten | Mittel |

---

## Empfohlener Stack (wenn man databallr nachbauen will)

```bash
npm install @heroui/react tailwindcss framer-motion
```

- **React + Vite** — gleich wie databallr
- **HeroUI** — alle Komponenten (Table, Card, Modal, Tabs, Dropdown, Badge)
- **Tailwind CSS** — Utility-Klassen
- **DM Sans + Lato** — Google Fonts

---

## Direkt nutzbare Erkenntnisse für Rushmore

1. **Farb-Token kopieren**: Das `--primary: 42 100% 67%` (Gold) passt sehr gut zu unserem Orange-Akzent. Die ganze HSL-Variablen-Struktur ist 1:1 übertragbar.

2. **Zahlen-Schrift-Trick**: `.font-numeric { font-family: Lato; font-feature-settings: "tnum" "lnum"; letter-spacing: .03em; }` — für alle Stats/Zahlen in unseren Player-Cards übernehmen.

3. **HeroUI-Library**: Falls wir Table, Modal, Tabs, Dropdown noch nicht haben — databallr nutzt HeroUI vollständig. Lohnt sich als Referenz was gut aussieht.

4. **Kein Scroll-Magic**: Databallr macht nichts besonders kompliziertes — reines React mit guter Component-Library. Wir müssen da nichts "nachjagen".

---

## Notes

- Die JS-Datei ist das vollständige React-Bundle — kein Code-Splitting sichtbar. Alles in einer Datei.
- Keine eigenen Animations-Libraries (kein GSAP, kein Framer Motion sichtbar).
- Font-Loading mit `onload`-Trick für Performance (non-blocking) — können wir übernehmen.
- HeroUI verwendet eigene CSS-Custom-Properties mit `--heroui-` Prefix parallel zu Tailwind.
