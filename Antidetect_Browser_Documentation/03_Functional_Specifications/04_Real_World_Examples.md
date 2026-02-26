# Real-World Examples

## 1. Complete Workflow Examples

### 1.1 Web Scraping Workflow

```python
"""
Complete web scraping workflow with stealth browser
"""
from stealth_browser import StealthBrowser, Profile, ProxyManager
import asyncio

class WebScraper:
    def __init__(self):
        self.browser = StealthBrowser()
        self.proxy_manager = ProxyManager()
    
    async def scrape_ecommerce(self, product_urls: list, proxy_pool: list):
        results = []
        
        for idx, url in enumerate(product_urls):
            # Rotate proxy for each product
            proxy = proxy_pool[idx % len(proxy_pool)]
            
            # Create profile with proxy
            profile = await self.create_stealth_profile(
                name=f"scraper_{idx}",
                proxy=proxy,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            try:
                # Start session
                session = await self.browser.start_session(profile)
                
                # Navigate to product page
                await session.navigate(url)
                
                # Extract product data
                product_data = await session.extract({
                    'title': 'h1.product-title',
                    'price': 'span.price',
                    'availability': 'div.stock-status',
                    'reviews': 'span.review-count'
                })
                
                results.append(product_data)
                
                # Close session
                await session.close()
                
                # Wait between requests (rate limiting)
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                await self.handle_error(session, e)
        
        return results
    
    async def create_stealth_profile(self, name: str, proxy: ProxyConfig, user_agent: str):
        profile = Profile(name=name)
        profile.browser.user_agent = user_agent
        profile.browser.canvas_noise = True
        profile.browser.webgl_randomize = True
        profile.browser.webrtc_block = True
        profile.proxy = proxy
        return await self.browser.save_profile(profile)
    
    async def handle_error(self, session, error):
        """Handle scraping errors"""
        if session:
            # Save logs for debugging
            await session.save_logs(f"error_{int(asyncio.get_event_loop().time())}.log")
            await session.close()

# Usage
async def main():
    scraper = WebScraper()
    
    proxy_pool = [
        ProxyConfig('http', '192.168.1.1', 8000),
        ProxyConfig('http', '192.168.1.2', 8000),
        ProxyConfig('http', '192.168.1.3', 8000)
    ]
    
    products = [
        'https://example.com/product/1',
        'https://example.com/product/2',
        'https://example.com/product/3'
    ]
    
    results = await scraper.scrape_ecommerce(products, proxy_pool)
    print(f"Scraped {len(results)} products")

asyncio.run(main())
```

### 1.2 Social Media Management Workflow

```python
"""
Multi-account social media management with isolation
"""
from stealth_browser import StealthBrowser, ProfileManager
import asyncio

class SocialMediaManager:
    def __init__(self):
        self.browser = StealthBrowser()
        self.profile_manager = ProfileManager()
    
    async def setup_accounts(self, accounts: list):
        """Setup multiple social media accounts"""
        for account in accounts:
            # Create isolated profile
            profile = Profile(
                name=f"social_{account['username']}",
                browser_type="chrome",
                resolution="1920x1080",
                timezone=account.get('timezone', 'UTC'),
                language=account.get('language', 'en-US')
            )
            
            # Add account-specific cookies
            profile.cookies = account.get('cookies', [])
            
            # Save profile
            await self.profile_manager.save(profile)
    
    async def post_to_platform(self, platform: str, content: str, accounts: list):
        """Post content to multiple accounts"""
        results = []
        
        for account in accounts:
            # Get profile for this account
            profile = await self.profile_manager.load(f"social_{account['username']}")
            
            try:
                # Start session
                session = await self.browser.start_session(profile)
                
                # Navigate to platform
                await session.navigate(f"https://{platform}.com")
                
                # Login if needed
                if not await session.is_logged_in():
                    await session.login(
                        username=account['username'],
                        password=account['password']
                    )
                
                # Create post
                post_result = await session.create_post(content)
                results.append({
                    'account': account['username'],
                    'success': True,
                    'post_id': post_result.get('id')
                })
                
                await session.close()
                
                # Random delay between accounts
                await asyncio.sleep(random.randint(30, 120))
                
            except Exception as e:
                results.append({
                    'account': account['username'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def monitor_account_health(self, accounts: list):
        """Monitor account health and get metrics"""
        health_data = []
        
        for account in accounts:
            profile = await self.profile_manager.load(f"social_{account['username']}")
            
            # Check for suspensions
            session = await self.browser.start_session(profile)
            is_suspended = await session.check_account_status()
            
            # Get activity metrics
            metrics = await session.get_activity_metrics()
            
            health_data.append({
                'account': account['username'],
                'status': 'suspended' if is_suspended else 'active',
                'posts_today': metrics.get('posts_today', 0),
                'engagement_rate': metrics.get('engagement', 0)
            })
            
            await session.close()
        
        return health_data
```

