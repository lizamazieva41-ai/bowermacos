# Accessibility

## 1. WCAG 2.1 AA Compliance

### 1.1 Guidelines Overview

This application follows WCAG 2.1 Level AA guidelines, ensuring accessibility for users with disabilities.

| Principle | Level | Implementation |
|-----------|-------|----------------|
| Perceivable | A, AA | All content is presentable in perceivable ways |
| Operable | A, AA | All functionality is operable by all users |
| Understandable | A, AA | Content and interface are understandable |
| Robust | A, AA | Content is robust enough for assistive technologies |

### 1.2 Target Standards

- **WCAG 2.1 Level AA**: Minimum compliance
- **WCAG 2.1 Level AAA**: Where practical, for enhanced accessibility
- **Section 508**: Required for government deployments
- **EN 301 549**: Required for European Union deployments

## 2. Color Contrast Requirements

### 2.1 Minimum Contrast Ratios

| Context | Ratio | Example |
|---------|-------|---------|
| Normal Text | 4.5:1 | Gray 700 (#374151) on White |
| Large Text (18px+) | 3:1 | Gray 600 (#4B5563) on White |
| UI Components | 3:1 | Border/Icon on background |
| Text over Images | 3:1 | Overlay with sufficient contrast |
| Status Indicators | 3:1 | Color + Icon/Text combined |

### 2.2 Contrast Verification

```
Primary Action Button:
- Default: Primary 600 (#2563EB) on White → 4.6:1 ✓
- Hover: Primary 700 (#1D4ED8) on White → 5.5:1 ✓

Body Text:
- Primary: Gray 700 (#374151) on Gray 50 (#F9FAFB) → 10.9:1 ✓
- Secondary: Gray 500 (#6B7280) on Gray 50 → 6.3:1 ✓
- Muted: Gray 400 (#9CA3AF) on Gray 50 → 3.1:1 ✓

Status Colors:
- Success text on white: 4.5:1 ✓
- Error text on white: 4.5:1 ✓
```

### 2.3 Color Independence

All status information is conveyed through:

- Iconography (checkmarks, X icons, warning triangles)
- Text labels ("Active", "Error", "Warning")
- Patterns (for data visualization where applicable)
- Never color alone

## 3. Keyboard Navigation

### 3.1 Required Keyboard Interactions

| Action | Keyboard Shortcut |
|--------|-------------------|
| Navigate forward | Tab |
| Navigate backward | Shift + Tab |
| Activate button/Link | Enter / Space |
| Open dropdown | Enter / Space / Arrow Down |
| Close modal | Escape |
| Select option | Arrow Keys + Enter |
| Multi-select | Ctrl/Cmd + Arrow |

### 3.2 Focus Indicators

```
Default (not visible):
outline: none

Focused Element:
outline: 2px solid Primary 500
outline-offset: 2px
border-color: Primary 500

Exception - Buttons:
outline: none (use border change)
border: 2px solid Primary 600

Visible Focus (high contrast mode):
outline: 3px solid Black
outline-offset: 2px
```

### 3.3 Focus Order

1. Logical reading order (left to right, top to bottom)
2. Skip links to main content
3. Modal focus trapped within modal
4. Return focus to triggering element on close

### 3.4 Skip Link Implementation

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <nav>...</nav>
  <main id="main-content">
    <!-- Page content -->
  </main>
</body>

<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: primary-600;
  color: white;
  padding: 8px;
  z-index: 100;
}
.skip-link:focus {
  top: 0;
}
</style>
```

## 4. Screen Reader Support

### 4.1 Semantic HTML

```html
<!-- Headings -->
<h1>Page Title</h1>
<h2>Section Title</h2>
<h3>Subsection</h3>

<!-- Navigation -->
<nav aria-label="Main navigation">
<nav aria-label="Breadcrumb">

<!-- Buttons -->
<button>Action</button>
<!-- Not: <div onclick="..."> -->

<!-- Forms -->
<label for="email">Email</label>
<input id="email" type="email" aria-required="true">

<!-- Status -->
<span role="status">Saved</span>
<span role="alert">Error message</span>
```

### 4.2 ARIA Attributes

| Attribute | Usage |
|-----------|-------|
| aria-label | Accessible name for interactive elements |
| aria-describedby | Links to descriptive text |
| aria-required | Indicates required fields |
| aria-invalid | Indicates validation errors |
| aria-hidden | Hides decorative elements |
| aria-expanded | Toggle state for accordions/dropdowns |
| aria-selected | Current selection in tabs/lists |
| aria-live | Dynamic content updates |
| role="alert" | Important announcements |
| role="dialog" | Modal dialogs |

### 4.3 Form Accessibility

```html
<form>
  <div class="form-group">
    <label for="username">Username <span aria-hidden="true">*</span></label>
    <input 
      id="username" 
      type="text" 
      aria-required="true"
      aria-describedby="username-help username-error"
    >
    <span id="username-help" class="help-text">3-20 characters</span>
    <span id="username-error" class="error-text" role="alert" hidden>
      Username is required
    </span>
  </div>
</form>
```

## 5. Interactive Elements

### 5.1 Button Accessibility

```html
<!-- Primary Button -->
<button class="btn btn-primary">
  Save Changes
</button>

<!-- Icon Button with Label -->
<button class="btn-icon" aria-label="Close dialog">
  <svg aria-hidden="true">...</svg>
</button>

<!-- Toggle Button -->
<button 
  aria-pressed="false"
  aria-label="Enable notifications"
>
  <svg aria-hidden="true">...</svg>
</button>
```

### 5.2 Modal Accessibility

```html
<div 
  role="dialog" 
  aria-modal="true" 
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <h2 id="modal-title">Confirm Action</h2>
  <p id="modal-description">Are you sure you want to proceed?</p>
  <!-- Focus trap inside -->
  <button>Cancel</button>
  <button>Confirm</button>
</div>
```

### 5.3 Dropdown Accessibility

```html
<div class="dropdown">
  <button 
    aria-haspopup="listbox" 
    aria-expanded="false" 
    aria-controls="dropdown-list"
    id="dropdown-trigger"
  >
    Select Option
    <svg aria-hidden="true">...</svg>
  </button>
  <ul 
    role="listbox" 
    id="dropdown-list" 
    aria-labelledby="dropdown-trigger"
    hidden
  >
    <li role="option">Option 1</li>
    <li role="option">Option 2</li>
  </ul>
</div>
```

## 6. Text Accessibility

### 6.1 Font Sizing

- Minimum body text: 13px (0.8125rem)
- Default body text: 14px (0.875rem)
- Line height: 1.5 minimum
- Letter spacing: Normal (avoid negative)

### 6.2 Text Scaling

- Support browser zoom up to 200%
- No fixed widths that break at increased text size
- Responsive containers that reflow content

### 6.3 Link Accessibility

```html
<!-- Descriptive Link Text -->
<a href="/profile/edit">Edit profile settings</a>

<!-- Avoid: -->
<a href="/profile/edit">Click here</a>
<a href="/profile/edit">Here</a>

<!-- Icon Links -->
<a href="/export" aria-label="Export data as CSV">
  <svg aria-hidden="true">...</svg>
</a>
```

## 7. Testing Checklist

### 7.1 Automated Testing

- [ ] WAVE evaluation
- [ ] axe-core automated tests
- [ ] Lighthouse accessibility audit
- [ ] Color contrast analyzer

### 7.2 Manual Testing

- [ ] Navigate entire application with keyboard only
- [ ] Test with screen reader (NVDA, VoiceOver, JAWS)
- [ ] Test with browser zoom at 200%
- [ ] Test reduced motion preferences
- [ ] Test high contrast mode

### 7.3 Device Testing

- [ ] Test on Windows with narrator
- [ ] Test on macOS with VoiceOver
- [ ] Test on mobile/tablet with VoiceOver
- [ ] Test touch target sizes (44x44px minimum)

## 8. Accessibility Features

### 8.1 Reduce Motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### 8.2 High Contrast Mode

```css
@media (prefers-contrast: more) {
  --border-width: 2px;
  --outline-width: 2px;
  /* Force higher contrast colors */
}
```

### 8.3 Screen Reader Announcements

```javascript
// Announce dynamic content updates
const announce = (message) => {
  const liveRegion = document.getElementById('live-region');
  liveRegion.textContent = '';
  setTimeout(() => {
    liveRegion.textContent = message;
  }, 100);
};

// Usage
announce('Profile saved successfully');
announce('Error: Invalid email address');
```

## 9. Training & Documentation

### 9.1 Developer Guidelines

All developers must:

1. Complete WCAG 2.1 fundamentals training
2. Use semantic HTML as first choice
3. Test with keyboard before committing
4. Include aria-labels where needed
5. Review accessibility before code review

### 9.2 QA Accessibility Testing

- Include accessibility tests in regression suite
- Test new features with screen readers
- Document accessibility considerations in tickets
