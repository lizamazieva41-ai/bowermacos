# Typography

## 1. Font Families

### 1.1 Primary Font

**Inter** - Primary interface font

```
Use: All UI text, buttons, labels, navigation
Weights: 400 (Regular), 500 (Medium), 600 (Semi-Bold), 700 (Bold)
License: Open Source (SIL Open Font License)
Source: Google Fonts
```

### 1.2 Monospace Font

**JetBrains Mono** - Code, technical data, logs

```
Use: Code blocks, terminal output, technical values
Weights: 400 (Regular), 500 (Medium)
License: Open Source
Source: JetBrains
```

### 1.3 System Font Stack

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

## 2. Type Scale

### 2.1 Display

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| Display Large | 48px | 700 | 1.1 | -0.02em | Hero headlines |
| Display Medium | 36px | 600 | 1.2 | -0.01em | Section titles |
| Display Small | 30px | 600 | 1.25 | 0 | Page titles |

### 2.2 Headings

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| H1 | 28px | 700 | 1.3 | -0.01em | Main page titles |
| H2 | 24px | 600 | 1.35 | 0 | Section headings |
| H3 | 20px | 600 | 1.4 | 0 | Subsection headings |
| H4 | 18px | 600 | 1.4 | 0 | Card titles |

### 2.3 Body

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| Body Large | 16px | 400 | 1.6 | 0 | Primary content |
| Body Medium | 14px | 400 | 1.5 | 0 | Secondary content |
| Body Small | 13px | 400 | 1.5 | 0.01em | Tertiary content |

### 2.4 Labels & UI

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| Label Large | 14px | 500 | 1.4 | 0.01em | Form labels |
| Label Medium | 12px | 500 | 1.4 | 0.02em | Button text |
| Label Small | 11px | 500 | 1.4 | 0.05em | Badges, tags |

### 2.5 Code

| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| Code | 13px | 400 | 1.6 | Inline code |
| Code Block | 13px | 400 | 1.7 | Code snippets |

## 3. Text Styles

### 3.1 Heading Styles

```markdown
H1 - Page Title
Size: 28px / 1.3 / -0.01em
Weight: 700
Margin Bottom: 24px

H2 - Section Heading
Size: 24px / 1.35 / 0
Weight: 600
Margin Bottom: 20px

H3 - Subsection Heading
Size: 20px / 1.4 / 0
Weight: 600
Margin Bottom: 16px

H4 - Card Heading
Size: 18px / 1.4 / 0
Weight: 600
Margin Bottom: 12px
```

### 3.2 Body Text Styles

```markdown
Body Large - Primary Content
Size: 16px / 1.6 / 0
Weight: 400
Color: Gray 700

Body Medium - Secondary Content
Size: 14px / 1.5 / 0
Weight: 400
Color: Gray 600

Body Small - Tertiary Content
Size: 13px / 1.5 / 0.01em
Weight: 400
Color: Gray 500
```

### 3.3 Interactive Text

```markdown
Link
Size: inherit / 1.5 / 0
Weight: 500
Color: Primary 600
Decoration: underline (hover only)

Button Text
Size: 14px / 1.4 / 0.01em
Weight: 500
Transform: none

Input Text
Size: 14px / 1.5 / 0
Weight: 400
Color: Gray 900
```

## 4. Spacing System for Text

### 4.1 Line Length

| Context | Max Characters | Recommended Width |
|---------|----------------|-------------------|
| Prose Content | 65-75 | 640px |
| UI Components | N/A | Full width |
| Tables | N/A | Scrollable |
| Code Blocks | N/A | Full width |

### 4.2 Vertical Rhythm

```
Paragraph Spacing: 16px (1em)
Heading to Paragraph: 24px
Section to Section: 32px
List Item Spacing: 8px
```

## 5. Font Implementation

### 5.1 CSS Variables

```css
:root {
  /* Font Families */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Font Sizes */
  --text-xs: 11px;
  --text-sm: 13px;
  --text-base: 14px;
  --text-lg: 16px;
  --text-xl: 18px;
  --text-2xl: 20px;
  --text-3xl: 24px;
  --text-4xl: 28px;
  --text-5xl: 36px;
  --text-6xl: 48px;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.6;

  /* Letter Spacing */
  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.02em;
  --tracking-wider: 0.05em;
}
```

### 5.2 Utility Classes

```css
/* Headings */
.text-h1 { font-size: 28px; font-weight: 700; line-height: 1.3; }
.text-h2 { font-size: 24px; font-weight: 600; line-height: 1.35; }
.text-h3 { font-size: 20px; font-weight: 600; line-height: 1.4; }
.text-h4 { font-size: 18px; font-weight: 600; line-height: 1.4; }

/* Body */
.text-body-lg { font-size: 16px; line-height: 1.6; }
.text-body { font-size: 14px; line-height: 1.5; }
.text-body-sm { font-size: 13px; line-height: 1.5; }

/* Labels */
.text-label { font-size: 14px; font-weight: 500; line-height: 1.4; }
.text-label-sm { font-size: 12px; font-weight: 500; line-height: 1.4; }
.text-label-xs { font-size: 11px; font-weight: 500; line-height: 1.4; }

/* Code */
.font-mono { font-family: var(--font-mono); }
.text-code { font-size: 13px; line-height: 1.6; font-family: var(--font-mono); }
```

## 6. Accessibility Guidelines

### 6.1 Text Legibility

- Minimum font size: 13px for body text
- Line height: 1.5 minimum for body text
- Letter spacing: Avoid negative values for body text
- Font weight: Use 500+ for important interactive elements

### 6.2 Contrast Requirements

- Body text: 4.5:1 minimum (Gray 600 on white)
- Large text (18px+): 3:1 minimum
- UI components: 3:1 minimum
- Text on colored backgrounds: Adjust accordingly
