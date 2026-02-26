# Component Library

## 1. Buttons

### 1.1 Primary Button

```
States: Default | Hover | Active | Disabled | Loading

Default:  bg-primary-600, text-white, rounded-md, px-4 py-2
Hover:    bg-primary-700, cursor-pointer
Active:   bg-primary-800, scale-98
Disabled: bg-primary-300, opacity-50, cursor-not-allowed
Loading:  bg-primary-600, spinner-icon, text-transparent
```

**Specifications:**
- Height: 36px (small), 40px (medium), 48px (large)
- Border Radius: 6px
- Font Weight: 500
- Transition: 150ms ease

### 1.2 Secondary Button

```
Default:  bg-transparent, border-primary-600, text-primary-600
Hover:    bg-primary-50
Active:   bg-primary-100
Disabled: border-primary-300, text-primary-300
```

### 1.3 Destructive Button

```
Default:  bg-red-600, text-white
Hover:    bg-red-700
Active:   bg-red-800
```

### 1.4 Icon Button

```
Size: 32x32px (small), 40x40px (medium), 48x48px (large)
Border Radius: 50%
States: Same as Primary Button
Use Cases: Toolbar actions, header actions, inline actions
```

## 2. Form Inputs

### 2.1 Text Input

```
┌──────────────────────────────────────┐
│ Label                               │
│ ┌────────────────────────────────┐  │
│ │ Input placeholder              │  │
│ └────────────────────────────────┘  │
│ Helper text (optional)              │
└──────────────────────────────────────┘

Height: 40px
Padding: 12px horizontal
Border: 1px solid gray-300
Border Radius: 6px
Focus: border-primary-500, ring-2 ring-primary-100
Error: border-red-500, ring-2 ring-red-100
Disabled: bg-gray-100, cursor-not-allowed
```

### 2.2 Select Dropdown

```
┌──────────────────────────────────────┐
│ Label                               │
│ ┌────────────────────────────────┐  │
│ │ Selected Option            ▼  │  │
│ └────────────────────────────────┘  │
└──────────────────────────────────────┘

Dropdown Max Height: 240px (scrollable)
Option Height: 36px
Hover: bg-gray-50
Selected: bg-primary-50, text-primary-700
```

### 2.3 Toggle Switch

```
Off:  bg-gray-200, thumb-gray-50
On:   bg-primary-600, thumb-white
Size: 44x24px (default), 36x20px (small)
Transition: 200ms cubic-bezier(0.4, 0, 0.2, 1)
```

### 2.4 Checkbox

```
Size: 18x18px
Border: 2px solid gray-400
Border Radius: 4px
Checked: bg-primary-600, checkmark-white
Indeterminate: bg-primary-600, dash-white
Focus: ring-2 ring-primary-200
```

### 2.5 Radio Button

```
Size: 18x18px (outer), 8x8px (inner when selected)
Border: 2px solid gray-400
Selected Border: 2px solid primary-600
Selected Inner: bg-primary-600
Focus: ring-2 ring-primary-200
```

## 3. Navigation Components

### 3.1 Sidebar Navigation Item

```
┌─────────────────────────────────────┐
│ [Icon]  Label                  [>]  │
└─────────────────────────────────────┘

Height: 40px
Padding: 12px
Inactive: text-gray-600
Hover: bg-gray-50, text-gray-900
Active: bg-primary-50, text-primary-700, left-border-3px-primary-600
Collapsed: icon-only with tooltip
```

### 3.2 Tab Navigation

```
┌────────────────────────────────────────────┐
│  Tab 1    │  Tab 2    │  Tab 3    │        │
├───────────┴───────────┴───────────┴────────┤
│  Content Area                               │
└────────────────────────────────────────────┘

Tab Height: 44px
Active: text-primary-600, border-bottom-2px-primary-600
Inactive: text-gray-500
Hover: text-gray-700
```

### 3.3 Breadcrumb

```
Home / Profiles / All Profiles / Edit Profile

Separator: "/", color-gray-400
Link: text-primary-600, hover:underline
Current: text-gray-900, font-weight-500
```

### 3.4 Pagination

```
┌──────────────────────────────────────────┐
│ [<]  [1]  [2]  [3]  ...  [10]  [>]      │
│            Showing 1-20 of 150           │
└──────────────────────────────────────────┘

Button: 32x32px, rounded-md
Active: bg-primary-600, text-white
Disabled: opacity-50, cursor-not-allowed
```

## 4. Modal & Dialog

### 4.1 Modal Container

```
┌─────────────────────────────────────────────────────┐
│ ┌───────────────────────────────────────────────┐  │
│ │ Header                              [X]       │  │
│ ├───────────────────────────────────────────────┤  │
│ │                                               │  │
│ │  Body Content                                 │  │
│ │                                               │  │
│ ├───────────────────────────────────────────────┤  │
│ │  [Cancel Button]        [Confirm Button]     │  │
│ └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

Overlay: bg-black-50, backdrop-blur-sm
Modal Max Width: 480px (small), 640px (medium), 800px (large)
Modal Padding: 24px
Border Radius: 12px
Shadow: shadow-xl
Animation: fade-in + scale-up 200ms
```

