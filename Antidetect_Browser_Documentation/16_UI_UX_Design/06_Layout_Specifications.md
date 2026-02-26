# Layout Specifications

## 1. Grid System

### 1.1 Base Grid

```
Grid Type: 12-column
Gutter Width: 24px
Column Width: Flexible (percentage-based)
Max Container: 1440px
Margin: 24px (desktop), 16px (tablet), 12px (mobile)
```

### 1.2 Grid Breakpoints

| Breakpoint | Width | Columns | Gutter | Margin |
|------------|-------|---------|--------|--------|
| xs | < 640px | 4 | 16px | 12px |
| sm | 640-767px | 4 | 16px | 16px |
| md | 768-1023px | 8 | 20px | 20px |
| lg | 1024-1279px | 12 | 24px | 24px |
| xl | 1280-1535px | 12 | 24px | 32px |
| 2xl | ≥ 1536px | 12 | 24px | 48px |

## 2. Spacing Scale

### 2.1 Spacing Tokens

| Token | Value | Usage |
|-------|-------|-------|
| space-0 | 0 | No spacing |
| space-1 | 4px | Tight spacing, icon gaps |
| space-2 | 8px | Inline elements, small gaps |
| space-3 | 12px | Related elements |
| space-4 | 16px | Standard component spacing |
| space-5 | 20px | Between related groups |
| space-6 | 24px | Section padding, card padding |
| space-8 | 32px | Section spacing |
| space-10 | 40px | Large section gaps |
| space-12 | 48px | Page-level spacing |
| space-16 | 64px | Major section dividers |
| space-20 | 80px | Hero spacing |
| space-24 | 96px | Full-width section padding |

### 2.2 Component Spacing

```
Card Padding: 24px
Button Padding: 12px 16px (small), 12px 20px (medium), 16px 24px (large)
Input Padding: 12px horizontal
List Item Padding: 12px 16px
Table Cell Padding: 12px 16px
Modal Padding: 24px
Drawer Padding: 24px
```

## 3. Layout Containers

### 3.1 Main Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Header (56px fixed height)                                     │
├────────────┬────────────────────────────────────────────────────┤
│            │                                                     │
│  Sidebar   │  Main Content Area                                 │
│  240px     │                                                     │
│  (collaps- │  ┌─────────────────────────────────────────────┐   │
│   ible)    │  │ Page Header                                 │   │
│            │  ├─────────────────────────────────────────────┤   │
│            │  │                                             │   │
│            │  │ Content                                     │   │
│            │  │                                             │   │
│            │  │                                             │   │
│            │  └─────────────────────────────────────────────┘   │
│            │                                                     │
├────────────┴────────────────────────────────────────────────────┤
│  Status Bar (28px fixed height) - optional                     │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Content Max Widths

| Context | Max Width | Justification |
|---------|------------|----------------|
| Page Content | 1200px | Optimal reading width |
| Form Content | 640px | Focus and readability |
| Table Content | 100% | Full width with scroll |
| Modal Content | 480px (sm), 640px (md), 800px (lg) | Task-focused |
| Drawer Content | 400px (sm), 600px (md) | Side panel |

## 4. Responsive Breakpoints

### 4.1 Application Breakpoints

```
Desktop (Primary):
Min: 1280px
Optimal: 1920px
Sidebar: Expanded (240px)
Content: Full grid

Tablet:
Min: 768px
Max: 1279px
Sidebar: Collapsed to icons (64px) or hidden
Content: Reduced grid (8 columns)

Mobile (Limited Support):
Min: 320px
Max: 767px
Layout: Stacked single column
Navigation: Hamburger menu
```

### 4.2 Component Responsiveness

```
Cards:
Desktop: 3-4 columns
Tablet: 2 columns
Mobile: 1 column

Tables:
Desktop: Full display
Tablet: Horizontal scroll
Mobile: Card view alternative

Forms:
Desktop: Single column, label above
Mobile: Single column, full width
```

## 5. Layout Patterns

### 5.1 Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Header: Logo + Search + User Actions                            │
├──────────┬──────────────────────────────────────────────────────┤
│ Sidebar  │ ┌────────────────────────────────────────────────┐   │
│          │ │ Stats Row (4 cards)                            │   │
│ Nav      │ ├────────────────────────────────────────────────┤   │
│ Items    │ │                                                │   │
│          │ │ Main Content (Grid/List/Tables)              │   │
│          │ │                                                │   │
│          │ │                                                │   │
│          │ └────────────────────────────────────────────────┘   │
├──────────┴──────────────────────────────────────────────────────┤
│ Status Bar: System info                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Form Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Form Title + Description                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────────┐  ┌─────────────────┐                        │
│ │ Input Group    │  │ Input Group    │  (2 columns)          │
│ └─────────────────┘  └─────────────────┘                        │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────┐     │
│ │ Full Width Input Group                                   │     │
│ └─────────────────────────────────────────────────────────┘     │
│                                                                  │
│ ┌─────────────────┐  ┌─────────────────┐                        │
│ │ Input Group    │  │ Input Group    │  (2 columns)          │
│ └─────────────────┘  └─────────────────┘                        │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────┐     │
│ │ Section Title                                             │     │
│ │ ┌─────────────────┐  ┌─────────────────┐              │     │
│ │ │ Input Group    │  │ Input Group    │              │     │
│ │ └─────────────────┘  └─────────────────┘              │     │
│ └─────────────────────────────────────────────────────────┘     │
│                                                                  │
│ [Cancel]                                      [Save Changes]     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Detail View Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back                    [Actions]                             │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                      │
│ Tabs     │ Tab Content                                          │
│          │                                                      │
│          │ ┌──────────────────────┐                            │
│          │ │ Primary Information  │                            │
│          │ └──────────────────────┘                            │
│          │                                                      │
│          │ ┌──────────────────────┐                            │
│          │ │ Secondary Information│                            │
│          │ └──────────────────────┘                            │
│          │                                                      │
└──────────┴──────────────────────────────────────────────────────┘
```

## 6. Elevation & Shadows

### 6.1 Shadow Scale

| Level | Shadow | Usage |
|-------|--------|-------|
| None | none | Flat elements |
| sm | 0 1px 2px rgba(0,0,0,0.05) | Subtle elevation |
| base | 0 1px 3px rgba(0,0,0,0.1) | Cards, dropdowns |
| md | 0 4px 6px rgba(0,0,0,0.1) | Elevated cards |
| lg | 0 10px 15px rgba(0,0,0,0.1) | Modals, popovers |
| xl | 0 20px 25px rgba(0,0,0,0.15) | Large modals |

### 6.2 Z-Index Scale

| Level | Value | Usage |
|-------|-------|-------|
| base | 0 | Default stacking |
| dropdown | 100 | Dropdown menus |
| sticky | 200 | Sticky headers |
| modal-backdrop | 300 | Modal overlay |
| modal | 400 | Modal dialogs |
| tooltip | 500 | Tooltips, popovers |
| toast | 600 | Toast notifications |

## 7. Layout Utilities

```css
/* Container */
.container { max-width: 1440px; margin: 0 auto; padding: 0 24px; }
.container-sm { max-width: 1200px; }
.container-form { max-width: 640px; }

/* Grid */
.grid { display: grid; gap: 24px; }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Flex */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: 8px; }
.gap-4 { gap: 16px; }
.gap-6 { gap: 24px; }

/* Spacing */
.p-4 { padding: 16px; }
.p-6 { padding: 24px; }
.m-0 { margin: 0; }
.mb-4 { margin-bottom: 16px; }
.mb-6 { margin-bottom: 24px; }
```
