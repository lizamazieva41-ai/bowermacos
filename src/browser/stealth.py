"""
Advanced stealth fingerprinting module.
Provides comprehensive anti-detection capabilities.
"""

import random
import hashlib
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


def generate_random_string(length: int = 32) -> str:
    """Generate random string for fingerprint randomization."""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(chars) for _ in range(length))


def generate_canvas_noise() -> str:
    """Generate canvas noise to randomize fingerprint."""
    return f"canvas_{generate_random_string(16)}"


def generate_webgl_vendor() -> str:
    """Generate random WebGL vendor."""
    vendors = [
        "Google Inc.",
        "Intel Inc.",
        "NVIDIA Corporation",
        "AMD",
        "Apple Inc.",
    ]
    return random.choice(vendors)


def generate_webgl_renderer() -> str:
    """Generate random WebGL renderer."""
    renderers = [
        "ANGLE (Intel, Intel Iris OpenGL Renderer)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080)",
        "ANGLE (AMD, AMD Radeon Pro 5500M)",
        "Intel Iris Pro Graphics",
        "Apple M1",
    ]
    return random.choice(renderers)


def get_stealth_script() -> str:
    """
    Get comprehensive stealth initialization script.
    This script runs on every page load to prevent detection.
    """
    return f"""
(function() {{
    // === Navigator WebDriver ===
    Object.defineProperty(navigator, 'webdriver', {{
        get: () => undefined,
        configurable: true
    }});

    // === Navigator Plugins ===
    Object.defineProperty(navigator, 'plugins', {{
        get: () => [1, 2, 3, 4, 5],
        configurable: true
    }});

    // === Navigator Languages ===
    Object.defineProperty(navigator, 'languages', {{
        get: () => ['en-US', 'en', 'en-GB'],
        configurable: true
    }});

    // === Permissions Query ===
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({{ state: Notification.permission }}) :
            originalQuery(parameters)
    );

    // === Chrome Runtime ===
    window.chrome = {{ 
        runtime: {{}},
        loadTimes: () => ({{
            commitContentPatchEnabled: false,
            wasAlternateProtocolAvailable: false,
            wasNpnNegotiated: false,
            npnNegotiatedProtocol: '',
            pendingBackgroundXHRBytes: 0,
            proxyServer: '',
            proxyPacScript: '',
            requestTime: Date.now() / 1000,
            responseTime: Date.now() / 1000,
            sendFinishLength: 0,
            sendStartLength: 0,
            sslCipherGroupId: 0,
            sslClientRandom: '',
            sslFeatureVersion: 0,
            sslKeyArg: '',
            sslKeys: '',
            sslNegotiatedProtocol: '',
            connectionInfo: '',
            eagerFirstContentfulPaint_MS: 0,
            eagerFirstEmptyTime_MS: 0,
            eagerFirstPaint_MS: 0,
            eagerNextHop2_MS: 0,
            eagerNextHop_MS: 0,
            firstContentfulPaint_MS: 0,
            firstLayoutTime_MS: 0,
            firstPaintTime_MS: 0,
            loadEventEnd: 0,
            loadEventStart: 0,
            navigationType: '',
            newEndTime_MS: 0,
            newStartTime_MS: 0,
            npnNegotiatedProtocolNetworkIsolationKey: '',
            optimizerStableId: '',
            originalURL: '',
            pushStartTime: 0,
            redirectEndTime: 0,
            redirectStartTime: 0,
            requestTime: 0,
            responseTime: 0,
            sendEndTime: 0,
            sendStartTime: 0,
            slateDelta: 0,
            slateTime: 0,
            startTime: 0,
            tcpConnEndTime: 0,
            tcpConnStartTime: 0,
            terminalType: '',
            timeSinceAPIAvailable: 0,
            timeSinceCrossSiteLoadStartVisible: 0,
            timeSinceNonAPILoadStartEager: 0,
            unloadEventEnd: 0,
            unloadEventStart: 0
        }})
    }};

    // === Screen Properties ===
    Object.defineProperty(screen, 'availWidth', {{
        get: () => 1920,
        configurable: true
    }});
    Object.defineProperty(screen, 'availHeight', {{
        get: () => 1080,
        configurable: true
    }});
    Object.defineProperty(screen, 'width', {{
        get: () => 1920,
        configurable: true
    }});
    Object.defineProperty(screen, 'height', {{
        get: () => 1080,
        configurable: true
    }});

    // === Hardware Concurrency ===
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => 8,
        configurable: true
    }});

    // === Device Memory ===
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => 8,
        configurable: true
    }});

    // === Connection ===
    if (navigator.connection) {{
        Object.defineProperty(navigator.connection, 'downlink', {{
            get: () => 10,
            configurable: true
        }});
        Object.defineProperty(navigator.connection, 'effectiveType', {{
            get: () => '4g',
            configurable: true
        }});
        Object.defineProperty(navigator.connection, 'rtt', {{
            get: () => 50,
            configurable: true
        }});
        Object.defineProperty(navigator.connection, 'saveData', {{
            get: () => false,
            configurable: true
        }});
    }}

    console.log('Stealth mode activated');
}})();
"""