### 4.2 Confirmation Dialog

```
┌──────────────────────────────────────┐
│  [Icon: Warning/Info/Error]         │
│                                      │
│  Title                              │
│  Description text...                │
│                                      │
│  [Checkbox: Don't ask again]        │
│                                      │
│  [Cancel]           [Confirm]       │
└──────────────────────────────────────┘
```

### 4.3 Drawer (Side Panel)

```
┌──────────────────────────────────────────────┐
│ Drawer Title           [X]                   │
├──────────────────────────────────────────────┤
│                                              │
│  Content                                     │
│                                              │
│  ...                                         │
│                                              │
├──────────────────────────────────────────────┤
│  [Cancel]           [Save]                   │
└──────────────────────────────────────────────┘

Width: 400px (standard), 600px (wide)
Position: Right side
Overlay: Same as modal
Animation: slide-in from right
```

## 5. Data Display

### 5.1 Cards

```
┌─────────────────────────────────────────────┐
│  ┌─────────┐                                │
│  │  Image  │  Card Title                    │
│  │  64x64  │  Subtitle text goes here       │
│  └─────────┘                                │
│                                              │
│  Description text with details...           │
│                                              │
│  [Action 1]  [Action 2]                     │
└─────────────────────────────────────────────┘

Border: 1px solid gray-200
Border Radius: 8px
Padding: 16px
Shadow: shadow-sm
Hover: shadow-md, border-gray-300
```

### 5.2 Tables

```
┌────────────────────────────────────────────────────┐
│ Column A    │ Column B    │ Column C    │ Actions │
├─────────────┼─────────────┼─────────────┼─────────┤
│ Data        │ Data        │ Data        │ [•••]  │
│ Data        │ Data        │ Data        │ [•••]  │
│ Data        │ Data        │ Data        │ [•••]  │
└────────────────────────────────────────────────────┘

Header: bg-gray-50, font-weight-600, text-gray-700
Row Height: 48px
Row Hover: bg-gray-50
Border: 1px solid gray-200
Alternating Rows: optional (disabled by default)
```

### 5.3 Status Badges

```
Active:    bg-green-100, text-green-800, dot-green-500
Inactive:  bg-gray-100, text-gray-800
Error:     bg-red-100, text-red-800
Warning:   bg-yellow-100, text-yellow-800
Pending:   bg-blue-100, text-blue-800

Padding: 4px 8px
Border Radius: 9999px (pill)
Font Size: 12px
Font Weight: 500
```

### 5.4 Progress Indicators

```
Linear Progress Bar:
┌────────────────────────────────────────┐
│ ████████████░░░░░░░░░░░░░░░░  45%    │
└────────────────────────────────────────┘
Height: 8px
Border Radius: 4px
Background: gray-200
Fill: gradient-primary

Circular Progress:
Size: 48x48px (small), 64x64px (medium)
Stroke Width: 4px
```

## 6. Feedback Components

### 6.1 Toast Notifications

```
┌─────────────────────────────────────────────────┐
│ [Icon]  Message text here              [X]    │
└─────────────────────────────────────────────────┘

Position: Top-right
Width: 360px
Padding: 16px
Border Radius: 8px
Duration: 4 seconds (auto-dismiss)
Animation: slide-in from right

Types:
- Success: bg-green-50, border-green-500, icon-green
- Error: bg-red-50, border-red-500, icon-red
- Warning: bg-yellow-50, border-yellow-500, icon-yellow
- Info: bg-blue-50, border-blue-500, icon-blue
```

### 6.2 Tooltips

```
┌─────────────────────┐
│ Tooltip content     │
└─────────────────────┘

Background: gray-900
Text: white
Padding: 8px 12px
Border Radius: 6px
Font Size: 12px
Arrow: 6px
Delay: 300ms (show), 0ms (hide)
Max Width: 200px
```

### 6.3 Empty States

```
┌─────────────────────────────────────────────┐
│                                             │
│           [Large Icon]                      │
│                                             │
│     No Items Found                          │
│     Create your first item to get started   │
│                                             │
│           [Primary Action Button]          │
│                                             │
└─────────────────────────────────────────────┘

Icon Size: 64x64px
Text: text-gray-500
Action Button: centered below text
```

## 7. Interactive States Reference

| Component | Default | Hover | Active | Focus | Disabled |
|-----------|---------|-------|--------|-------|----------|
| Primary Button | bg-primary-600 | bg-primary-700 | bg-primary-800 | ring-2 | opacity-50 |
| Input | border-gray-300 | border-gray-400 | border-primary-500 | ring-2 | bg-gray-100 |
| Checkbox | border-gray-400 | border-primary-400 | bg-primary-600 | ring-2 | opacity-50 |
| Link | text-primary-600 | text-primary-700 | text-primary-800 | ring-2 | text-gray-400 |
