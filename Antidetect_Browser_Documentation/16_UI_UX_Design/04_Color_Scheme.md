# Color Scheme

## 1. Color Palette Overview

### 1.1 Primary Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Primary 50 | #EFF6FF | 239, 246, 255 | Backgrounds, highlights |
| Primary 100 | #DBEAFE | 219, 234, 254 | Subtle backgrounds |
| Primary 200 | #BFDBFE | 191, 219, 254 | Secondary backgrounds |
| Primary 300 | #93C5FD | 147, 197, 253 | Disabled states, borders |
| Primary 400 | #60A5FA | 96, 165, 250 | Active states, links |
| Primary 500 | #3B82F6 | 59, 130, 246 | Primary actions, brand |
| Primary 600 | #2563EB | 37, 99, 235 | Primary buttons (default) |
| Primary 700 | #1D4ED8 | 29, 78, 216 | Primary button hover |
| Primary 800 | #1E40AF | 30, 64, 175 | Active/pressed states |
| Primary 900 | #1E3A8A | 30, 58, 138 | Strong emphasis |

### 1.2 Neutral Colors (Grays)

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Gray 50 | #F9FAFB | 249, 250, 251 | Page backgrounds |
| Gray 100 | #F3F4F6 | 243, 244, 246 | Card backgrounds |
| Gray 200 | #E5E7EB | 229, 231, 235 | Borders, dividers |
| Gray 300 | #D1D5DB | 209, 213, 217 | Disabled borders |
| Gray 400 | #9CA3AF | 156, 163, 175 | Placeholder text |
| Gray 500 | #6B7280 | 107, 114, 128 | Secondary text |
| Gray 600 | #4B5563 | 75, 85, 99 | Body text |
| Gray 700 | #374151 | 55, 65, 81 | Headings |
| Gray 800 | #1F2937 | 31, 41, 55 | Primary headings |
| Gray 900 | #111827 | 17, 24, 39 | Dark backgrounds |

### 1.3 Semantic Colors

#### Success (Green)

| Name | Hex | Usage |
|------|-----|-------|
| Success 50 | #F0FDF4 | Backgrounds |
| Success 100 | #DCFCE7 | Light backgrounds |
| Success 500 | #22C55E | Icons, links |
| Success 600 | #16A34A | Buttons |
| Success 700 | #15803D | Hover states |
| Success 900 | #14532D | Text emphasis |

#### Error (Red)

| Name | Hex | Usage |
|------|-----|-------|
| Error 50 | #FEF2F2 | Backgrounds |
| Error 100 | #FEE2E2 | Light backgrounds |
| Error 500 | #EF4444 | Icons, links |
| Error 600 | #DC2626 | Buttons |
| Error 700 | #B91C1C | Hover states |
| Error 900 | #7F1D1D | Text emphasis |

#### Warning (Yellow)

| Name | Hex | Usage |
|------|-----|-------|
| Warning 50 | #FEFCE8 | Backgrounds |
| Warning 100 | #FEF9C3 | Light backgrounds |
| Warning 500 | #EAB308 | Icons, links |
| Warning 600 | #CA8A04 | Buttons |
| Warning 700 | #A16207 | Hover states |
| Warning 900 | #713F12 | Text emphasis |

#### Info (Blue)

| Name | Hex | Usage |
|------|-----|-------|
| Info 50 | #F0F9FF | Backgrounds |
| Info 100 | #E0F2FE | Light backgrounds |
| Info 500 | #0EA5E9 | Icons, links |
| Info 600 | #0284C7 | Buttons |
| Info 700 | #0369A1 | Hover states |
| Info 900 | #0C4A6E | Text emphasis |

## 2. Dark Mode Colors

### 2.1 Dark Mode Palette

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Dark 50 | #0F172A | 15, 23, 42 | Main background |
| Dark 100 | #1E293B | 30, 41, 59 | Card backgrounds |
| Dark 200 | #334155 | 51, 65, 85 | Elevated surfaces |
| Dark 300 | #475569 | 71, 85, 105 | Borders |
| Dark 400 | #64748B | 100, 116, 139 | Muted text |
| Dark 500 | #94A3B8 | 148, 163, 184 | Secondary text |
| Dark 600 | #CBD5E1 | 203, 213, 225 | Primary text |

## 3. Application-Specific Colors

### 3.1 Security & Privacy Indicators

| Color | Hex | Meaning |
|-------|-----|---------|
| Secure | #10B981 | Connection secured, fingerprint protected |
| Caution | #F59E0B | Partial protection, some exposures detected |
| Warning | #EF4444 | Unprotected, fingerprint detected |
| Verified | #3B82F6 | Identity verified, premium feature |

### 3.2 Session Status

| Status | Background | Text | Border |
|--------|------------|------|--------|
| Active | Success 100 | Success 700 | Success 500 |
| Paused | Warning 100 | Warning 700 | Warning 500 |
| Stopped | Gray 100 | Gray 700 | Gray 300 |
| Error | Error 100 | Error 700 | Error 500 |

### 3.3 Browser Fingerprint Colors

| Fingerprint Type | Color | Hex |
|------------------|-------|-----|
| Canvas | Purple | #8B5CF6 |
| Audio | Pink | #EC4899 |
| WebGL | Cyan | #06B6D4 |
| Fonts | Orange | #F97316 |
| Hardware | Teal | #14B8A6 |

## 4. Color Usage Guidelines

### 4.1 Accessibility Requirements

- **Text Contrast**: Minimum 4.5:1 for body text, 3:1 for large text
- **Interactive Elements**: Minimum 3:1 for UI components
- **Status Colors**: Never use color alone; always combine with icon or text

### 4.2 Color Application Rules

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Page Background | Gray 50 | Dark 50 |
| Card Background | White | Dark 100 |
| Primary Text | Gray 900 | Dark 600 |
| Secondary Text | Gray 500 | Dark 400 |
| Primary Action | Primary 600 | Primary 500 |
| Borders | Gray 200 | Dark 300 |

## 5. CSS Variables

```css
:root {
  /* Primary */
  --color-primary-50: #EFF6FF;
  --color-primary-100: #DBEAFE;
  --color-primary-200: #BFDBFE;
  --color-primary-300: #93C5FD;
  --color-primary-400: #60A5FA;
  --color-primary-500: #3B82F6;
  --color-primary-600: #2563EB;
  --color-primary-700: #1D4ED8;
  --color-primary-800: #1E40AF;
  --color-primary-900: #1E3A8A;

  /* Neutral */
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;

  /* Semantic */
  --color-success: #22C55E;
  --color-error: #EF4444;
  --color-warning: #EAB308;
  --color-info: #0EA5E9;

  /* Dark Mode */
  --color-dark-50: #0F172A;
  --color-dark-100: #1E293B;
  --color-dark-200: #334155;
}
```
