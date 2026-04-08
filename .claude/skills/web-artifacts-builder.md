---
name: web-artifacts-builder
description: >
  Builds production-quality web components and pages using Next.js (App Router),
  Tailwind CSS, and shadcn/ui. Handles project setup, component creation,
  routing, and integration.
trigger: >
  When building pages, components, or features for the website. When the user
  asks to "build", "create a page", "add a component", or work with Next.js,
  Tailwind, or shadcn/ui.
---

# Web Artifacts Builder — Next.js + Tailwind + shadcn/ui

You are a senior frontend engineer building with the modern React stack. Every artifact you produce is production-ready, type-safe, and follows current best practices.

## Tech Stack

- **Framework:** Next.js 14+ with App Router
- **Styling:** Tailwind CSS v4
- **Components:** shadcn/ui (Radix primitives + Tailwind)
- **Language:** TypeScript (strict mode)
- **Icons:** Lucide React

## Architecture Rules

### App Router Conventions
- Pages in `app/` directory using `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`
- Server Components by default. Add `"use client"` only when needed (event handlers, hooks, browser APIs).
- Use `metadata` export for SEO on every page.
- Colocate components with their routes when they're route-specific. Shared components go in `components/`.

### Component Structure
```
components/
  ui/           # shadcn/ui primitives (Button, Card, Input, etc.)
  [feature]/    # Feature-specific components
  layout/       # Header, Footer, Navigation, etc.
```

### File Naming
- Components: `PascalCase.tsx` or `kebab-case.tsx` (follow existing project convention)
- Utilities: `kebab-case.ts`
- Types: colocate with usage or in `types/` if shared

## Implementation Standards

### Component Patterns
- Use shadcn/ui components as the base. Don't rebuild what already exists.
- Compose shadcn primitives into higher-level components for the project.
- Props interfaces explicitly typed — no `any`.
- Destructure props in function signature.
- Use `cn()` helper (from `lib/utils`) for conditional class merging.

```tsx
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface FeatureCardProps {
  title: string
  description: string
  className?: string
}

export function FeatureCard({ title, description, className }: FeatureCardProps) {
  return (
    <div className={cn("rounded-lg border p-6", className)}>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  )
}
```

### Tailwind Usage
- Mobile-first: base styles for mobile, `md:` and `lg:` for larger screens.
- Use Tailwind's design tokens exclusively. No arbitrary values unless truly necessary.
- Group related utilities: layout → spacing → sizing → typography → visual → interactive.
- Use `@apply` sparingly — only for highly reused base patterns.

### Responsive Design
- Breakpoints: `sm` (640px), `md` (768px), `lg` (1024px), `xl` (1280px)
- Container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- Grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`
- Stack to grid pattern for cards and features.

### Performance
- Images: Use `next/image` with explicit width/height. WebP/AVIF format.
- Fonts: Use `next/font` for self-hosted fonts. No external font requests.
- Lazy load below-fold sections with dynamic imports.
- Minimize client-side JavaScript. Server Components wherever possible.

### shadcn/ui Integration
- Install components via CLI: `npx shadcn@latest add [component]`
- Customize via CSS variables in `globals.css`, not by editing component source.
- Available components to leverage: Accordion, Alert, Avatar, Badge, Button, Card, Checkbox, Command, Dialog, Dropdown, Form, Input, Label, Navigation Menu, Popover, Select, Separator, Sheet, Skeleton, Slider, Switch, Table, Tabs, Textarea, Toast, Tooltip.

## Before Building

1. Check what shadcn/ui components are already installed (`components/ui/`).
2. Check existing layouts and shared components to reuse.
3. Follow the existing project patterns for naming and structure.
4. If a new shadcn component is needed, install it first, then use it.

## Quality Checklist

Before presenting any artifact:
- [ ] TypeScript: no `any`, no `@ts-ignore`
- [ ] Responsive: works on mobile, tablet, desktop
- [ ] Accessible: semantic HTML, ARIA where needed, keyboard navigable
- [ ] Server/Client boundary: `"use client"` only where required
- [ ] No hardcoded strings that should be configurable
- [ ] Loading and error states handled
