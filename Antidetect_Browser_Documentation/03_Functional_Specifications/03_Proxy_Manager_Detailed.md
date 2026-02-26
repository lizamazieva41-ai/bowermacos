# Proxy Manager - Detailed Documentation

## 1. Proxy Configuration

### 1.1 Proxy Types Supported

| Type | Protocol | Authentication | Use Case |
|------|----------|----------------|-----------|
| HTTP | HTTP | Basic/Digest | Web scraping, general |
| HTTPS | HTTPS | Basic/Digest | Secure connections |
| SOCKS4 | SOCKS4 | IP-based | Legacy systems |
| SOCKS5 | SOCKS5 | IP/Username | Gaming, P2P |
| SSH | SSH Tunnel | Key/Certificate | High security |

### 1.2 Proxy Configuration per Profile

```python
# Python - Proxy Configuration
class ProxyConfig:
    def __init__(self, proxy_type: str, host: str, port: int, 
                 username: str = None, password: str = None):
        self.proxy_type = proxy_type  # http, https, socks5
        self.host = host
        self.port = port
        self.username = username
        self.password = password
    
    def to_dict(self) -> dict:
        return {
            "type": self.proxy_type,
            "host": self.host,
            "port": self.port,
            "auth": {
                "username": self.username,
                "password": self.password
            } if self.username else None
        }
    
    def to_curl_format(self) -> str:
        if self.username:
            return f"--proxy {self.proxy_type}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"--proxy {self.proxy_type}://{self.host}:{self.port}"

# C# - Proxy Configuration
public class ProxyConfig
{
    public ProxyType Type { get; set; }
    public string Host { get; set; }
    public int Port { get; set; }
    public string Username { get; set; }
    public string Password { get; set; }
    
    public WebProxy ToWebProxy()
    {
        var proxy = new WebProxy($"{Host}:{Port}");
        if (!string.IsNullOrEmpty(Username))
        {
            proxy.Credentials = new NetworkCredential(Username, Password);
        }
        return proxy;
    }
}

public enum ProxyType
{
    HTTP,
    HTTPS,
    SOCKS4,
    SOCKS5
}
```

### 1.3 Profile-Proxy Association

```python
class ProfileProxyManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def assign_proxy_to_profile(self, profile_id: str, proxy_id: str):
        """Assign a proxy to a specific profile"""
        query = """
            UPDATE profiles 
            SET proxy_id = ?, updated_at = NOW()
            WHERE id = ?
        """
        self.db.execute(query, (proxy_id, profile_id))
    
    def get_profile_proxy(self, profile_id: str) -> ProxyConfig:
        """Get proxy configuration for a profile"""
        query = """
            SELECT p.*, pr.host, pr.port, pr.type, pr.username, pr.password
            FROM profiles p
            LEFT JOIN proxies pr ON p.proxy_id = pr.id
            WHERE p.id = ?
        """
        row = self.db.fetchone(query, (profile_id,))
        if row:
            return ProxyConfig(
                proxy_type=row['type'],
                host=row['host'],
                port=row['port'],
                username=row['username'],
                password=row['password']
            )
        return None
    
    def clear_profile_proxy(self, profile_id: str):
        """Remove proxy from profile"""
        query = "UPDATE profiles SET proxy_id = NULL WHERE id = ?"
        self.db.execute(query, (profile_id,))
```

## 2. Proxy Rotation Logic

### 2.1 Round-Robin Rotation

```python
class RoundRobinProxyRotation:
    def __init__(self, proxy_list: list):
        self.proxies = proxy_list
        self.current_index = 0
    
    def get_next_proxy(self) -> ProxyConfig:
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def reset(self):
        self.current_index = 0
```

### 2.2 Random Rotation

```python
import random

class RandomProxyRotation:
    def __init__(self, proxy_list: list):
        self.proxies = proxy_list
    
    def get_next_proxy(self) -> ProxyConfig:
        return random.choice(self.proxies)
    
    def get_random_excluding(self, exclude: ProxyConfig) -> ProxyConfig:
        available = [p for p in self.proxies if p != exclude]
        return random.choice(available) if available else exclude
```