### 1.3 E-commerce Price Monitoring

```python
"""
Price monitoring across multiple e-commerce sites
"""
from stealth_browser import StealthBrowser
import asyncio
from datetime import datetime

class PriceMonitor:
    def __init__(self):
        self.browser = StealthBrowser()
        self.price_history = {}
    
    async def monitor_prices(self, products: list, check_interval: int = 3600):
        """Monitor prices continuously"""
        while True:
            for product in products:
                try:
                    price_data = await self.check_price(product)
                    self.save_price_data(product['id'], price_data)
                    
                    # Alert if price dropped significantly
                    if self.is_significant_drop(product['id'], price_data['price']):
                        await self.send_alert(product, price_data)
                        
                except Exception as e:
                    print(f"Error monitoring {product['url']}: {e}")
            
            await asyncio.sleep(check_interval)
    
    async def check_price(self, product: dict) -> dict:
        """Check price for a single product"""
        # Use rotating profiles
        profile = await self.browser.get_next_profile()
        session = await self.browser.start_session(profile)
        
        try:
            await session.navigate(product['url'])
            
            # Extract price (site-specific selectors)
            price_selector = product.get('price_selector', '.price')
            price = await session.extract_text(price_selector)
            
            # Extract availability
            availability = await session.extract_text(
                product.get('stock_selector', '.availability')
            )
            
            return {
                'price': self.parse_price(price),
                'currency': product.get('currency', 'USD'),
                'available': 'in stock' in availability.lower(),
                'timestamp': datetime.now().isoformat()
            }
            
        finally:
            await session.close()
    
    def parse_price(self, price_str: str) -> float:
        """Convert price string to float"""
        # Remove currency symbols and whitespace
        cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
        return float(cleaned) if cleaned else 0.0
    
    def is_significant_drop(self, product_id: str, new_price: float) -> bool:
        """Check if price dropped significantly"""
        if product_id not in self.price_history:
            return False
        
        history = self.price_history[product_id]
        if not history:
            return False
        
        old_price = history[-1]['price']
        drop_percent = ((old_price - new_price) / old_price) * 100
        
        return drop_percent >= 20  # 20% drop threshold
    
    async def send_alert(self, product: dict, price_data: dict):
        """Send price drop alert"""
        message = f"""
        � Price Drop Alert!
        
        Product: {product['name']}
        New Price: ${price_data['price']}
        URL: {product['url']}
        """
        
        # Send notification (email, Slack, etc.)
        print(message)
```

## 2. Error Handling Scenarios

### 2.1 Network Timeout Handling

```python
"""
Network timeout and retry handling
"""
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class NetworkErrorHandler:
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def fetch_with_retry(self, session, url: str):
        """Fetch URL with automatic retry"""
        try:
            response = await session.navigate(url, timeout=30)
            return response
        except asyncio.TimeoutError:
            print(f"Timeout fetching {url}, retrying...")
            raise
        except ConnectionError as e:
            print(f"Connection error: {e}, retrying...")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    async def fetch_with_fallback_proxy(self, url: str, proxies: list):
        """Try with fallback proxies"""
        last_error = None
        
        for proxy in proxies:
            try:
                session = await self.browser.start_session(proxy=proxy)
                return await self.fetch_with_retry(session, url)
            except Exception as e:
                last_error = e
                print(f"Proxy {proxy} failed: {e}")
                continue
        
        raise last_error
```

### 2.2 CAPTCHA Handling

```python
"""
CAPTCHA detection and handling
"""
from enum import Enum

class CaptchaType(Enum):
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    IMAGE_CAPTCHA = "image"

class CaptchaHandler:
    def __init__(self, solver_service=None):
        self.solver = solver_service
    
    async def detect_captcha(self, session) -> CaptchaType:
        """Detect if page has CAPTCHA"""
        
        # Check for reCAPTCHA
        recaptcha = await session.evaluate("""
            document.querySelector('.g-recaptcha') !== null ||
            document.querySelector('[data-sitekey]') !== null
        """)
        
        if recaptcha:
            return CaptchaType.RECAPTCHA_V2
        
        # Check for hCaptcha
        hcaptcha = await session.evaluate("""
            document.querySelector('.h-captcha') !== null ||
            document.querySelector('[data-sitekey]') !== null
        """)
        
        if hcaptcha:
            return CaptchaType.HCAPTCHA
        
        # Check for reCAPTCHA v3
        recaptcha_v3 = await session.evaluate("""
            window.grecaptcha && window.grecaptcha.execute
        """)
        
        if recaptcha_v3:
            return CaptchaType.RECAPTCHA_V3
        
        return None
    
    async def solve_captcha(self, session, captcha_type: CaptchaType):
        """Solve CAPTCHA based on type"""
        
        if captcha_type == CaptchaType.RECAPTCHA_V2:
            # Get site key
            site_key = await session.evaluate("""
                document.querySelector('[data-sitekey]').dataset.sitekey
            """)
            
            # Solve via service
            solution = await self.solver.solve_recaptcha_v2(
                url=session.url,
                site_key=site_key
            )
            
            # Submit solution
            await session.evaluate(f"""
                document.getElementById('g-recaptcha-response').value = '{solution}';
            """)
            
            # Submit form if needed
            await session.click('button[type="submit"]')
        
        elif captcha_type == CaptchaType.HCAPTCHA:
            site_key = await session.evaluate("""
                document.querySelector('[data-sitekey]').dataset.sitekey
            """)
            
            solution = await self.solver.solve_hcaptcha(
                url=session.url,
                site_key=site_key
            )
            
            await session.evaluate(f"""
                document.querySelector('[name="h-captcha-response"]').value = '{solution}';
            """)
        
        # Wait for verification
        await asyncio.sleep(2)
```

