# 1. THIẾT KẾ DATABASE

## Tables

### profiles
```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    fingerprint_config TEXT,
    default_proxy_id INTEGER,
    created_at TIMESTAMP,
    is_active BOOLEAN
);
```

### sessions
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER,
    status VARCHAR(50),
    started_at TIMESTAMP,
    browser_type VARCHAR(50),
    process_id INTEGER
);
```

### proxies
```sql
CREATE TABLE proxies (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    proxy_type VARCHAR(50),
    host VARCHAR(255),
    port INTEGER,
    username VARCHAR(255),
    password VARCHAR(255),
    is_active BOOLEAN
);
```

### fingerprints
```sql
CREATE TABLE fingerprints (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER,
    user_agent TEXT,
    platform VARCHAR(100),
    webgl_vendor VARCHAR(255),
    webgl_renderer VARCHAR(255)
);
```

*Document ID: ABB-V2-DOC-0601*