### 2.3 Smart Rotation (Failure-Aware)

```python
import time
from collections import defaultdict

class SmartProxyRotation:
    def __init__(self, proxy_list: list):
        self.proxies = proxy_list
        self.failure_count = defaultdict(int)
        self.last_failure = defaultdict(float)
        self.min_retry_interval = 60  # seconds
    
    def get_next_proxy(self) -> ProxyConfig:
        # Filter out proxies that recently failed
        available = [
            p for p in self.proxies 
            if self._is_proxy_available(p)
        ]
        
        if not available:
            # All proxies failed, reset and use any
            available = self.proxies
            self._reset_failures()
        
        # Select proxy with lowest failure count
        return min(available, key=lambda p: self.failure_count[p.host])
    
    def _is_proxy_available(self, proxy: ProxyConfig) -> bool:
        last_fail = self.last_failure.get(proxy.host, 0)
        return (time.time() - last_fail) > self.min_retry_interval
    
    def report_failure(self, proxy: ProxyConfig):
        self.failure_count[proxy.host] += 1
        self.last_failure[proxy.host] = time.time()
    
    def report_success(self, proxy: ProxyConfig):
        self.failure_count[proxy.host] = max(0, self.failure_count[proxy.host] - 1)
    
    def _reset_failures(self):
        self.failure_count.clear()
        self.last_failure.clear()
```

### 2.4 Sticky Session Rotation

```python
class StickyProxyRotation:
    """Keep same proxy for a session, rotate after timeout"""
    
    def __init__(self, proxy_list: list, sticky_duration: int = 300):
        self.proxies = proxy_list
        self.sticky_duration = sticky_duration
        self.session_proxies = {}  # session_id -> proxy
    
    def get_proxy_for_session(self, session_id: str) -> ProxyConfig:
        now = time.time()
        
        # Check existing sticky proxy
        if session_id in self.session_proxies:
            proxy, assigned_at = self.session_proxies[session_id]
            if (now - assigned_at) < self.sticky_duration:
                return proxy
        
        # Assign new proxy
        proxy = random.choice(self.proxies)
        self.session_proxies[session_id] = (proxy, now)
        return proxy
    
    def release_session(self, session_id: str):
        if session_id in self.session_proxies:
            del self.session_proxies[session_id]
```

## 3. Proxy Health Checking

### 3.1 Health Check Service

```python
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProxyHealth:
    host: str
    port: int
    is_alive: bool
    latency_ms: Optional[float]
    last_checked: float

class ProxyHealthChecker:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.test_urls = [
            'http://httpbin.org/ip',
            'https://api.ipify.org?format=json'
        ]
    
    async def check_proxy(self, proxy: ProxyConfig) -> ProxyHealth:
        start_time = time.time()
        
        try:
            connector = aiohttp.ProxyConnector.from_url(
                f"{proxy.proxy_type}://{proxy.host}:{proxy.port}"
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    self.test_urls[0], 
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    latency = (time.time() - start_time) * 1000
                    
                    return ProxyHealth(
                        host=proxy.host,
                        port=proxy.port,
                        is_alive=response.status == 200,
                        latency_ms=latency,
                        last_checked=time.time()
                    )
        except Exception as e:
            return ProxyHealth(
                host=proxy.host,
                port=proxy.port,
                is_alive=False,
                latency_ms=None,
                last_checked=time.time()
            )
    
    async def check_all_proxies(self, proxies: list) -> list:
        tasks = [self.check_proxy(p) for p in proxies]
        return await asyncio.gather(*tasks)
```

### 3.2 Continuous Health Monitoring

```python
import threading
import schedule

class ProxyHealthMonitor:
    def __init__(self, proxy_manager: 'ProxyManager', check_interval: int = 60):
        self.proxy_manager = proxy_manager
        self.check_interval = check_interval
        self.running = False
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_schedule)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        self.running = False
    
    def _run_schedule(self):
        schedule.every(self.check_interval).seconds.do(self._check_all_proxies)
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _check_all_proxies(self):
        proxies = self.proxy_manager.get_all_proxies()
        checker = ProxyHealthChecker()
        
        results = asyncio.run(checker.check_all_proxies(proxies))
        
        for health in results:
            if not health.is_alive:
                self.proxy_manager.mark_proxy_dead(health.host)
                logger.warning(f"Proxy {health.host}:{health.port} is down")
            else:
                self.proxy_manager.update_latency(health.host, health.latency_ms)
```

