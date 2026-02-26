# DNS Leak Protection

## 1. Understanding DNS Leaks

### 1.1 What is a DNS Leak?

A DNS leak occurs when a VPN/proxy user experiences a privacy breach where DNS queries escape the encrypted tunnel, revealing the user's browsing activity to their ISP or DNS servers.

### 1.2 How DNS Leaks Happen

```
Normal Flow (Without Protection):
┌──────────┐      DNS Query       ┌─────────────┐
│  User    │ ──────────────────▶ │ DNS Server  │
│ Browser  │                      │ (ISP)       │
└──────────┘                      └─────────────┘
      │                                  │
      │      Visible!                    │
      └──────────────────────────────────┘

Protected Flow (With VPN):
┌──────────┐      Encrypted      ┌───────────┐     ┌─────────────┐
│  User    │ ──────────────────▶│ VPN DNS   │ ──▶│ Final DNS   │
│ Browser  │      Tunnel        │ (Secure)   │     │ Server      │
└──────────┘                     └───────────┘     └─────────────┘
                                              │
                                              │ Hidden
                                              └──────────
```

### 1.3 DNS Leak Test Methods

| Method | Description | Website |
|--------|-------------|---------|
| Standard DNS | Check if DNS matches ISP | dnsleaktest.com |
| WebRTC DNS | Check WebRTC-based DNS | browserleaks.com |
| Extended DNS | Advanced leak detection | ipleak.net |

## 2. DNS Resolver Configuration

### 2.1 Secure DNS Providers

| Provider | DNS Servers | Privacy Level | Speed |
|----------|-------------|---------------|-------|
| Cloudflare | 1.1.1.1, 1.0.0.1 | High | Fast |
| Google | 8.8.8.8, 8.8.4.4 | Medium | Fast |
| Quad9 | 9.9.9.9, 149.112.112.112 | High | Medium |
| OpenDNS | 208.67.222.222 | Medium | Fast |
| NextDNS | Custom | High | Fast |

### 2.2 DNS over HTTPS Configuration

```python
import requests
import json

class SecureDNSResolver:
    """DNS over HTTPS (DoH) resolver"""
    
    def __init__(self, provider: str = 'cloudflare'):
        self.providers = {
            'cloudflare': 'https://cloudflare-dns.com/dns-query',
            'google': 'https://dns.google/resolve',
            'quad9': 'https://dns.quad9.net:5053/dns-query'
        }
        self.provider_url = self.providers.get(provider)
        self.headers = {
            'Accept': 'application/dns-json'
        }
    
    def resolve(self, domain: str, record_type: str = 'A') -> dict:
        """Resolve domain using DoH"""
        params = {
            'name': domain,
            'type': record_type
        }
        
        response = requests.get(
            self.provider_url,
            params=params,
            headers=self.headers
        )
        
        return response.json()
    
    def resolve_https(self, domain: str) -> list:
        """Resolve with HTTPS certificate validation"""
        try:
            result = self.resolve(domain)
            return [answer['data'] for answer in result.get('Answer', [])]
        except Exception as e:
            logger.error(f"DNS resolution failed: {e}")
            return []
```

### 2.3 DNS over TLS Configuration

```python
import ssl
import socket

class DoTResolver:
    """DNS over TLS (DoT) resolver"""
    
    def __init__(self, server: str = '1.1.1.1', port: int = 853):
        self.server = server
        self.port = port
    
    def create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for DoT"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_default_certs()
        return context
    
    def resolve(self, domain: str, record_type: str = 'A') -> list:
        """Resolve domain using DoT"""
        # Build DNS query
        query = self._build_dns_query(domain, record_type)
        
        # Create secure connection
        context = self.create_ssl_context()
        
        with socket.create_connection((self.server, self.port)) as sock:
            with context.wrap_socket(sock, server_hostname=self.server) as ssock:
                ssock.send(query)
                response = ssock.recv(4096)
        
        return self._parse_dns_response(response)
    
    def _build_dns_query(self, domain: str, record_type: str) -> bytes:
        # DNS query building logic
        # Simplified example
        transaction_id = b'\x00\x01'
        flags = b'\x01\x00'
        questions = b'\x00\x01'
        answer_rrs = b'\x00\x00'
        authority_rrs = b'\x00\x00'
        additional_rrs = b'\x00\x00'
        
        # Encode domain name
        encoded_domain = b''
        for part in domain.split('.'):
            encoded_domain += bytes([len(part)]) + part.encode()
        encoded_domain += b'\x00'
        
        # Record type
        type_map = {'A': b'\x00\x01', 'AAAA': b'\x00\x1c', 'MX': b'\x00\x0f'}
        qtype = type_map.get(record_type, b'\x00\x01')
        
        qclass = b'\x00\x01'
        
        return transaction_id + flags + questions + answer_rrs + \
               authority_rrs + additional_rrs + encoded_domain + qtype + qclass
```

### 2.4 C# DNS over HTTPS

