# Quick Responsive Mode Toggle

## 🔄 How to Switch Between Mobile-Only and Responsive Modes

### Method 1: Using `responsive-toggle.css` (Easiest)

**File Location:** `c:\Users\hi\KisanMitra-AI-v2\responsive-toggle.css`

**To Enable MOBILE-ONLY Mode:**
1. Open `responsive-toggle.css`
2. Comment out the "RESPONSIVE MODE" section (lines 12-28)
3. Uncomment the "MOBILE-ONLY MODE" section (lines 38-48)
4. Save file

**To Enable RESPONSIVE Mode:**
1. Open `responsive-toggle.css`
2. Uncomment the "RESPONSIVE MODE" section (lines 12-28)
3. Comment out the "MOBILE-ONLY MODE" section (lines 38-48)
4. Save file

### Method 2: Quick `index.html` Edit

**File:** `c:\Users\hi\KisanMitra-AI-v2\index.html`

**For Mobile-Only (414px):**
```html
<style>
  #root {
    max-width: 414px !important;
    margin: 0 auto !important;
    background: #F5F7FA;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.3);
  }
  
  html, body {
    background: #1F2937;
  }
</style>
```

**For Responsive (Desktop + Mobile):**
```html
<style>
  #root {
    width: 100% !important;
    max-width: none !important;
  }
  
  @media (min-width: 1024px) {
    #root {
      max-width: 1600px !important;
      margin: 0 auto !important;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
    }
  }
</style>
```

### Method 3: CSS Variable Toggle (Advanced)

Add this to `index.html` `<style>` section:
```css
:root {
  --mobile-only: 414px;  /* Change to 'none' for responsive */
}

#root {
  max-width: var(--mobile-only) !important;
}
```

Then just change `414px` to `none` to switch modes!

## 📝 Quick Reference

| Mode | `#root max-width` | Body Background |
|------|-------------------|-----------------|
| Mobile-Only | `414px` | `#1F2937` (dark) |
| Responsive | `none` then `1600px` @1024px | `#E5E7EB` (light grey) |

## ⚡ Keyboard Shortcut Tip

Create a VS Code snippet for even faster toggling:
1. Go to File → Preferences → User Snippets
2. Select "css"
3. Add custom snippets for mobile/responsive toggles