### 3.3 C# Implementation

```csharp
public class ProxyHealthChecker
{
    private readonly int _timeoutMs;
    private readonly string[] _testUrls = { "http://httpbin.org/ip" };

    public ProxyHealthChecker(int timeoutMs = 10000)
    {
        _timeoutMs = timeoutMs;
    }

    public async Task<ProxyHealth> CheckProxyAsync(ProxyConfig proxy)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        
        try
        {
            var handler = new HttpClientHandler
            {
                Proxy = proxy.ToWebProxy(),
                UseProxy = true
            };

            using var client = new HttpClient(handler)
            {
                client.Timeout = TimeSpan.FromMilliseconds(_timeoutMs);
                
                var response = await client.GetAsync(_testUrls[0]);
                sw.Stop();

                return new ProxyHealth
                {
                    Host = proxy.Host,
                    Port = proxy.Port,
                    IsAlive = response.IsSuccessStatusCode,
                    LatencyMs = sw.ElapsedMilliseconds,
                    LastChecked = DateTime.UtcNow
                };
            }
        }
        catch
        {
            sw.Stop();
            return new ProxyHealth
            {
                Host = proxy.Host,
                Port = proxy.Port,
                IsAlive = false,
                LatencyMs = null,
                LastChecked = DateTime.UtcNow
            };
        }
    }
}
```

## 4. Proxy Manager API

### 4.1 REST API Endpoints

```
# Get all proxies
GET /api/v1/proxies

# Add new proxy
POST /api/v1/proxies
{
    "type": "socks5",
    "host": "192.168.1.1",
    "port": 1080,
    "username": "user",
    "password": "pass"
}

# Update proxy
PUT /api/v1/proxies/{id}

# Delete proxy
DELETE /api/v1/proxies/{id}

# Test proxy
POST /api/v1/proxies/{id}/test

# Get proxy health status
GET /api/v1/proxies/health
```

### 4.2 Python API Implementation

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
proxy_manager = ProxyManager()

@app.route('/api/v1/proxies', methods=['GET'])
def get_proxies():
    proxies = proxy_manager.list_proxies()
    return jsonify([p.to_dict() for p in proxies])

@app.route('/api/v1/proxies', methods=['POST'])
def add_proxy():
    data = request.json
    proxy = ProxyConfig(
        proxy_type=data['type'],
        host=data['host'],
        port=data['port'],
        username=data.get('username'),
        password=data.get('password')
    )
    proxy_id = proxy_manager.add_proxy(proxy)
    return jsonify({"id": proxy_id}), 201

@app.route('/api/v1/proxies/<proxy_id>/test', methods=['POST'])
async def test_proxy(proxy_id):
    proxy = proxy_manager.get_proxy(proxy_id)
    checker = ProxyHealthChecker()
    health = await checker.check_proxy(proxy)
    return jsonify(health.__dict__)

@app.route('/api/v1/proxies/<proxy_id>', methods=['DELETE'])
def delete_proxy(proxy_id):
    proxy_manager.delete_proxy(proxy_id)
    return '', 204
```

## 5. Best Practices

### 5.1 Proxy Usage Guidelines

- **Don't overuse single proxy**: Rotate after 50-100 requests
- **Monitor response times**: Switch proxy if latency > 3000ms
- **Handle 407 errors**: Proxy authentication failed, update credentials
- **Use residential proxies**: For sensitive operations
- **Implement retry logic**: With different proxy on failure

### 5.2 Security Considerations

```python
# Never store proxy passwords in plain text
class SecureProxyStorage:
    def __init__(self, encryption_key: bytes):
        self.key = encryption_key
    
    def encrypt_password(self, password: str) -> str:
        cipher = Fernet(self.key)
        return cipher.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted: str) -> str:
        cipher = Fernet(self.key)
        return cipher.decrypt(encrypted.encode()).decode()
```
