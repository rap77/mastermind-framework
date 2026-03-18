# UI Design Brain Context — War Room Frontend v2.1
**Brain:** brain-03-ui-design
**Brief:** War Room Frontend — 4 screens

## VISUAL LANGUAGE

A high-density, technical "Command Center" aesthetic designed for expert users. The mood is authoritative and precise, utilizing a dark-first theme to reduce eye strain during long periods of execution monitoring [1, 2]. The tone is functional, where hierarchy is established through space and weight rather than excessive decoration, following a "Swiss-style" digital grid for maximum order [3-5].

## COLOR PALETTE

{'primary': '`#D0BCFF` (A desaturated violet role for dark mode that provides brand identity without "vibrating" against dark backgrounds) [6, 7].', 'secondary': '`#2C2C2C` (A surface-variant used for container backgrounds to indicate tonal elevation instead of traditional shadows) [7, 8].', 'accent': '`#F2B8B5` (A semantic role for critical errors and high-urgency AI status alerts that remains distinct from the primary brand color) [7, 9].', 'background': '`#121212` (The foundation for the dark theme, chosen to prevent OLED smearing and provide a comfortable contrast ratio for long-term reading) [2, 7].', 'text': '`#E6E1E5` (A high-contrast neutral for primary content, ensuring WCAG AA compliance with a 15.8:1 ratio against the background) [7, 10].'}

## TYPOGRAPHY

{'heading': '`Inter, Semi-Bold` (A clean, functional sans-serif that communicates technical reliability and sophisticated architecture) [11, 12].', 'body': '`Inter, Regular` (Selected for its high legibility in dense dashboards, maintaining a minimum size of 14px-16px for readability) [11, 13, 14].', 'mono': '`JetBrains Mono` (Specifically used in the Engine Room and logs for its distinct character separation, crucial for AI engineers) [15, 16].'}

## SPACING SYSTEM

An 8px base scale (4, 8, 12, 16, 24, 32, 48, 64) to ensure mathematical harmony across the Bento Grid and DAG visualization [5, 17].

## COMPONENT HIERARCHY

- **name:** **Bento Card (Organism)**
- **description:** A modular container for the **Command Center** that uses a 12-column grid system and fixed 8px gutters to organize metrics and quick actions [18-20].
- **name:** **DAG Flow Node (Molecule)**
- **description:** A structured unit within **The Nexus** combining an icon, a status label, and interactive handles, with colored indicators for real-time feedback [21-23].
- **name:** **Command Palette (Organism)**
- **description:** A keyboard-first `cmdk` interface with a **focus-trap** and high-contrast search results for rapid navigation and orchestration [24-26].
- **name:** **Log Viewer (Organism)**
- **description:** A high-density monitoring component in the **Engine Room** that uses monospaced text and semantic color-coding (red/yellow/green) to communicate system status [7, 10, 27].

## DESIGN PRINCIPLES

- **Hierarchy is Function**: Every design decision—size, weight, or color—must be used to communicate the **importance of AI orchestration data** in under three seconds [3, 17, 28].
- **The System Before the Screen**: Design using **Atomic Design levels** (atoms to organisms) to ensure that the Strategy Vault and Engine Room share a single source of truth [29-31].
- **Insight Over Decoration**: Every visual element, particularly the DAG visualization and log animations, must **answer a specific functional question** for the developer, following the "Form Follows Function" doctrine [27, 32, 33].

## GENERATED AT

2026-03-18 16:25:37.933599
