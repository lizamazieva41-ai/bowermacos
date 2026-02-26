# 1. STEALTH IMPLEMENTATION GUIDE

## Overview
This document provides detailed implementation for anti-detection features.

---

## 1. Navigator Webdriver Override

### Purpose
Prevent detection by hiding automation flags.

### Implementation
```python
# Playwright Python
await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    delete navigator.webdriver;
""")
```

---

## 2. WebGL Spoofing

### Purpose
Mask the actual WebGL renderer.

### Implementation
```python
await page.add_init_script("""
    // Override WebGL Vendor
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {
        if (param === 37445) return 'Google Inc.';
        if (param === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 620)';
        return getParameter.call(this, param);
    };
    
    // Override WebGL2
    const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
    WebGL2RenderingContext.prototype.getParameter = function(param) {
        if (param === 37445) return 'Google Inc.';
        if (param === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 620)';
        return getParameter2.call(this, param);
    };
""")
```

---

## 3. Canvas Fingerprint Protection

### Purpose
Randomize canvas to prevent fingerprinting.

### Implementation
```python
await page.add_init_script("""
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, encoderOptions) {
        // Add subtle noise
        const ctx = this.getContext('2d');
        if (ctx) {
            const imageData = ctx.getImageData(0, 0, this.width, this.height);
            const data = imageData.data;
            for (let i = 0; i < data.length; i += 4) {
                if (Math.random() > 0.5) {
                    data[i] = (data[i] + 1) % 256;
                }
            }
            ctx.putImageData(imageData, 0, 0);
        }
        return originalToDataURL.call(this, type, encoderOptions);
    };
""")
```

---

## 4. WebRTC Protection

### Purpose
Prevent IP leak through WebRTC.

### Implementation
```python
# Option 1: Chrome Flags
launch_args = [
    '--disable-webrtc',
    '--force-webrtc-ip-handling-policy=disable_non_proxied_udp',
    '--disable-media-session',
]

# Option 2: Init Script
await page.add_init_script("""
    // Disable WebRTC
    window.RTCPeerConnection = undefined;
    window.RTCSessionDescription = undefined;
    window.RTCIceCandidate = undefined;
    window.webkitRTCPeerConnection = undefined;
    
    // Override getUserMedia
    navigator.mediaDevices.getUserMedia = async () => {
        throw new Error('NotAllowedError');
    };
""")
```

---

## 5. User-Agent Spoofing

### Purpose
Customize user agent string.

### Implementation
```python
# Via Playwright Context
context = await browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport={'width': 1920, 'height': 1080},
    locale='en-US',
    timezone_id='America/New_York',
)
```

---

## 6. Timezone Spoofing

### Purpose
Match timezone with proxy location.

### Implementation
```python
# Via Chrome flag
args = ['--time-zone=America/New_York']

# Or via Playwright
context = await browser.new_context(
    timezone_id='America/New_York'
)
```

---

## 7. Language & Locale

### Purpose
Set consistent language preferences.

### Implementation
```python
context = await browser.new_context(
    locale='en-US,en;q=0.9',
    languages=['en-US', 'en'],
    permissions=['geolocation'],
)
```

---

## 8. Complete Stealth Setup Example

```python
async def create_stealth_context(browser, profile_config):
    """Create a stealth browser context with all anti-detection measures."""
    
    # Prepare stealth scripts
    stealth_scripts = """
        // Hide webdriver
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        
        // WebGL override
        const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Google Inc.';
            if (param === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 620)';
            return originalGetParameter.call(this, param);
        };
        
        // Canvas noise
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {
            return originalToDataURL.apply(this, arguments);
        };
    """
    
    # Build context with profile settings
    context = await browser.new_context(
        user_agent=profile_config.get('user_agent'),
        viewport=profile_config.get('viewport', {'width': 1920, 'height': 1080}),
        locale=profile_config.get('locale', 'en-US'),
        timezone_id=profile_config.get('timezone', 'UTC'),
        permissions=['geolocation'],
        extra_http_headers={
            'Accept-Language': profile_config.get('language', 'en-US,en;q=0.9'),
        }
    )
    
    # Apply stealth to all pages
    await context.add_init_script(stealth_scripts)
    
    return context
```

---

## 9. Testing Anti-Detection

### Test Sites
| Site | URL | Expected |
|------|-----|----------|
| Bot detection | https://bot.sannysoft.com | Pass |
| Fingerprint | https://amiunique.org | Randomized |
| WebGL | https://webglsamples.org | No leak |

### Verification Commands
```python
# Check navigator.webdriver
await page.evaluate('navigator.webdriver')

# Check WebGL vendor
await page.evaluate('''
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl');
    gl.getParameter(gl.VENDOR);
''')

# Check timezone
await page.evaluate('Intl.DateTimeFormat().resolvedOptions().timeZone')
```

---

*Document ID: ABB-V2-DOC-1501*