def get_webgl_stealth_script() -> str:
    """
    WebGL fingerprint spoofing.
    Overrides WebGL rendering to prevent canvas fingerprinting.
    """
    vendor = generate_webgl_vendor()
    renderer = generate_webgl_renderer()

    return f"""
(function() {{
    const getParameter = WebGLRenderingContext.prototype.getParameter;

    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        if (parameter === 37445) {{
            return '{vendor}';
        }}
        if (parameter === 37446) {{
            return '{renderer}';
        }}
        return getParameter.apply(this, arguments);
    }};

    if (WebGL2RenderingContext) {{
        WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{vendor}';
            }}
            if (parameter === 37446) {{
                return '{renderer}';
            }}
            return getParameter.apply(this, arguments);
        }};
    }}

    const originalGetExtension = WebGLRenderingContext.prototype.getExtension;
    WebGLRenderingContext.prototype.getExtension = function(name) {{
        const ext = originalGetExtension.apply(this, arguments);
        if (name === 'WEBGL_debug_renderer_info' && ext) {{
            const origGetParameter = ext.getParameter;
            ext.getParameter = function(parameter) {{
                if (parameter === 37445) {{
                    return '{vendor}';
                }}
                if (parameter === 37446) {{
                    return '{renderer}';
                }}
                return origGetParameter.apply(this, arguments);
            }};
        }}
        return ext;
    }};

    console.log('WebGL stealth activated');
}})();
"""


def get_canvas_stealth_script() -> str:
    """
    Canvas fingerprint randomization.
    Adds noise to canvas operations to prevent fingerprinting.
    """
    return """
(function() {
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const originalToBlob = HTMLCanvasElement.prototype.toBlob;
    const originalGetContext = HTMLCanvasElement.prototype.getContext;

    function addCanvasNoise(canvas) {
        try {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.fillStyle = 'rgba(0,0,0,0.00001)';
                ctx.fillRect(0, 0, 1, 1);
            }
        } catch(e) {}
    }

    HTMLCanvasElement.prototype.toDataURL = function() {
        if (this.width > 0 && this.height > 0) {
            addCanvasNoise(this);
        }
        return originalToDataURL.apply(this, arguments);
    };

    HTMLCanvasElement.prototype.toBlob = function() {
        if (this.width > 0 && this.height > 0) {
            addCanvasNoise(this);
        }
        return originalToBlob.apply(this, arguments);
    };

    HTMLCanvasElement.prototype.getContext = function(contextType) {
        const ctx = originalGetContext.apply(this, arguments);
        if (ctx && (contextType === '2d' || contextType === 'webgl' || contextType === 'webgl2')) {
            const originalFillText = ctx.fillText;
            const originalStrokeText = ctx.strokeText;
            const originalFillRect = ctx.fillRect;
            const originalDrawImage = ctx.drawImage;

            ctx.fillText = function() {
                this.shadowColor = this.shadowColor || 'rgba(0,0,0,0)';
                return originalFillText.apply(this, arguments);
            };

            ctx.strokeText = function() {
                this.shadowColor = this.shadowColor || 'rgba(0,0,0,0)';
                return originalStrokeText.apply(this, arguments);
            };

            ctx.fillRect = function() {
                if (Math.random() > 0.5) {
                    this.fillStyle = 'rgba(0,0,0,0.000001)';
                }
                return originalFillRect.apply(this, arguments);
            };

            ctx.drawImage = function() {
                return originalDrawImage.apply(this, arguments);
            };
        }
        return ctx;
    };

    console.log('Canvas stealth activated');
})();
"""


