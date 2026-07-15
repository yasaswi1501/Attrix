# DOC-0003 — Design System Specification

| Field | Value |
|---|---|
| Product | Attrix |
| Specification Suite | Attrix Product Architecture & Engineering Specification |
| Acronym | APAES |
| Document ID | DOC-0003 |
| Level | Level 2 — Design System |
| Volume | Volume 2.1 — Visual Identity Guidelines |
| Version | 1.0 |
| Status | Approved Foundation |
| Owner | Chief Product Architect |
| Reviewer | Product Owner |
| Product Owner | Yasaswi Vadrevu |
| Repository | https://github.com/yasaswi1501/Attrix |
| Dependencies | None |
| Supersedes | None |
| Affected Scope | Entire Attrix product |
| Implementation Impact | Documentation only |
| Next Document | DOC-0004 — Component Library Specifications |

---

## Document Purpose

This document, **DOC-0003 — Design System Specification**, establishes the permanent visual identity, design tokens, and visualization principles for **Attrix**. All future pages, components, layouts, and charts must inherit from the definitions, grid scales, and color systems outlined here to maintain Stripe/Apple-level enterprise design quality.

---

## 1. Color Palette Tokens

To prevent visual clutter, Attrix uses a quiet, neutral color system. Saturated colors are used only to communicate specific data warnings or domain thresholds.

### Primary Layout Neutrals
- **App Canvas Background:** `#F5F5F7` (Apple Light Gray)
- **Primary Card Background:** `#FFFFFF` (Solid White)
- **Sidebar Background:** `#FBFBFD` (Off White Canvas)
- **Primary Text:** `#1D1D1F` (Charcoal/Graphite)
- **Secondary Text:** `#6E6E73` (Medium Gray)
- **Muted Text / Labels:** `#86868B` (Light Gray)
- **Borders & Dividers:** `rgba(0, 0, 0, 0.06)` (Soft Translucent Divider)
- **Chart Gridlines:** `rgba(0, 0, 0, 0.04)` (Ultra Soft Translucent Grid)

### Domain & Priority Accents
- **Retention State (Healthy):** `#2E7D5B` (Muted Forest Emerald)
- **Attention State (Warning):** `#C9792B` (Muted Amber)
- **Critical Risk State (Danger):** `#B54747` (Muted Crimson)
- **Accent Blue (Primary Action):** `#0071E3` (Apple Royal Blue)
- **Neutral Grey (Baseline lines):** `#8E8E93` (System Grey)

---

## 2. Typography Hierarchy

The platform inherits the standard sans-serif system font stack:
`'-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif'`

### Scale Definition
| Tier | Font Size | Weight | Line Height | Margin Bottom |
| :--- | :--- | :--- | :--- | :--- |
| **Hero Title** | 34px | 800 (Bold) | 1.1 | 6px |
| **Page Subtitle** | 15px | 400 (Regular) | 1.45 | 20px |
| **Section Title** | 22px | 700 (Bold) | 1.2 | 6px |
| **Card / KPI Title** | 11px | 600 (Semi-Bold) | 1.2 | 6px |
| **Metric Value** | 32px | 700 (Bold) | 1.15 | 4px |
| **Body / Paragraph** | 13.5px | 400 (Regular) | 1.55 | 10px |
| **Badges / Ticks** | 11.5px | 600 (Semi-Bold) | 1.2 | 0 |

---

## 3. Spacing, Rhythm, & Grids

- **Max Width Cap:** Cap the main visual content blocks at `1400px` (`max-width: 1400px !important`). Content must automatically center inside the desktop view.
- **Padding Bounds:** Main container elements must maintain `40px` left/right padding and `36px` top padding.
- **Card Margins:** Individual cards (`.apple-card`) have a fixed `20px` bottom margin to keep card grids separated.

---

## 4. Component Layout Specifications

### The `.apple-card` Canvas
- **Background:** `#FFFFFF`
- **Border Radius:** `14px`
- **Border Width:** `1px solid rgba(0, 0, 0, 0.06)`
- **Shadow:** `0 1px 2px rgba(0, 0, 0, 0.02)` (minimal weight shadow)
- **Hover Micro-Interaction:** Hovering over a card increases shadow to `0 8px 24px rgba(0, 0, 0, 0.04)` and elevates border color to `rgba(0, 0, 0, 0.12)` over a transition duration of `150ms`.

### Unified Buttons
- **Border Radius:** `8px`
- **Primary Color:** `#0071E3`
- **Secondary / Ghost Color:** `#FFFFFF` with `rgba(0, 0, 0, 0.08)` border.
- **Micro-Interaction:** Hover state shifts primary color to `#0077ED` over `150ms`. Active state darkens to `#0062C4`.

---

## 5. Chart Design Principles

- **Baseline Indicators:** Organizational benchmarks must be represented by dashed grey lines (`#8E8E93` or `#B54747`) with localized text annotations showing the delta.
- **Dynamic Grid Toggles:**
  - Vertical bar, scatter, and line charts show horizontal gridlines only.
  - Horizontal bar charts show vertical gridlines only.
- **Hover tooltips:** Tooltip frames are customized to feature solid white backgrounds, thin gray borders, and zero default Plotly metadata labels.
- **Hidden Modebar Actions:** All developer actions (zoom, pan, lasso, spikelines) are hidden, leaving only download and zoom resets visible.

---

## 6. Revision History

| Version | Date | Status | Authors | Change Description |
| :--- | :--- | :--- | :--- | :--- |
| **1.0.0** | 2026-07-15 | Approved | Chief Architect | Initial Design System Specification. |
