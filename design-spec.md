# Design Specification - AI Agent Management Platform

**Style**: Dark Mode First  
**Version**: 1.0  
**Target Audience**: Developers, technical teams, power users (20-40)  
**Last Updated**: 2026-02-22

---

## 1. Direction & Rationale

### Design Essence

This platform embraces **dark mode as the primary interface**, optimized for extended screen time and low-light environments typical of developer workflows. The aesthetic combines **pure blacks (#000) for OLED efficiency** with **dual vibrant accents** (electric blue + emerald green) that create high-energy focal points against the deep backgrounds. This is a technical tool for power users—prioritizing focus, efficiency, and visual clarity over decorative elements.

**Visual Strategy**: Depth through layered surface elevation (not shadows), vibrant saturated accents for action items, high contrast text (15.2:1 ratio), and glowing interactive states. The design supports **right-to-left (RTL) layouts for Arabic**, with mirrored navigation and text alignment.

**Reference Examples**: VS Code dark theme, GitHub's dark interface, Vercel dashboard, Linear app.

---

## 2. Design Tokens

### 2.1 Color Palette

#### Background System (90% Dark Surfaces)

| Token | Value | Usage | Contrast |
|-------|-------|-------|----------|
| `bg-pure-black` | `#000000` | OLED optimization, hero sections, sidebars | - |
| `bg-base` | `#0a0a0a` | Main application background | - |
| `bg-elevated` | `#141414` | Cards, panels, elevated surfaces | +10% from base |
| `bg-hover` | `#1e1e1e` | Interactive states, active elements | +20% from base |
| `bg-modal` | `#282828` | Modals, tooltips, highest elevation | +30% from base |

#### Text Colors (High Contrast)

| Token | Value | Usage | WCAG Ratio on `#0a0a0a` |
|-------|-------|-------|-------------------------|
| `text-primary` | `#e4e4e7` (zinc-200) | Headlines, primary content | 15.2:1 AAA |
| `text-secondary` | `#a1a1aa` (zinc-400) | Descriptions, labels | 8.9:1 AAA |
| `text-tertiary` | `#71717a` (zinc-500) | Captions, timestamps | 5.2:1 AA |
| `text-inverse` | `#0a0a0a` | Text on accent backgrounds | - |

#### Accent Colors (10% Vibrant)

| Token | Value | Usage | Contrast |
|-------|-------|-------|----------|
| `accent-primary` | `#3b82f6` (blue-500) | Primary CTAs, links, focus states | 8.6:1 AAA |
| `accent-primary-hover` | `#60a5fa` (blue-400) | Hover states | 10.1:1 AAA |
| `accent-primary-glow` | `rgba(59, 130, 246, 0.5)` | Glow effects | - |
| `accent-secondary` | `#10b981` (emerald-500) | Success states, secondary actions | 9.2:1 AAA |
| `accent-secondary-hover` | `#34d399` (emerald-400) | Hover states | 11.8:1 AAA |
| `accent-secondary-glow` | `rgba(16, 185, 129, 0.5)` | Glow effects | - |

#### Semantic Colors

| Token | Value | Usage |
|-------|-------|-------|
| `semantic-success` | `#10b981` (emerald-500) | Success messages, completed states |
| `semantic-warning` | `#f59e0b` (amber-500) | Warnings, cautionary states |
| `semantic-error` | `#ef4444` (red-500) | Errors, destructive actions |
| `semantic-info` | `#3b82f6` (blue-500) | Information, neutral notifications |

#### Border Colors

| Token | Value | Usage |
|-------|-------|-------|
| `border-subtle` | `rgba(255, 255, 255, 0.1)` | Card borders, dividers |
| `border-moderate` | `rgba(255, 255, 255, 0.15)` | Hover borders, active states |
| `border-strong` | `rgba(255, 255, 255, 0.2)` | Focus outlines, emphasized borders |

### 2.2 Typography

#### Font Families

| Token | Stack | Usage |
|-------|-------|-------|
| `font-primary` | `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | UI text, headings |
| `font-mono` | `'JetBrains Mono', 'Fira Code', 'Courier New', monospace` | Code blocks, technical data |

#### Font Sizes (Desktop)

| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `text-hero` | `48px` | `1.1` (53px) | Hero headlines |
| `text-h1` | `36px` | `1.2` (43px) | Page titles |
| `text-h2` | `28px` | `1.2` (34px) | Section headers |
| `text-h3` | `20px` | `1.3` (26px) | Card titles, subsections |
| `text-body-lg` | `18px` | `1.6` (29px) | Intro paragraphs |
| `text-body` | `16px` | `1.5` (24px) | Standard body text |
| `text-sm` | `14px` | `1.5` (21px) | Labels, captions |
| `text-code` | `14px` | `1.4` (20px) | Code snippets |

#### Font Weights

| Token | Value | Usage |
|-------|-------|-------|
| `font-regular` | `400` | Body text (lighter for dark mode) |
| `font-medium` | `500` | Emphasized text |
| `font-semibold` | `600` | Subheadings, buttons |
| `font-bold` | `700` | Headlines |

#### Letter Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `tracking-tight` | `-0.02em` | Large headlines |
| `tracking-normal` | `0` | Body text |
| `tracking-wide` | `0.01em` | Small text, labels |

### 2.3 Spacing (8-Point Grid)

| Token | Value | Usage |
|-------|-------|-------|
| `spacing-1` | `4px` | Icon padding |
| `spacing-2` | `8px` | Inline element gaps |
| `spacing-3` | `12px` | Compact spacing |
| `spacing-4` | `16px` | Standard element gaps |
| `spacing-6` | `24px` | Card padding (compact) |
| `spacing-8` | `32px` | Card padding (standard) |
| `spacing-12` | `48px` | Section margins |
| `spacing-16` | `64px` | Large section spacing |
| `spacing-20` | `80px` | Hero padding |
| `spacing-32` | `128px` | Extra large spacing |

### 2.4 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | `8px` | Buttons, tags |
| `radius-md` | `12px` | Cards, inputs |
| `radius-lg` | `16px` | Modals, large cards |
| `radius-full` | `9999px` | Pills, avatars |

### 2.5 Shadows & Glows

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-card` | `0 0 0 1px rgba(255,255,255,0.05), 0 4px 12px rgba(0,0,0,0.5)` | Elevated cards |
| `shadow-modal` | `0 0 0 1px rgba(255,255,255,0.1), 0 8px 24px rgba(0,0,0,0.6)` | Modals, dropdowns |
| `glow-primary` | `0 0 20px rgba(59,130,246,0.5), 0 0 40px rgba(59,130,246,0.3)` | Primary button hover |
| `glow-secondary` | `0 0 20px rgba(16,185,129,0.5), 0 0 40px rgba(16,185,129,0.3)` | Secondary button hover |
| `glow-icon` | `drop-shadow(0 0 8px rgba(59,130,246,0.6))` | Interactive icon hover |

### 2.6 Animation

| Token | Value | Usage |
|-------|-------|-------|
| `duration-fast` | `150ms` | Button hover, icon changes |
| `duration-normal` | `250ms` | Card transitions |
| `duration-slow` | `400ms` | Modals, panels |
| `easing-default` | `ease-out` | General animations |
| `easing-sharp` | `cubic-bezier(0.4, 0.0, 0.2, 1)` | Sharp transitions |

---

## 3. Component Specifications

### 3.1 Button (Primary & Secondary)

**Primary Button (Electric Blue Accent)**
- **Structure**: Height 48px, Padding 16-32px horizontal, Radius 12px
- **Typography**: font-semibold (600), 16px, letter-spacing 0
- **Colors**: Background `accent-primary` (#3b82f6), Text white (#ffffff)
- **States**:
  - Default: Background #3b82f6, no border
  - Hover: Brightness 110%, add `glow-primary` (0 0 20px blue glow)
  - Active: Brightness 95%, scale(0.98)
  - Focus: `border-strong` outline, 2px offset
  - Disabled: Opacity 40%, cursor not-allowed
- **Note**: Use for primary actions (Create Agent, Deploy, Save). Max 1-2 per screen.

**Secondary Button (Emerald Green Accent)**
- **Structure**: Same dimensions as primary
- **Typography**: Same as primary
- **Colors**: Background transparent, Border 2px solid `accent-secondary` (#10b981), Text #10b981
- **States**:
  - Default: Outlined with emerald border
  - Hover: Background #10b981, Text white, add `glow-secondary`
  - Active: Background brightness 90%, scale(0.98)
  - Focus: Same as primary
  - Disabled: Same as primary
- **Note**: Use for secondary actions (Cancel, View Details). Provides visual hierarchy.

### 3.2 Card (Elevated Surface)

**Structure**: Padding 32-40px, Radius 16px, Background `bg-elevated` (#141414)
- **Visual Treatment**: 
  - Border: 1px solid `border-subtle` (rgba(255,255,255,0.1))
  - Shadow: `shadow-card` (subtle elevation glow)
- **States**:
  - Default: Background #141414, border subtle
  - Hover: Background `bg-hover` (#1e1e1e), border `border-moderate` (rgba(255,255,255,0.15))
  - Active: Background #1e1e1e, border `border-strong`
- **Content Pattern**:
  - Title: `text-h3` (20px semibold), color `text-primary`
  - Description: `text-body` (16px regular), color `text-secondary`
  - Gap: 16px between title and description
- **Note**: Use for agent cards, dashboard panels, settings sections. Minimum 32px padding for premium feel.

### 3.3 Input Field

**Structure**: Height 48px, Padding 12-16px, Radius 12px
- **Typography**: font-regular (400), 16px
- **Colors**:
  - Background: `bg-elevated` (#141414)
  - Border: 1px solid `border-subtle`
  - Text: `text-primary` (#e4e4e7)
  - Placeholder: `text-tertiary` (#71717a)
- **States**:
  - Default: Border subtle, background #141414
  - Focus: Border `accent-primary` (2px), add subtle `glow-primary` (blur 8px, opacity 0.3)
  - Error: Border `semantic-error`, error message below in red-400
  - Disabled: Opacity 50%, cursor not-allowed
- **Note**: All inputs support RTL text direction for Arabic. Use `dir="rtl"` attribute.

### 3.4 Navigation (Top Bar)

**Structure**: Height 64px, Background `bg-base` (#0a0a0a) with `backdrop-blur(10px)` for glass effect
- **Layout**:
  - **LTR**: Logo left, Nav links center-left, User menu + CTA right
  - **RTL**: Logo right, Nav links center-right, User menu + CTA left
- **Visual Treatment**:
  - Border-bottom: 1px solid `border-subtle`
  - Fixed position: sticky top 0, z-index 50
- **Nav Links**:
  - Default: Color `text-secondary` (#a1a1aa), padding 8-16px
  - Hover: Color `text-primary` (#e4e4e7), underline 2px `accent-primary` (fade in 150ms)
  - Active: Color `accent-primary`, underline 2px solid
- **CTA Button**: Primary button (48px height, electric blue)
- **Note**: Logo max height 32px. Support both LTR and RTL layouts via flexbox `flex-direction: row-reverse`.

### 3.5 Modal (Highest Elevation)

**Structure**: Max-width 600px, Padding 48px, Radius 16px
- **Colors**:
  - Background: `bg-modal` (#282828)
  - Overlay: rgba(0, 0, 0, 0.8) with `backdrop-blur(4px)`
- **Visual Treatment**:
  - Border: 1px solid `border-moderate`
  - Shadow: `shadow-modal` (0 8px 24px rgba(0,0,0,0.6))
- **Animation**:
  - Entrance: Opacity 0→1 (250ms) + scale 0.95→1 (250ms) ease-out
  - Exit: Reverse entrance (200ms)
- **Content Pattern**:
  - Header: `text-h2` (28px bold), margin-bottom 24px
  - Body: `text-body` (16px), color `text-secondary`
  - Actions: Right-aligned buttons (RTL: left-aligned), gap 12px
- **Note**: Dismiss on overlay click or Escape key. Trap focus within modal.

### 3.6 Agent Status Badge (Project-Specific)

**Structure**: Height 28px, Padding 8-16px, Radius 9999px (full pill)
- **Typography**: font-medium (500), 14px, letter-spacing 0.01em
- **Colors** (Status-Based):
  - **Active**: Background `accent-secondary` (#10b981), Text white
  - **Idle**: Background `bg-hover` (#1e1e1e), Border 1px `border-moderate`, Text `text-secondary`
  - **Error**: Background `semantic-error` (#ef4444), Text white
  - **Paused**: Background amber-500/20, Border 1px amber-500, Text amber-400
- **States**:
  - Default: Static display
  - Interactive (clickable): Add hover brightness 110%, cursor pointer
- **Note**: Display agent execution status on cards and detail views. Include status icon (16px SVG) to left of text (8px gap).

---

## 4. Layout & Responsive

### 4.1 Page Architecture (MPA)

Based on platform requirements, this is a **multi-page application (MPA)** with the following page patterns:

#### Page 1: Dashboard (Home)
- **Layout Pattern**: Hero (400px) + Metrics Grid (4-column) + Agent List (2-column card grid)
- **Hero Section**: Full-width `bg-pure-black` (#000), centered content (max-width 1200px), padding 80-120px vertical
  - Title: `text-hero` (48px bold), color `text-primary`
  - CTA: Primary button (56px height), electric blue with glow
- **Metrics Cards**: Apply Card Pattern (§3.2), 4-column grid (gap 24px) → 2-column (tablet) → 1-column (mobile)
  - Content: Large metric number (`text-h1` 36px bold), label (`text-body` 16px secondary)
- **Agent Grid**: Apply Card Pattern (§3.2), 2-column (gap 32px) → 1-column (mobile)

#### Page 2: Agent Detail
- **Layout Pattern**: Breadcrumb + Header (200px) + 2-Column Layout (7/5 split)
- **Header**: `bg-elevated` (#141414), padding 48px
  - Title: `text-h1` (36px), Status badge, action buttons (Edit, Delete)
- **Main Content (7-col)**: Agent configuration, logs, metrics (apply Card Pattern)
- **Sidebar (5-col)**: Metadata, quick actions, related agents
- **Responsive**: Stack to single column on tablet (<768px)

#### Page 3: Agent Creation/Edit Form
- **Layout Pattern**: Centered Form (max-width 800px) + Sticky Action Bar
- **Form Container**: Apply Card Pattern (§3.2), padding 48px
- **Input Fields**: Apply Input Pattern (§3.3), full-width, gap 24px
- **Action Bar**: Sticky bottom (mobile), fixed bottom-right (desktop)
  - Buttons: Primary (Create/Save) + Secondary (Cancel)

#### Page 4: Settings
- **Layout Pattern**: Sidebar Navigation (240px) + Content Area (flex-1)
- **Sidebar**: `bg-pure-black` (#000), fixed left (LTR) / right (RTL)
  - Active item: Background #1e1e1e, border-left 3px `accent-primary` (LTR) / border-right (RTL)
- **Content**: Tabbed sections with Card Pattern
- **Responsive**: Collapse sidebar to top tabs on mobile

### 4.2 Grid System

**Container Max-Width**: 1400px (centered, padding 24-48px horizontal)
**Column Gaps**: 24-32px (desktop), 16-24px (mobile)
**Grid Columns**:
- 12-column flexible grid
- Desktop: 4-col, 3-col, 2-col layouts
- Tablet (768px): 2-col → 1-col
- Mobile (640px): Always 1-col

### 4.3 Responsive Breakpoints

| Breakpoint | Width | Adjustments |
|------------|-------|-------------|
| `sm` | 640px | Stack grids to 1-column, increase touch targets to 48×48px |
| `md` | 768px | Collapse sidebar to tabs, 2-column grids |
| `lg` | 1024px | Standard desktop layout, full navigation |
| `xl` | 1280px | Max content width 1400px, generous spacing |

### 4.4 RTL Support (Arabic)

**Layout Mirroring**:
- Navigation: Logo position flipped (left→right)
- Sidebar: Fixed right instead of left
- Text alignment: `text-align: right` for body text
- Icons: Directional icons (arrows) mirrored horizontally

**Implementation**:
```css
[dir="rtl"] .nav { flex-direction: row-reverse; }
[dir="rtl"] .sidebar { right: 0; left: auto; }
[dir="rtl"] .card { text-align: right; }
```

**Typography**: Inter font supports Arabic glyphs. Use font-weight 500+ for Arabic text clarity.

### 4.5 Responsive Touch Targets

- **Mobile**: All interactive elements ≥48×48px (WCAG 2.1 AAA)
- **Desktop**: Minimum 44×44px (mouse precision)
- **Glow Effects**: Reduce to single-layer on mobile (50% intensity)

---

## 5. Interaction & Animation

### 5.1 Animation Standards

**Timing by Element**:
- Buttons: 150ms (fast hover response)
- Cards: 250ms (elevation changes)
- Modals: 400ms (entrance/exit)
- Page transitions: 300ms (fade or slide)

**Easing**: Use `ease-out` (90% of cases), `cubic-bezier(0.4, 0.0, 0.2, 1)` for sharp UI changes

**Transform-Only Rule**: Animate ONLY `transform` and `opacity` (GPU-accelerated). Never animate width/height/margin.

### 5.2 Interactive States

**Buttons**:
- Hover: Brightness 110% + glow (20px blur, 0.5 opacity)
- Active: Scale 0.98 + brightness 95%
- Focus: 2px outline, 2px offset, `accent-primary` color

**Cards**:
- Hover: Background elevation +1 level (#141414 → #1e1e1e), border opacity +50%
- Active: Scale 0.99 (subtle press feedback)

**Links**:
- Hover: Color `text-primary` + 2px underline (fade in 150ms)
- Active: Color `accent-primary`

**Icons**:
- Hover: Color `accent-primary` + `glow-icon` (8px drop-shadow)
- Active: Scale 0.95

### 5.3 Glow Effects (Dark Mode Signature)

**Primary Glow (Electric Blue)**:
```
box-shadow: 0 0 20px rgba(59, 130, 246, 0.5),
            0 0 40px rgba(59, 130, 246, 0.3);
```
- Apply on: Primary button hover, focused inputs, active nav items

**Secondary Glow (Emerald Green)**:
```
box-shadow: 0 0 20px rgba(16, 185, 129, 0.5),
            0 0 40px rgba(16, 185, 129, 0.3);
```
- Apply on: Success notifications, secondary button hover, agent status badges (active)

**Icon Glow**:
```
filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.6));
```
- Apply on: Interactive icon hover states

**Performance**: Glows use `box-shadow` (GPU-accelerated). Limit to ≤3 glowing elements per viewport.

### 5.4 Reduced Motion Support

**Respect User Preference**:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Fallback**: Replace animations with instant state changes (opacity 0→1 remains, remove scale/translate).

### 5.5 Micro-Interactions

**Status Pulse (Agent Active)**:
- Badge: Pulse animation 2s infinite on active agents
- Glow: `0 0 12px accent-secondary`, opacity 0.5→1→0.5

**Button Loading State**:
- Replace text with spinner (20px, `accent-primary` color)
- Disable pointer events, opacity 70%

**Toast Notifications**:
- Slide in from top-right (LTR) / top-left (RTL)
- Duration: 250ms entrance, auto-dismiss 5s, 200ms exit
- Apply Card Pattern with appropriate semantic color border

---

**End of Specification**

This design system prioritizes **developer efficiency, visual clarity, and accessibility** in low-light environments. All components support RTL layouts for Arabic localization. Implement using CSS variables mapped to design tokens for easy theming and maintenance.