def get_webrtc_stealth_script() -> str:
    """
    WebRTC protection.
    Disables WebRTC to prevent IP leaks.
    """
    return """
(function() {
    // Disable RTCPeerConnection
    const OriginalRTCPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection;
    
    window.RTCPeerConnection = function() {
        console.log('RTCPeerConnection blocked');
        return null;
    };
    
    window.RTCPeerConnection.prototype = OriginalRTCPeerConnection ? OriginalRTCPeerConnection.prototype : {};
    
    // Disable getUserMedia
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
        navigator.mediaDevices.getUserMedia = function(constraints) {
            console.log('getUserMedia blocked');
            return Promise.reject(new Error('getUserMedia disabled'));
        };
    }

    // Disable enumerateDevices
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
        const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices.bind(navigator.mediaDevices);
        navigator.mediaDevices.enumerateDevices = function() {
            return Promise.resolve([]);
        };
    }

    // Override MediaStreamTrack
    if (window.MediaStreamTrack) {
        window.MediaStreamTrack.getSources = function() {
            return [];
        };
    }

    // Remove WebRTC leak detection
    window.RTCSessionDescription = null;
    window.RTCIceCandidate = null;

    // Disable peer connection
    window.webkitGetUserMedia = null;
    window.mozGetUserMedia = null;
    window.msGetUserMedia = null;

    console.log('WebRTC protection activated');
})();
"""


def get_audio_stealth_script() -> str:
    """
    AudioContext fingerprint spoofing.
    Prevents audio fingerprinting by adding noise and randomizing output.
    """
    return """
(function() {
    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
    const originalCreateOscillator = AudioContext.prototype.createOscillator;
    const originalCreateDynamicsCompressor = AudioContext.prototype.createDynamicsCompressor;
    const originalCreateGain = AudioContext.prototype.createGain;
    const originalCreateScriptProcessor = AudioContext.prototype.createScriptProcessor;
    const originalCreateBufferSource = AudioContext.prototype.createBufferSource;

    AudioContext.prototype.createAnalyser = function() {
        const analyser = originalCreateAnalyser.apply(this, arguments);
        if (analyser) {
            const originalGetByteFrequencyData = analyser.getByteFrequencyData;
            const originalGetByteTimeDomainData = analyser.getByteTimeDomainData;
            
            analyser.getByteFrequencyData = function(array) {
                for (let i = 0; i < array.length; i++) {
                    array[i] = Math.max(0, Math.min(255, array[i] + (Math.random() - 0.5) * 3));
                }
                return originalGetByteFrequencyData.apply(this, arguments);
            };
            
            if (originalGetByteTimeDomainData) {
                analyser.getByteTimeDomainData = function(array) {
                    for (let i = 0; i < array.length; i++) {
                        array[i] = Math.max(0, Math.min(255, array[i] + (Math.random() - 0.5) * 2));
                    }
                    return originalGetByteTimeDomainData.apply(this, arguments);
                };
            }
        }
        return analyser;
    };

    AudioContext.prototype.createOscillator = function() {
        const oscillator = originalCreateOscillator.apply(this, arguments);
        const originalStart = oscillator.start;
        const originalStop = oscillator.stop;
        
        oscillator.start = function(when = 0) {
            return originalStart.call(this, when + Math.random() * 0.001);
        };
        
        oscillator.stop = function(when = 0) {
            return originalStop.call(this, when + Math.random() * 0.001);
        };
        
        return oscillator;
    };

    AudioContext.prototype.createGain = function() {
        const gain = originalCreateGain.apply(this, arguments);
        const originalGainValue = Object.getOwnPropertyDescriptor(gain.gain, 'value');
        
        if (originalGainValue && originalGainValue.configurable) {
            Object.defineProperty(gain.gain, 'value', {
                get: function() {
                    return originalGainValue.get.call(this);
                },
                set: function(val) {
                    return originalGainValue.set.call(this, val * (1 + (Math.random() - 0.5) * 0.01));
                },
                configurable: true
            });
        }
        
        return gain;
    };

    AudioContext.prototype.createBufferSource = function() {
        const source = originalCreateBufferSource.apply(this, arguments);
        const originalStart = source.start;
        
        source.start = function(when = 0) {
            return originalStart.call(this, when + Math.random() * 0.0001);
        };
        
        return source;
    };

    const originalAudioContext = window.AudioContext;
    if (window.AudioContext) {
        window.AudioContext = function() {
            const ctx = new originalAudioContext();
            const originalResume = ctx.resume;
            ctx.resume = function() {
                return originalResume.apply(this, arguments).then(() => {
                    if (ctx.state === 'running') {
                        ctx.suspend();
                        ctx.resume();
                    }
                });
            };
            return ctx;
        };
        window.AudioContext.prototype = originalAudioContext.prototype;
    }

    if (window.OfflineAudioContext) {
        const originalOffline = window.OfflineAudioContext;
        window.OfflineAudioContext = function() {
            return new originalOffline(arguments[0], arguments[1], arguments[2]);
        };
    }

    console.log('AudioContext stealth activated');
})();
"""