### 2.3 Profile Corruption Recovery

```python
"""
Profile corruption detection and recovery
"""
import os
import json
from datetime import datetime

class ProfileRecovery:
    def __init__(self, profile_dir: str, backup_dir: str):
        self.profile_dir = profile_dir
        self.backup_dir = backup_dir
    
    async def detect_corruption(self, profile_id: str) -> bool:
        """Detect if profile is corrupted"""
        profile_path = os.path.join(self.profile_dir, f"{profile_id}.json")
        
        try:
            # Check if file exists
            if not os.path.exists(profile_path):
                return True
            
            # Try to load profile
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            
            # Validate required fields
            required = ['id', 'name', 'browser', 'created_at']
            for field in required:
                if field not in profile:
                    return True
            
            return False
            
        except json.JSONDecodeError:
            return True
        except Exception as e:
            print(f"Error checking profile: {e}")
            return True
    
    async def recover_profile(self, profile_id: str) -> bool:
        """Attempt to recover corrupted profile"""
        
        # Check for backup
        backup_path = os.path.join(
            self.backup_dir, 
            f"{profile_id}_{datetime.now().date()}.json"
        )
        
        if os.path.exists(backup_path):
            # Restore from backup
            profile_path = os.path.join(self.profile_dir, f"{profile_id}.json")
            
            with open(backup_path, 'r') as src:
                profile_data = json.load(src)
            
            # Add recovery metadata
            profile_data['recovered_at'] = datetime.now().isoformat()
            profile_data['recovery_notes'] = 'Restored from backup'
            
            with open(profile_path, 'w') as dst:
                json.dump(profile_data, dst, indent=2)
            
            print(f"Profile {profile_id} recovered from backup")
            return True
        
        # No backup, create new profile
        print(f"No backup found for profile {profile_id}")
        return False
    
    async def create_backup(self, profile_id: str):
        """Create profile backup"""
        profile_path = os.path.join(self.profile_dir, f"{profile_id}.json")
        backup_path = os.path.join(
            self.backup_dir,
            f"{profile_id}_{datetime.now().date()}.json"
        )
        
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as src:
                with open(backup_path, 'w') as dst:
                    dst.write(src.read())
            
            print(f"Backup created for {profile_id}")
```

## 3. Performance Optimization

### 3.1 Session Pool Management

```python
"""
Optimized session pool for high-performance operations
"""
import asyncio
from queue import Queue
from contextlib import asynccontextmanager

class SessionPool:
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.available = Queue()
        self.in_use = set()
        self.lock = asyncio.Lock()
    
    async def acquire(self, profile) -> 'BrowserSession':
        """Acquire session from pool"""
        async with self.lock:
            # Try to get from available pool
            if not self.available.empty():
                session = self.available.get()
                
                # Check if session is still valid
                if await session.is_alive():
                    self.in_use.add(session)
                    return session
                else:
                    await session.close()
            
            # Create new session if pool not full
            if len(self.in_use) < self.max_size:
                session = await self.browser.start_session(profile)
                self.in_use.add(session)
                return session
            
            # Wait for available session
            return await self._wait_for_session(profile)
    
    async def release(self, session: 'BrowserSession'):
        """Release session back to pool"""
        async with self.lock:
            if session in self.in_use:
                self.in_use.remove(session)
                
                # Reset session state for reuse
                await session.reset()
                self.available.put(session)
    
    @asynccontextmanager
    async def session(self, profile):
        """Context manager for session"""
        session = await self.acquire(profile)
        try:
            yield session
        finally:
            await self.release(session)
    
    async def cleanup(self):
        """Cleanup all sessions"""
        async with self.lock:
            while not self.available.empty():
                session = self.available.get()
                await session.close()
            
            for session in self.in_use:
                await session.close()
            
            self.in_use.clear()
```

