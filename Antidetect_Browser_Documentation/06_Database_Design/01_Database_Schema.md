# 1. THIẾT KẾ DATABASE

## Tables

### profiles
```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    use_case VARCHAR(100),
    browser_engine VARCHAR(50) DEFAULT 'chromium',
    user_agent TEXT,
    proxy VARCHAR(500),
    proxy_username VARCHAR(255),
    proxy_password VARCHAR(255),
    resolution VARCHAR(20) DEFAULT '1920x1080',
    timezone VARCHAR(100),
    language VARCHAR(20),
    headless BOOLEAN DEFAULT 1,
    advanced_settings TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### sessions
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    browser_type VARCHAR(50),
    process_id INTEGER,
    debug_port INTEGER,
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
);
```

### proxies
```sql
CREATE TABLE proxies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    proxy_type VARCHAR(50) DEFAULT 'http',
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(255),
    password VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    health_status VARCHAR(20) DEFAULT 'unknown',
    last_checked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### fingerprints
```sql
CREATE TABLE fingerprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER,
    user_agent TEXT,
    platform VARCHAR(100),
    webgl_vendor VARCHAR(255),
    webgl_renderer VARCHAR(255),
    canvas_hash VARCHAR(255),
    audio_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
);
```

### api_keys
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    permissions VARCHAR(500) DEFAULT 'read',
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### audit_logs
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Indexes
```sql
CREATE INDEX idx_profiles_name ON profiles(name);
CREATE INDEX idx_sessions_profile_id ON sessions(profile_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_proxies_host ON proxies(host);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

## Relationships

```
users (1) ───< (N) audit_logs
profiles (1) ───< (N) sessions
profiles (1) ───< (N) fingerprints
profiles (N) ───< (1) proxies (via default_proxy_id)
```

---

*Document ID: ABB-V2-DOC-0601 v2*