def get_font_stealth_script() -> str:
    """
    Font fingerprint protection.
    Limits exposed fonts to prevent enumeration.
    """
    # Common safe fonts that are widely available
    safe_fonts = [
        "Arial",
        "Arial Black",
        "Arial Narrow",
        "Calibri",
        "Cambria",
        "Cambria Math",
        "Comic Sans MS",
        "Consolas",
        "Courier",
        "Courier New",
        "Georgia",
        "Helvetica",
        "Impact",
        "Lucida Console",
        "Lucida Sans Unicode",
        "Microsoft Sans Serif",
        "Palatino Linotype",
        "Segoe UI",
        "Tahoma",
        "Times",
        "Times New Roman",
        "Trebuchet MS",
        "Verdana",
        "Monaco",
        "Menlo",
        "Ubuntu",
        "Roboto",
    ]
    fonts_js = "['" + "','".join(safe_fonts) + "']"

    script = """
(function() {
    // Limit fonts detection via CSS
    const originalGetComputedStyle = window.getComputedStyle;
    window.getComputedStyle = function(element, pseudo) {
        const style = originalGetComputedStyle.apply(this, arguments);
        
        // Return safe font family
        const fontFamily = style.fontFamily;
        if (fontFamily) {
            Object.defineProperty(style, 'fontFamily', {
                get: () => 'Arial, sans-serif',
                configurable: true
            });
        }
        
        return style;
    };

    // Hide extra fonts from detection
    const SAFE_FONTS = """ + fonts_js + """;
    Object.defineProperty(document.fonts, 'check', {
        value: function(font) {
            return SAFE_FONTS.some(f => font.includes(f));
        },
        writable: false
    });

    console.log('Font stealth activated');
})();
"""
    return script


def get_timezone_stealth_script(timezone: str = "UTC") -> str:
    """
    Timezone spoofing script.
    Spoofs timezone to match proxy location.
    """
    return f"""
(function() {{
    const TIMEZONE = '{timezone}';
    
    if (Intl.DateTimeFormat) {{
        const originalDateTimeFormat = Intl.DateTimeFormat;
        Intl.DateTimeFormat = function(locale, options) {{
            options = options || {{}};
            options.timeZone = options.timeZone || TIMEZONE;
            return new originalDateTimeFormat(locale, options);
        }};
        
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
            return {{
                timeZone: TIMEZONE,
                locale: 'en-US'
            }};
        }};
    }}
    
    if (Date) {{
        const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset = function() {{
            return 0;
        }};
    }}
    
    console.log('Timezone spoofed to:', TIMEZONE);
}})();
"""


def get_all_stealth_scripts(timezone: str = "UTC") -> List[str]:
    """Get all stealth scripts combined."""
    from src.proxy.dns_leak import get_dns_leak_protection_script

    return [
        get_stealth_script(),
        get_webgl_stealth_script(),
        get_canvas_stealth_script(),
        get_webrtc_stealth_script(),
        get_audio_stealth_script(),
        get_font_stealth_script(),
        get_timezone_stealth_script(timezone),
        get_dns_leak_protection_script(),
    ]


def get_combined_stealth_script(timezone: str = "UTC") -> str:
    """Get all stealth scripts combined into one."""
    scripts = get_all_stealth_scripts(timezone)
    return "\n\n".join(scripts)