### 3.2 Resource Monitoring

```python
"""
Monitor and optimize resource usage
"""
import psutil
import asyncio

class ResourceMonitor:
    def __init__(self, memory_limit_mb: int = 2048, cpu_limit: int = 80):
        self.memory_limit = memory_limit_mb * 1024 * 1024
        self.cpu_limit = cpu_limit
        self.monitoring = True
    
    async def start_monitoring(self, callback=None):
        """Start resource monitoring"""
        while self.monitoring:
            # Check memory
            memory = psutil.virtual_memory()
            
            if memory.percent > 80:
                print(f"High memory usage: {memory.percent}%")
                if callback:
                    await callback('memory_high', memory.percent)
            
            # Check CPU
            cpu = psutil.cpu_percent(interval=1)
            
            if cpu > self.cpu_limit:
                print(f"High CPU usage: {cpu}%")
                if callback:
                    await callback('cpu_high', cpu)
            
            await asyncio.sleep(5)
    
    async def get_session_resources(self, session) -> dict:
        """Get resource usage for session"""
        try:
            process = session.get_process()
            
            return {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads()
            }
        except:
            return {}
    
    async def optimize_sessions(self, sessions: list):
        """Optimize sessions based on resource usage"""
        for session in sessions:
            resources = await self.get_session_resources(session)
            
            # Kill sessions using too much memory
            if resources.get('memory_mb', 0) > 1024:
                print(f"Closing session {session.id} - high memory")
                await session.close()
```

### 3.3 Caching Strategy

```python
"""
Intelligent caching for better performance
"""
import hashlib
import json
import time
from typing import Optional

class CacheManager:
    def __init__(self, max_age: int = 3600, max_size: int = 1000):
        self.cache = {}
        self.max_age = max_age
        self.max_size = max_size
    
    def _make_key(self, url: str, params: dict = None) -> str:
        """Generate cache key"""
        data = f"{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, url: str, params: dict = None) -> Optional[dict]:
        """Get cached response"""
        key = self._make_key(url, params)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if time.time() - entry['timestamp'] < self.max_age:
                return entry['data']
            else:
                del self.cache[key]
        
        return None
    
    def set(self, url: str, data: dict, params: dict = None):
        """Cache response"""
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]['timestamp']
            )
            del self.cache[oldest_key]
        
        key = self._make_key(url, params)
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    async def cached_request(self, session, url: str, params: dict = None):
        """Make request with caching"""
        # Check cache first
        cached = self.get(url, params)
        if cached:
            return cached
        
        # Make request
        response = await session.fetch(url)
        
        # Cache response
        self.set(url, response, params)
        
        return response
```

## 4. Integration Examples

### 4.1 REST API Integration

```python
"""
FastAPI integration for stealth browser
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
browser = StealthBrowser()

class ProfileCreate(BaseModel):
    name: str
    user_agent: Optional[str] = None
    proxy: Optional[str] = None

class ScrapeRequest(BaseModel):
    url: str
    profile_id: Optional[str] = None
    selectors: dict

@app.post("/profiles")
async def create_profile(profile: ProfileCreate):
    """Create new browser profile"""
    new_profile = await browser.create_profile(
        name=profile.name,
        user_agent=profile.user_agent,
        proxy=profile.proxy
    )
    return new_profile

@app.post("/scrape")
async def scrape_page(request: ScrapeRequest):
    """Scrape page with browser"""
    try:
        session = await browser.start_session(
            profile_id=request.profile_id
        )
        
        await session.navigate(request.url)
        
        results = {}
        for key, selector in request.selectors.items():
            results[key] = await session.extract_text(selector)
        
        await session.close()
        
        return {"success": True, "data": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "sessions": browser.active_sessions}
```

### 4.2 Webhook Integration

```python
"""
Webhook notifications for events
"""
import aiohttp
from enum import Enum

class WebhookEvent(Enum):
    PROFILE_CREATED = "profile.created"
    SESSION_STARTED = "session.started"
    SESSION_ENDED = "session.ended"
    ERROR_OCCURRED = "error.occurred"
    PRICE_ALERT = "price.alert"

class WebhookNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send(self, event: WebhookEvent, data: dict):
        """Send webhook notification"""
        payload = {
            "event": event.value,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(
                self.webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            )
    
    # Convenience methods
    async def notify_profile_created(self, profile_id: str, name: str):
        await self.send(WebhookEvent.PROFILE_CREATED, {
            "profile_id": profile_id,
            "name": name
        })
    
    async def notify_error(self, error: str, context: dict):
        await self.send(WebhookEvent.ERROR_OCCURRED, {
            "error": error,
            "context": context
        })
```