```csharp
using System.Net.Http;
using System.Text.Json;

public class SecureDnsResolver
{
    private readonly HttpClient _httpClient;
    private readonly string _dohUrl;

    public SecureDnsResolver(string provider = "cloudflare")
    {
        _httpClient = new HttpClient();
        _dohUrl = provider switch
        {
            "cloudflare" => "https://cloudflare-dns.com/dns-query",
            "google" => "https://dns.google/resolve",
            "quad9" => "https://dns.quad9.net:5053/dns-query",
            _ => "https://cloudflare-dns.com/dns-query"
        };
    }

    public async Task<List<string>> ResolveAsync(string domain, string recordType = "A")
    {
        var request = new HttpRequestMessage(HttpMethod.Get, 
            $"{_dohUrl}?name={domain}&type={recordType}");
        request.Headers.Add("Accept", "application/dns-json");

        var response = await _httpClient.SendAsync(request);
        var json = await response.Content.ReadAsStringAsync();
        
        var result = JsonSerializer.Deserialize<DnsResponse>(json);
        
        return result.Answer?
            .Select(a => a.Data)
            .ToList() ?? new List<string>();
    }
}

public class DnsResponse
{
    public List<DnsAnswer> Answer { get; set; }
}

public class DnsAnswer
{
    public string Data { get; set; }
}
```

## 3. Chrome Flags for DNS Protection

### 3.1 Essential Chrome Flags

```bash
# Force DNS over HTTPS
--enable-features=SecureDnsSettingOverrides
--force-dark-mode

# Disable WebRTC IP handling
--disable-webrtc-ip-handling
--disable-peer-connection

# Disable QUIC protocol
--disable-quic

# Force legacy TLS (if needed)
--ssl-version-min=tls1.2
--ssl-version-max=tls1.3
```

### 3.2 Chrome Policy Configuration

```json
{
  "name": "DNS Over HTTPS Policy",
  "description": "Configure DNS over HTTPS for Chrome",
  "policies": {
    "DNSOverHttpsMode": {
      "DNSOverHttps": "secure",
      "Templates": "https://dns.google/dns-query{?dns}"
    },
    "QuickUnlockMinimumSeconds": {
      "Value": 0
    },
    "QuicAllowed": {
      "Value": false
    }
  }
}
```

### 3.3 Browser Startup Configuration

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_stealth_chrome_options() -> Options:
    options = webdriver.ChromeOptions()
    
    # DNS Protection
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--disable-extensions-http-throttling')
    
    # Network prediction
    options.add_argument('--disable-preconnect')
    options.add_argument('--disable-sync')
    
    # WebRTC protection
    options.add_argument('--disable-webrtc-ip-handling')
    options.add_argument('--disable-peer-connection')
    
    # Disable QUIC
    options.add_argument('--disable-quic')
    
    # Force secure DNS
    options.add_argument('--enable-features=SecureDnsSettingOverrides')
    
    return options
```

## 4. DNS Leak Prevention Implementation

### 4.1 System-Level DNS Configuration

```bash
# Linux - systemd-resolved configuration
# /etc/systemd/resolved.conf

[Resolve]
DNS=1.1.1.1 1.0.0.1
DNSOverHttps=yes
DNSSEC=yes
Cache=yes
DNSStubListener=yes

# Restart systemd-resolved
sudo systemctl restart systemd-resolved
```

```bash
# macOS - Configure DNS via scutil
# Set DNS servers
sudo scutil --set DNS 1.1.1.1 1.0.0.1

# Verify configuration
scutil --dns
```

```powershell
# Windows - PowerShell
# Set DNS via PowerShell
$adapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses ("1.1.1.1","1.0.0.1")

# Enable DoH
Set-NetAdapterDns -InterfaceIndex $adapter.ifIndex -DnsServer "1.1.1.1" -EnableDnsOverHttps -DohServer "https://cloudflare-dns.com/dns-query"
```

### 4.2 Application-Level Implementation

```python
import socket
import subprocess

