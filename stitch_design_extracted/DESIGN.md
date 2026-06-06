---
name: Obsidian Mint
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#68dba9'
  on-secondary: '#003825'
  secondary-container: '#25a475'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#e29100'
  on-tertiary-container: '#523200'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#85f8c4'
  secondary-fixed-dim: '#68dba9'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  headline-xl:
    fontFamily: Outfit
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  container-max-width: 1200px
  gutter: 24px
  margin-mobile: 16px
---

## Brand & Style
The design system is engineered for a premium fintech experience, specifically targeting investors seeking clarity and security within the mutual fund landscape. The brand personality is authoritative yet accessible, evoking a sense of calm intelligence and high-tier institutional quality.

The visual style utilizes **Modern Glassmorphism** set against a deep, dark-mode foundation. It leverages translucency and microscopic detail—such as fine-line borders and soft backing glows—to create a sense of depth and physical presence without the weight of traditional skeuomorphism. The emotional response should be one of "sophisticated safety," where the UI feels like a high-end financial terminal that is intuitive and human-centric.

## Colors
This design system operates on a high-contrast dark foundation. The primary background is a deep **Midnight Slate**, providing a stable, low-strain canvas for information-dense FAQ interactions.

- **Primary & Secondary (Mint & Teal):** Used exclusively for success states, growth indicators, and primary action triggers. They represent the "Go" signals of financial health.
- **Tertiary (Amber):** Reserved for legal disclaimers, risk warnings, and important mutual fund disclosures.
- **Surfaces:** Containers use a semi-transparent Charcoal Slate (#161D2F at 70% opacity) to allow background glows to permeate the UI.
- **Borders:** Every surface must be defined by a 1px border (`rgba(255, 255, 255, 0.08)`) to maintain structural integrity in a dark environment.

## Typography
The typography strategy pairs **Outfit** for headlines with **Inter** for functional text. 

- **Outfit** provides a geometric, modern flair that feels premium and tech-forward. Use it for headers and large numeric fund data.
- **Inter** ensures maximum legibility for complex financial explanations and FAQ responses. 
- **Hierarchy:** Use White (#FFFFFF) for all headlines to ensure they pop against the dark background. Use Muted Cool Grey (#9CA3AF) for body text to reduce visual noise during long-form reading. Labels and small metadata should use medium or semi-bold weights to remain legible at small scales.

## Layout & Spacing
The layout follows a **Fluid Grid** model with strict adherence to a 4px baseline shift. 

- **Desktop:** 12-column grid with a 1200px max-width to prevent line lengths from becoming unreadable in text-heavy FAQ sections.
- **Mobile:** 4-column grid with 16px side margins. 
- **Rhythm:** Use `lg` (24px) spacing for the vertical rhythm between FAQ cards and `md` (16px) for internal padding within containers. Large sections are separated by `xl` (40px) to give the UI "room to breathe," reinforcing the premium aesthetic.

## Elevation & Depth
Depth is not achieved through heavy drop shadows, but through **Tonal Layering** and **Backdrop Blurs**.

1.  **Level 0 (Base):** Midnight Slate (#0B0F19).
2.  **Level 1 (Cards/Containers):** Charcoal Slate (#161D2F) with 70% opacity and a 12px `backdrop-filter: blur()`.
3.  **Level 2 (Modals/Popovers):** Higher opacity (85%) and a subtle outer glow using the primary Mint color at 5% opacity to simulate a "light source" behind the element.

**Highlights:** A top-down light source is simulated using a linear gradient on the 1px borders, where the top and left edges are slightly brighter than the bottom and right.

## Shapes
The shape language is consistently **Rounded**, using a 16px (1rem) base for all primary containers and cards.

- **Buttons & Inputs:** Follow the 16px radius to match the containers, creating a unified, organic look.
- **Small Elements:** Tooltips and tags use a smaller 8px (0.5rem) radius.
- **Interactive States:** On hover, cards should not grow in size but may feature a slight increase in border opacity (from 0.08 to 0.2) to signal interactivity.

## Components
- **FAQ Cards:** Use the Glassmorphic style. The question is in White (Outfit, Bold) and the answer in Muted Grey (Inter, Regular). Include a minimalist "chevron" icon that rotates 180 degrees on expansion.
- **Buttons:**
    - *Primary:* Solid Forest Mint Green with White text. No shadow; use a subtle inner glow.
    - *Secondary:* Ghost style with the 1px white-alpha border and a 5% white hover fill.
- **Input Fields:** Darker than the container (#0B0F19 at 50% opacity) with a 16px radius. The active state features a Forest Mint Green border.
- **Compliance Chips:** Small, pill-shaped tags (32px height) with Soft Amber backgrounds (10% opacity) and Amber text for "Risk Disclosures."
- **Mutual Fund Stats:** Use "Outfit" for large numeric displays. Upward trends use Mint Green; downward trends use a muted Coral (if necessary), though the focus here is on safety and growth.
- **Icons:** Use thin-stroke (1.5px) minimalist icons. Avoid filled icons unless used as a status indicator.