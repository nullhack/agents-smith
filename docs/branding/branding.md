# Branding — agents-smith

> *Connect AI agent configurations to any project.*

Agents read this file before generating release names, C4 diagrams, README banners, or any document with visual or copy identity. All fields are optional; absent or blank fields fall back to defaults (adjective-animal release names, Mermaid default colours, no wording constraints).

**Ownership**: The stakeholder owns this file. The design agent proposes changes (colour palettes, visual assets, wording updates); the stakeholder approves them. No other agent edits this file.

---

## Identity

- **Project name:** agents-smith
- **Tagline:** Connect AI agent configurations to any project
- **Mission:** Eliminate the repetitive, error-prone process of manually copying AI agent configuration files into projects by providing a single command to fetch, install, and track them — then cleanly purge when done.
- **Vision:** Every developer can add or remove agentic tooling from any project with one command, confident that nothing is left behind or accidentally overwritten. Like Agent Smith in the Matrix, smith enters a project, copies its patterns, and returns something more capable than what it found.
- **Tone of voice:** direct, precise, minimal

## Visual

The palette is drawn from the Matrix — dark void backgrounds, bright green phosphor for accents. Every colour choice serves legibility first; decoration is secondary.

- **Background/void:** `#0F1117` — Deep dark near-black for terminals and dark mode backgrounds
- **Primary/phosphor:** `#00FF41` — Matrix green for highlights, interactive elements, and the S lettermark; WCAG AAA on dark backgrounds at large text, decorative at small sizes
- **Primary text:** `#E0E0E0` — High-contrast light grey for readability on dark backgrounds
- **Secondary/text:** `#C0C0C0` — Muted silver for secondary text and taglines
- **Accent/white:** `#FFFFFF` — Pure white for the wordmark "mith" and high-emphasis text
- **Logo:** `docs/assets/logo.svg`
- **Banner:** `docs/assets/banner.svg`

> `#00FF41` on `#0F1117` achieves high contrast for large text and interactive elements. `#E0E0E0` on `#0F1117` achieves 12.6:1 contrast (WCAG AAA). `#00FF41` is decorative at small text sizes; it never carries meaning that must be read at body size.

### Logo

A stylised S lettermark carved from five horizontal scan-line bars. Negative space between the bars reads as the curves of an S. Rendered in `#00FF41` with varying opacity (0.65 at caps, 0.85 at arms, 1.0 at the waist). Dark mode: same mark on transparent background.

### Banner

Dark void background (`#0F1117`) with the S logo mark scaled to height, followed by "mith" in `#FFFFFF` bold sans-serif (system-ui), tagline "Pair program with AI, the right way." in `#C0C0C0` regular weight with letter-spacing.

## Release Naming

- **Convention:** `matrix-character` (adjective-matrix-character)
- **Theme:** The Matrix — each release is named after a character, concept, or quote from the Matrix franchise
- **Excluded words:** easy, simple, just, quick, scaffold, boilerplate

## Wording

Every word carries weight.

- **Avoid:** easy, simple, just, quick, scaffold, superseded, boilerplate, magic, seamlessly
- **Prefer:** minimal, precise, production-ready, rigorous, clone, purge, track, enter, copy