class DNSLeakProtector:
    """Application-level DNS leak protection"""
    
    def __init__(self):
        self.original_getaddrinfo = socket.getaddrinfo
        self.secure_dns = ('1.1.1.1', 53)
    
    def patch_socket_for_dns_protection(self):
        """Patch socket to use secure DNS"""
        
        def secure_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            # Use secure DNS instead of system DNS
            try:
                # Create UDP socket to secure DNS
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                
                # Send DNS query
                query = self._build_dns_query(host)
                sock.sendto(query, self.secure_dns)
                
                # Receive response
                data, _ = sock.recvfrom(512)
                sock.close()
                
                # Parse response and return
                return self._parse_dns_response(data, host, port, family, type, proto)
            except Exception as e:
                logger.warning(f"Secure DNS failed, falling back: {e}")
                # Fallback to original
                return self.original_getaddrinfo(host, port, family, type, proto, flags)
        
        socket.getaddrinfo = secure_getaddrinfo
    
    def _build_dns_query(self, domain: str) -> bytes:
        # Build standard DNS query
        transaction_id = b'\x00\x01'
        flags = b'\x01\x00'
        questions = b'\x00\x01'
        
        # Encode domain
        encoded = b''
        for part in domain.split('.'):
            encoded += bytes([len(part)]) + part.encode()
        encoded += b'\x00'
        
        qtype = b'\x00\x01'  # A record
        qclass = b'\x00\x01' # IN
        
        return transaction_id + flags + questions + \
               b'\x00\x00' + b'\x00\x00' + b'\x00\x00' + \
               encoded + qtype + qclass
    
    def _parse_dns_response(self, data: bytes, host: str, port: int, 
                           family: int, type: int, proto: int):
        # Parse DNS response and return socket addresses
        # Simplified - returns IPv4 addresses
        results = []
        
        # Skip header (12 bytes)
        offset = 12
        
        # Find answer section
        while offset < len(data):
            if offset + 12 > len(data):
                break
            offset += 12  # Skip name and type/class
            
            rdlength = int.from_bytes(data[offset:offset+2], 'big')
            offset += 2
            rdata = data[offset:offset+rdlength]
            offset += rdlength
            
            if rdlength == 4:  # IPv4
                ip = '.'.join(str(b) for b in rdata)
                results.append((socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port)))
        
        return results if results else [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('0.0.0.0', port))]
```

## 5. Testing & Validation

### 5.1 DNS Leak Test Script

```python
import requests
import json

class DNSLeakTester:
    """Test for DNS leaks"""
    
    def __init__(self):
        self.test_domains = [
            'example.com',
            'google.com',
            'cloudflare.com'
        ]
    
    def test_dns_leak(self) -> dict:
        """Perform DNS leak test"""
        results = {
            'leak_detected': False,
            'dns_servers': [],
            'isp_detected': False
        }
        
        # Test each DNS server
        for domain in self.test_domains:
            # Get DNS resolution from browser
            dns_servers = self._get_dns_servers_from_browser()
            
            if dns_servers:
                results['dns_servers'].extend(dns_servers)
                
                # Check if using ISP DNS
                if self._is_isp_dns(dns_servers):
                    results['isp_detected'] = True
                    results['leak_detected'] = True
        
        results['dns_servers'] = list(set(results['dns_servers']))
        return results
    
    def _get_dns_servers_from_browser(self) -> list:
        """Get DNS servers from WebRTC"""
        # Use WebRTC to leak DNS
        # This is for testing only
        js_code = """
        async function getRTCStats() {
            const pc = new RTCPeerConnection({
                iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
            });
            
            pc.createDataChannel('');
            await pc.createOffer();
            await pc.setLocalDescription(pc.localDescription);
            
            return new Promise(resolve => {
                pc.onicecandidate = async (e) => {
                    if (e.candidate) {
                        const stats = await pc.getStats();
                        stats.forEach(report => {
                            if (report.type === 'candidate-pair' && 
                                report.state === 'succeeded') {
                                resolve([report.remoteCandidates[0]]);
                            }
                        });
                    }
                };
                setTimeout(() => resolve([]), 1000);
            });
        }
        getRTCStats();
        """
        # Execute via browser automation
        return []
    
    def _is_isp_dns(self, dns_servers: list) -> bool:
        """Check if DNS belongs to ISP"""
        isp_ranges = ['10.', '192.168.', '172.16.']
        return any(
            any(dns.startswith(r) for r in isp_ranges)
            for dns in dns_servers
        )
```

### 5.2 Prevention Checklist

```markdown
## DNS Leak Prevention Checklist

### System Level
- [ ] Configure secure DNS (1.1.1.1 or 9.9.9.9)
- [ ] Enable DNS over HTTPS
- [ ] Disable IPv6 or configure with secure DNS
- [ ] Configure firewall to block non-VPN DNS

### Browser Level
- [ ] Disable WebRTC
- [ ] Use stealth browser mode
- [ ] Configure Chrome flags for DNS protection
- [ ] Disable network prediction

### Application Level
- [ ] Implement custom DNS resolution
- [ ] Use VPN DNS for all queries
- [ ] Monitor DNS queries
- [ ] Regular leak testing
```

## 6. Best Practices

### 6.1 DNS Configuration Best Practices

1. **Use DNS over HTTPS/TLS**: Encrypt DNS queries
2. **Choose privacy-focused DNS**: Cloudflare, Quad9
3. **Configure at system level**: Affects all applications
4. **Test regularly**: Verify no leaks

### 6.2 Recommended Configuration

```yaml
# Recommended DNS Configuration
dns:
  provider: cloudflare
  servers:
    - 1.1.1.1
    - 1.0.0.1
  protocol: doh  # dns-over-https
  security:
    dnssec: true
    edns: true
  features:
    block_malware: true
    block_ads: false  # optional
```
