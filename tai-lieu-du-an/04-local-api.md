# 04 — Local API Specification

> **Phiên bản**: 1.2 | **Ngày**: 2026-02-18 | **Trạng thái**: Review  
> **EPIC tương ứng**: C2 + API layer

---

## 1. Tổng quan

Local API là HTTP server chạy trên `127.0.0.1:{port}` (mặc định `40000`).  
Mọi client (CLI, GUI, backend ngoài) đều giao tiếp qua API này.

> **Tham chiếu MoreLogin**: Local API tại `127.0.0.1:40000` — "requests must originate from the same machine". Dự án này áp dụng cùng nguyên tắc: bind localhost only, yêu cầu token auth.

> **API Mode**: BrowserManager hỗ trợ hai envelope mode — **Native** (default) và **MoreLogin-compat** (opt-in). Xem §3.2 bên dưới. Tham chiếu quyết định kiến trúc: `01-kien-truc-he-thong.md` §2.7 ADR-007.

---

## 2. Authentication

### 2.1 Bearer Token

Mọi request (trừ `GET /health`) phải có header:

```
Authorization: Bearer {token}
```

- Token được sinh khi cài đặt lần đầu (32+ ký tự random URL-safe base64).
- Lưu dưới dạng SHA-256 hash trong DB `settings` key `api_token_hash`.
- Token plain-text chỉ hiển thị 1 lần khi tạo, sau đó không thể retrieval.
- Rotate token: `POST /api/agent/token/rotate` → sinh token mới, invalidate cũ.

### 2.2 Error responses

Authentication errors follow the same compat envelope as all other errors:

```json
// 401 Unauthorized (missing token)
{
  "code": -1501,
  "msg": "Unauthorized: missing token",
  "data": null,
  "requestId": "req-abc123"
}

// 401 Unauthorized (invalid token)
{
  "code": -1502,
  "msg": "Unauthorized: invalid token",
  "data": null,
  "requestId": "req-abc123"
}

// 403 Forbidden
{
  "code": -1504,
  "msg": "Forbidden: insufficient permissions",
  "data": null,
  "requestId": "req-abc123"
}
```

> **Lưu ý**: 401 và 403 dùng cùng compat envelope `{code, msg, data, requestId}` với negative codes — giống mọi error khác, để backend/CLI/GUI thống nhất parsing. Xem `error-catalog.md` §8 để biết đầy đủ các codes.

### 2.3 Rate limiting

- Max 100 requests/giây từ localhost (chống accidental loop).
- Nếu vượt: `429 Too Many Requests`.

---

## 3. Request / Response Format

### 3.1 Headers chuẩn

```
Content-Type: application/json
Accept: application/json
X-Request-ID: {uuid}  ← tuỳ chọn; agent sinh nếu không có
```

### 3.2 Response envelope

Tất cả endpoints sử dụng **một chuẩn duy nhất** `{code, msg, data, requestId}` (SSOT: `error-catalog.md`).

```json
// Success
{
  "code": 0,
  "msg": "success",
  "data": { ... },
  "requestId": "req-abc123"
}

// Error
{
  "code": -1601,
  "msg": "Profile name is required",
  "data": null,
  "requestId": "req-abc123"
}
```

| Code | Nghĩa | HTTP |
|---|---|---|
| `0` | Thành công | 200 |
| `-1601` — `-1607` | Validation error | 400 |
| `-1501` — `-1503` | Unauthorized | 401 |
| `-1504` | Forbidden | 403 |
| `-1001`, `-1101`, `-1201`, `-1301`, `-1401` | Not found | 404 |
| `-1002`, `-1005`, `-1102`, `-1202`, `-1302` | Conflict | 409 |
| `-1003`, `-1004`, `-1007`, `-1010`, `-1103`, `-1204`, `-1304`, `-1402`, `-1403`, `-1407` | Unprocessable Entity | 422 |
| `-1505` | Too many requests | 429 |
| `-1701`, `-1705` | Internal server error | 500 |
| `-1801` — `-1802` | Not implemented | 501 |
| `-1006`, `-1305`, `-1404`, `-1405`, `-1702`, `-1703` | Service unavailable | 503 |

> **SSOT for error codes**: See `error-catalog.md` for the complete list. All `code` values are negative integers (0 = success; < 0 = error).

> **Lưu ý endpoint độc lập với envelope**: Compat endpoints `/api/env/*` có thể dùng cả hai envelope mode. Xem §4A bên dưới.

### 3.3 HTTP Status codes

| Code | Nghĩa |
|---|---|
| `200` | OK |
| `201` | Created |
| `204` | No Content (DELETE thành công) |
| `400` | Bad Request (validation error) |
| `401` | Unauthorized (thiếu/sai token) |
| `404` | Not Found |
| `409` | Conflict (duplicate name, running session) |
| `429` | Too Many Requests |
| `500` | Internal Server Error |

---

## 4. OpenAPI Specification (YAML)

```yaml
openapi: "3.1.0"
info:
  title: BrowserManager Local API
  version: "1.0.0"
  description: |
    Local API for BrowserManager Agent.
    Runs on 127.0.0.1 (localhost only). Requires Bearer token.

servers:
  - url: "http://127.0.0.1:40000"
    description: Local Agent

components:
  securitySchemes:
    BearerToken:
      type: http
      scheme: bearer
      bearerFormat: Token

  schemas:
    ProfileCreate:
      type: object
      required: [name]
      properties:
        name:
          type: string
          maxLength: 100
        group_name:
          type: string
        tags:
          type: array
          items:
            type: string
        start_url:
          type: string
          format: uri
        extensions:
          type: array
          items:
            type: string
        headless_default:
          type: boolean
          default: false
        proxy:
          $ref: "#/components/schemas/ProxyConfig"

    ProxyConfig:
      type: object
      required: [type, host, port]
      properties:
        type:
          type: string
          enum: [http, https, socks5, ssh]
        host:
          type: string
        port:
          type: integer
          minimum: 1
          maximum: 65535
        username:
          type: string
        password:
          type: string
          description: Will be encrypted before storage

    Profile:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        group_name:
          type: string
        tags:
          type: array
          items:
            type: string
        status:
          type: string
          enum: [inactive, active, error]
        start_url:
          type: string
        extensions:
          type: array
          items:
            type: string
        data_dir:
          type: string
        proxy_id:
          type: string
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    Session:
      type: object
      properties:
        id:
          type: string
          format: uuid
        profile_id:
          type: string
        status:
          type: string
          enum: [launching, running, stopped, crashed]
        pid:
          type: integer
        debug_port:
          type: integer
        headless:
          type: boolean
        started_at:
          type: string
          format: date-time
        stopped_at:
          type: string
          format: date-time

    Job:
      type: object
      properties:
        id:
          type: string
          format: uuid
        type:
          type: string
        profile_id:
          type: string
        session_id:
          type: string
        status:
          type: string
          enum: [queued, running, completed, failed, cancelled]
        result:
          type: object
        error_msg:
          type: string
        created_at:
          type: string
          format: date-time
        started_at:
          type: string
          format: date-time
        completed_at:
          type: string
          format: date-time

    AgentStatus:
      type: object
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        version:
          type: string
        uptime_seconds:
          type: integer
        sessions:
          type: object
          properties:
            active:
              type: integer
            max:
              type: integer
        jobs:
          type: object
          properties:
            queued:
              type: integer
            running:
              type: integer

    WebhookCreate:
      type: object
      required: [url, events]
      properties:
        url:
          type: string
          format: uri
          description: HTTPS URL only; localhost/internal IPs are rejected
        events:
          type: array
          items:
            type: string
            enum: [job.completed, job.failed, job.cancelled, session.started, session.stopped, session.crashed, profile.created, profile.deleted]
        secret:
          type: string
          description: HMAC-SHA256 signing secret (optional but recommended)

    Webhook:
      type: object
      properties:
        id:
          type: string
          format: uuid
        url:
          type: string
        events:
          type: array
          items:
            type: string
        active:
          type: boolean
        created_at:
          type: string
          format: date-time
        last_triggered_at:
          type: string
          format: date-time
        failure_count:
          type: integer

    ExtensionCreate:
      type: object
      required: [source]
      properties:
        source:
          type: string
          description: Chrome Web Store URL or CRX file path
        name:
          type: string
          description: Human-readable name (auto-detected from store if omitted)

    Extension:
      type: object
      properties:
        id:
          type: string
          format: uuid
        ext_id:
          type: string
          description: Chrome extension ID (e.g., from Web Store)
        name:
          type: string
        version:
          type: string
        source_url:
          type: string
        assigned_profiles:
          type: integer
          description: Number of profiles this extension is assigned to
        verified:
          type: boolean
          description: Signature verified from Chrome Web Store
        created_at:
          type: string
          format: date-time

    ScriptCreate:
      type: object
      required: [id, name, entry_file]
      properties:
        id:
          type: string
          description: Unique script identifier (e.g., "health-check")
        name:
          type: string
          description: Human-readable display name
        description:
          type: string
        entry_file:
          type: string
          description: Relative path to main.js within the script directory
        version:
          type: string
          default: "1.0.0"
        params_schema:
          type: object
          description: JSON Schema for expected params (optional)

    Script:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        version:
          type: string
        entry_file:
          type: string
        params_schema:
          type: object
        registered_at:
          type: string
          format: date-time
        last_run_at:
          type: string
          format: date-time
          nullable: true

security:
  - BearerToken: []

paths:
  /health:
    get:
      summary: Healthcheck
      security: []
      responses:
        "200":
          description: Agent is running
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/AgentStatus"

  /api/agent/status:
    get:
      summary: Agent status with metrics
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/AgentStatus"

  /api/agent/token/rotate:
    post:
      summary: Rotate API token
      responses:
        "200":
          description: New token (shown once only)
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                  message:
                    type: string

  /api/profiles:
    get:
      summary: List profiles
      parameters:
        - name: group
          in: query
          schema:
            type: string
        - name: tag
          in: query
          schema:
            type: string
        - name: q
          in: query
          description: Search by name
          schema:
            type: string
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        "200":
          description: List of profiles
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/Profile"
                  total:
                    type: integer
                  page:
                    type: integer

    post:
      summary: Create profile
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ProfileCreate"
      responses:
        "201":
          description: Profile created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Profile"
        "400":
          description: Validation error
        "409":
          description: Name already exists

  /api/profiles/{id}:
    get:
      summary: Get profile by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Profile
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Profile"
        "404":
          description: Not found

    patch:
      summary: Update profile
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ProfileCreate"
      responses:
        "200":
          description: Updated profile
        "409":
          description: Profile has active session

    delete:
      summary: Delete profile
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "204":
          description: Deleted
        "409":
          description: Profile has active session

  /api/profiles/{id}/clone:
    post:
      summary: Clone profile
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                mode:
                  type: string
                  enum: [metadata_only, full_copy]
                  default: metadata_only
      responses:
        "201":
          description: Cloned profile

  /api/profiles/{id}/export:
    get:
      summary: Export profile as ZIP
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
        - name: exclude_secrets
          in: query
          schema:
            type: boolean
            default: true
        - name: include_data_dir
          in: query
          schema:
            type: boolean
            default: false
      responses:
        "200":
          description: ZIP file
          content:
            application/zip:
              schema:
                type: string
                format: binary

  /api/profiles/{id}/clear-cache:
    post:
      summary: Clear cache data for a profile
      description: Profile must not have an active session. Clears selected cache types from user-data-dir.
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [types]
              properties:
                types:
                  type: array
                  items:
                    type: string
                    enum: [cookies, local_storage, indexeddb, extension_data, all]
                  minItems: 1
      responses:
        "200":
          description: Cache cleared successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  cleared:
                    type: array
                    items:
                      type: string
                  bytes_freed:
                    type: integer
                  cleared_at:
                    type: string
                    format: date-time
        "409":
          description: Profile has active session

  /api/profiles/trash:
    get:
      summary: List profiles in recycle bin
      responses:
        "200":
          description: Trashed profiles with restore deadline
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      allOf:
                        - $ref: "#/components/schemas/Profile"
                        - type: object
                          properties:
                            deleted_at:
                              type: string
                              format: date-time
                            restore_deadline:
                              type: string
                              format: date-time

  /api/profiles/{id}/restore:
    post:
      summary: Restore profile from recycle bin (within 7 days)
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Profile restored
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Profile"
        "404":
          description: Profile not found in trash or restore deadline passed

  /api/profiles/{id}/permanent:
    delete:
      summary: Permanently delete profile (bypasses trash, irrecoverable)
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "204":
          description: Permanently deleted
        "409":
          description: Profile has active session

  /api/profiles/batch:
    post:
      summary: Batch update multiple profiles
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [profile_ids, operations]
              properties:
                profile_ids:
                  type: array
                  items:
                    type: string
                  minItems: 1
                operations:
                  type: array
                  items:
                    type: object
                    required: [op, value]
                    properties:
                      op:
                        type: string
                        enum: [set_group, set_proxy, add_tag, remove_tag, set_start_url]
                      value:
                        type: string
      responses:
        "200":
          description: Batch result
          content:
            application/json:
              schema:
                type: object
                properties:
                  total:
                    type: integer
                  updated:
                    type: integer
                  failed:
                    type: integer
                  errors:
                    type: array
                    items:
                      type: object

  /api/extensions:
    get:
      summary: List all extensions in central registry
      responses:
        "200":
          description: List of extensions
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/Extension"
    post:
      summary: Add extension to central registry
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ExtensionCreate"
      responses:
        "201":
          description: Extension added

  /api/extensions/{id}:
    delete:
      summary: Remove extension from registry
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "204":
          description: Removed

  /api/extensions/{id}/assign:
    post:
      summary: Assign or remove extension for multiple profiles
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [profile_ids, action]
              properties:
                profile_ids:
                  type: array
                  items:
                    type: string
                action:
                  type: string
                  enum: [add, remove]
      responses:
        "200":
          description: Assignment result

  /api/profiles/import:
    post:
      summary: Import profile from ZIP
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        "201":
          description: Imported profile

  /api/proxies:
    get:
      summary: List proxies
      responses:
        "200":
          description: List of proxies
    post:
      summary: Add proxy
      responses:
        "201":
          description: Proxy added

  /api/proxies/{id}:
    get:
      summary: Get proxy detail
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Proxy detail
        "404":
          description: Proxy not found
    patch:
      summary: Update proxy config
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                label:
                  type: string
                host:
                  type: string
                port:
                  type: integer
                username:
                  type: string
                password:
                  type: string
                  description: Will be encrypted before storage
                refresh_url:
                  type: string
      responses:
        "200":
          description: Updated proxy
        "404":
          description: Proxy not found
    delete:
      summary: Delete proxy
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "204":
          description: Proxy deleted
        "404":
          description: Proxy not found

  /api/proxies/{id}/test:
    post:
      summary: Test proxy connectivity
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Test result
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [ok, error]
                  ip:
                    type: string
                  latency_ms:
                    type: integer
                  reason:
                    type: string

  /api/sessions/start:
    post:
      summary: Launch browser session for a profile
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [profile_id]
              properties:
                profile_id:
                  type: string
                headless:
                  type: boolean
                  default: false
      responses:
        "200":
          description: Session started
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Session"
        "409":
          description: Max concurrent sessions reached

  /api/sessions/{id}/stop:
    post:
      summary: Stop session
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Session stopped

  /api/sessions:
    get:
      summary: List active sessions
      responses:
        "200":
          description: List of sessions

  /api/sessions/close-all:
    post:
      summary: Stop all currently running sessions
      responses:
        "200":
          description: All sessions stopped
          content:
            application/json:
              schema:
                type: object
                properties:
                  stopped_count:
                    type: integer
                  errors:
                    type: array
                    items:
                      type: object

  /api/sessions/debug-info:
    get:
      summary: Get CDP debug port info for all running sessions
      description: Returns a consolidated list of all active sessions with their debug ports for connecting via CDP.
      responses:
        "200":
          description: Debug info for all running sessions
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      type: object
                      properties:
                        session_id:
                          type: string
                        profile_id:
                          type: string
                        profile_name:
                          type: string
                        pid:
                          type: integer
                        debug_port:
                          type: integer
                        cdp_url:
                          type: string
                          example: "http://127.0.0.1:9222"
                        started_at:
                          type: string
                          format: date-time

  /api/jobs:
    get:
      summary: List jobs
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [queued, running, completed, failed, cancelled]
        - name: profile_id
          in: query
          schema:
            type: string
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        "200":
          description: List of jobs

  /api/jobs/{id}:
    get:
      summary: Get job detail
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Job detail with logs
          content:
            application/json:
              schema:
                allOf:
                  - $ref: "#/components/schemas/Job"
                  - type: object
                    properties:
                      logs:
                        type: array
                        items:
                          type: object

  /api/jobs/{id}/cancel:
    post:
      summary: Cancel a queued or running job
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Job cancelled

  /api/webhooks:
    get:
      summary: List configured webhooks
      responses:
        "200":
          description: List of webhooks
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: "#/components/schemas/Webhook"
    post:
      summary: Register a webhook
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/WebhookCreate"
      responses:
        "201":
          description: Webhook registered
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Webhook"
        "400":
          description: Invalid URL or events

  /api/webhooks/{id}:
    delete:
      summary: Remove a webhook
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "204":
          description: Webhook removed
    patch:
      summary: Update webhook (enable/disable, change events)
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                events:
                  type: array
                  items:
                    type: string
                active:
                  type: boolean
      responses:
        "200":
          description: Updated webhook

  /api/scripts/run:
    post:
      summary: Run automation script
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [script_id, profile_id]
              properties:
                script_id:
                  type: string
                profile_id:
                  type: string
                params:
                  type: object
                timeout_sec:
                  type: integer
                  default: 120
      responses:
        "200":
          description: Job created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Job"

  /api/scripts:
    get:
      summary: List all registered scripts
      responses:
        "200":
          description: List of scripts
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Script"
    post:
      summary: Register a new script
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ScriptCreate"
      responses:
        "201":
          description: Script registered
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Script"
        "409":
          description: Script ID already exists

  /api/scripts/{id}:
    get:
      summary: Get script detail
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Script detail
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Script"
        "404":
          description: Script not found
    delete:
      summary: Remove script from registry
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "204":
          description: Script removed
        "404":
          description: Script not found

  /api/jobs/{id}/artifacts:
    get:
      summary: Get artifacts (screenshots, logs) from a job
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: List of artifact files
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    type:
                      type: string
                      enum: [screenshot, log, json]
                    size_bytes:
                      type: integer
                    download_url:
                      type: string
        "404":
          description: Job not found
```

---

## 4A. MoreLogin-Compat Endpoints

> Các endpoint này là **alias** 1-1 sang native endpoints. Mục đích: code đang dùng MoreLogin API có thể chuyển sang BrowserManager mà không cần sửa client.
> Kích hoạt bằng `compatibility.enabled: true` trong `appsettings.json` (mặc định `false`). Xem [`15-config-keys-reference.md`](15-config-keys-reference.md) để biết chi tiết.
> Tham chiếu đầy đủ: [`13-baseline-morelogin-public.md`](13-baseline-morelogin-public.md).

### 4A.1 Env (Profile) Endpoints

| Method | Path | Alias → Native | Mô tả |
|---|---|---|---|
| `POST` | `/api/env/create/quick` | → `POST /api/profiles` | Tạo profile nhanh (fields tối thiểu) |
| `POST` | `/api/env/create/advanced` | → `POST /api/profiles` | Tạo profile đầy đủ (tất cả fields) |
| `POST` | `/api/env/update` | → `PATCH /api/profiles/{id}` | Cập nhật profile |
| `POST` | `/api/env/detail` | → `GET /api/profiles/{id}` | Chi tiết profile |
| `POST` | `/api/env/removeToRecycleBin/batch` | → `DELETE /api/profiles` (batch soft-delete) | Chuyển profiles vào Trash (soft delete) |
| `POST` | `/api/env/list` | → `GET /api/profiles` | Danh sách profiles |
| `POST` | `/api/env/page` | → `GET /api/profiles` (paginated) | Danh sách có phân trang + filter |
| `POST` | `/api/env/start` | → `POST /api/sessions/start` | Mở browser |
| `POST` | `/api/env/close` | → `POST /api/sessions/{id}/stop` | Đóng browser |
| `POST` | `/api/env/closeAll` | → `POST /api/sessions/close-all` | Đóng tất cả |
| `POST` | `/api/env/active` | → `PUT /api/sessions/{id}/focus` hoặc `GET /api/sessions` | Focus cửa sổ hoặc danh sách đang chạy (xem §4A.1a) |
| `POST` | `/api/env/reopen` | → `POST /api/sessions/start` (with restart semantics) | Mở lại (restart) session đã đóng |
| `POST` | `/api/env/removeLocalCache` | → `POST /api/profiles/{id}/clear-cache` | Xóa cache local |
| `POST` | `/api/env/cache/cleanCloud` | N/A (501) | Xóa cloud cache — **không hỗ trợ** |
| `POST` | `/api/env/getAllScreen` | Native (không có alias) | Thông tin màn hình (POST, body `{}`) |
| `POST` | `/api/env/arrangeWindows` | Native (không có alias) | Sắp xếp cửa sổ |
| `POST` | `/api/env/getAllProcessIds` | → `POST /api/sessions/debug-info` | PID tất cả session |
| `POST` | `/api/env/getAllDebugInfo` | → `POST /api/sessions/debug-info` | CDP debug info tất cả session |

#### §4A.1a POST /api/env/active — Window Focus Behavior

Endpoint này có **hai chế độ** tùy thuộc vào body request:

**Chế độ 1 — Không có `id` (liệt kê sessions đang chạy):**
```json
// Request: không có body hoặc body rỗng
POST /api/env/active

// Response
{
  "code": 0,
  "msg": "success",
  "data": [
    { "id": "uuid1", "name": "Profile A", "debugPort": 9222, "startTime": "2026-02-18T10:00:00Z" },
    { "id": "uuid2", "name": "Profile B", "debugPort": 9223, "startTime": "2026-02-18T10:05:00Z" }
  ],
  "requestId": "req-abc123"
}
```

**Chế độ 2 — Có `id` (đưa cửa sổ lên foreground):**
```json
// Request
{
  "id": "uuid-of-session"
}

// Response
{
  "code": 0,
  "msg": "success",
  "data": { "focused": true, "id": "uuid-of-session" },
  "requestId": "req-abc123"
}
```

**Behavior chi tiết (window focus):**
- Agent gọi Windows API `SetForegroundWindow(hWnd)` trên cửa sổ Chromium của session.
- Nếu cửa sổ đang bị minimize: trước tiên gọi `ShowWindow(hWnd, SW_RESTORE)`, sau đó `SetForegroundWindow`.
- Nếu session không tìm thấy hoặc không đang chạy: trả `404 Not Found`.
- Nếu compat mode tắt: trả `404 Not Found` với message "Compat mode disabled".
- Native equivalent: `PUT /api/sessions/{id}/focus` (gọi nội bộ tương tự).

> **Lưu ý Windows**: `SetForegroundWindow` yêu cầu process đang foreground hoặc có `FOREGROUND_LOCK_TIMEOUT` hợp lệ. Agent dùng `AllowSetForegroundWindow(pid)` để đảm bảo permission.

#### POST /api/env/page

Paginated profile list với filter nâng cao (compat MoreLogin).

// Response (native envelope)
{
  "data": {
    "list": [
      {
        "id": "uuid",
        "name": "Profile 1",
        "groupId": "uuid",
        "groupName": "Marketing",
        "remark": "VN account for campaign",
        "status": 1,
        "createdAt": "2026-02-18T10:30:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "pageSize": 20
  },
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

Field mapping giữa compat và native:

| Compat field | Native field | Ghi chú |
|---|---|---|
| `envName` | `q` (name search) | Search by name |
| `groupId` | `group_id` | FK group |
| `tagId` | `tag_id` | FK tag |
| `status` | `status` | `0`=inactive, `1`=active, `2`=error |
| `pageSize` | `page_size` | Size per page |

#### POST /api/env/start

Mở browser session (compat alias). Trả về thêm `debugPort`, `webdriver`, `browserVersion` theo MoreLogin baseline.

```json
// Request
{
  "envId": "uuid",
  "openWidth": 1280,
  "openHeight": 800
}

// Response
{
  "data": {
    "envId": "uuid",
    "http": "http://127.0.0.1:9222",
    "ws": "ws://127.0.0.1:9222/devtools/browser/xxx",
    "debugPort": 9222,
    "webdriver": "C:\\BrowserManager\\bin\\chromedriver.exe",
    "browserVersion": "120.0.6099.130"
  },
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

> **Lưu ý E2E**: Nếu profile có `e2e_encryption_enabled = true`, request phải kèm `encryptKey`. Nếu thiếu → `400 Bad Request`.
> Xem chi tiết: [`09-bao-mat-va-luu-tru.md`](09-bao-mat-va-luu-tru.md) §8C.

#### POST /api/env/cache/cleanCloud

Endpoint này **không được hỗ trợ** trong self-hosted mode. BrowserManager trả về HTTP 501:

```json
// HTTP 501 Not Implemented
{
  "code": -1501,
  "msg": "Cloud cache not supported in self-hosted mode",
  "data": {
    "alternative": "POST /api/env/removeLocalCache",
    "docs": "https://github.com/lizamazieva41-ai/bower/blob/main/tai-lieu-du-an/scope-exceptions.md"
  },
  "requestId": "req-abc123"
}
```

**Lý do**: BrowserManager là self-hosted architecture — không có cloud storage backend.  
**Giải pháp thay thế**: Sử dụng `POST /api/env/removeLocalCache` để xóa cache local.

#### POST /api/env/getAllScreen

Traả về danh sách màn hình vật lý trên máy. Body có thể rỗng `{}`.

```json
// Response
{
  "data": [
    {
      "id": 0,
      "isPrimary": true,
      "width": 1920,
      "height": 1080,
      "x": 0,
      "y": 0,
      "scaleFactor": 1.0
    }
  ],
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

#### POST /api/env/arrangeWindows

Sắp xếp tự động các cửa sổ browser đang chạy.

```json
// Request
{
  "envIds": ["uuid1", "uuid2"],
  "cols": 3,
  "screenId": 0,
  "width": 600,
  "height": 400
}

// Response
{
  "data": { "arranged": 2 },
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

#### POST /api/env/reopen

Đóng session đang chạy (nếu có) rồi mở lại — alias restart.

```json
// Request
{
  "id": "uuid-of-profile",
  "openWidth": 1280,
  "openHeight": 800
}

// Response
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "uuid-of-profile",
    "status": 1,
    "debugPort": 9222,
    "webdriver": "http://127.0.0.1:9222",
    "version": "Chrome/120.0.6099.109"
  },
  "requestId": "req-abc123"
}
```

Semantics: nếu session đang chạy, agent gọi `POST /api/sessions/{id}/stop` trước, sau đó `POST /api/sessions/start`. Kết quả trả về giống `/api/env/start`. Xem `openapi.yaml` cho full schema.

---

### 4A.2 Group (EnvGroup) Endpoints

| Method | Path | Mô tả |
|---|---|---|
| `POST` | `/api/envgroup/page` | Danh sách groups có phân trang |
| `POST` | `/api/envgroup/create` | Tạo group mới |
| `POST` | `/api/envgroup/edit` | Sửa group |
| `POST` | `/api/envgroup/delete` | Xoá group |

#### POST /api/envgroup/page

```json
// Request
{ "page": 1, "pageSize": 20, "groupName": "Marketing" }

// Response
{
  "data": {
    "list": [
      { "groupId": "uuid", "groupName": "Marketing", "envCount": 15, "createdAt": "2026-02-18T10:00:00Z" }
    ],
    "total": 3
  },
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

#### POST /api/envgroup/create

```json
// Request
{ "groupName": "Marketing Team" }

// Response
{
  "data": { "groupId": "uuid", "groupName": "Marketing Team" },
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

#### POST /api/envgroup/edit

```json
// Request
{ "groupId": "uuid", "groupName": "Marketing Team V2" }

// Response: 200 OK, data: updated group object
```

#### POST /api/envgroup/delete

```json
// Request
{ "groupIds": ["uuid1", "uuid2"] }

// Response: 200 OK, data: { "deleted": 2 }
// Profiles trong group bị xoá sẽ được chuyển về groupId = null (Ungrouped)
```

---

### 4A.3 Tag (EnvTag) Endpoints

| Method | Path | Mô tả |
|---|---|---|
| `GET` | `/api/envtag/all` | Lấy tất cả tags |
| `POST` | `/api/envtag/create` | Tạo tag mới |
| `POST` | `/api/envtag/edit` | Sửa tag |
| `POST` | `/api/envtag/delete` | Xoá tag |

#### GET /api/envtag/all

```json
// Response
{
  "data": [
    { "tagId": "uuid", "tagName": "VIP", "color": "#FF5733", "envCount": 5 }
  ],
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

#### POST /api/envtag/create

```json
// Request
{ "tagName": "VIP", "color": "#FF5733" }

// Response
{
  "data": { "tagId": "uuid", "tagName": "VIP", "color": "#FF5733" },
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

#### POST /api/envtag/edit

```json
// Request
{ "tagId": "uuid", "tagName": "VIP Customer", "color": "#C0392B" }
// Response: 200 OK, data: updated tag object
```

#### POST /api/envtag/delete

```json
// Request
{ "tagIds": ["uuid1"] }
// Response: 200 OK, data: { "deleted": 1 }
// Profile-tag links bị xoá tự động (CASCADE)
```

---

### 4A.4 ProxyInfo (Compat) Endpoints

| Method | Path | Alias → Native | Mô tả |
|---|---|---|---|
| `POST` | `/api/proxyInfo/page` | → `GET /api/proxies` | Danh sách proxy có phân trang |
| `POST` | `/api/proxyInfo/add` | → `POST /api/proxies` | Thêm proxy mới |
| `POST` | `/api/proxyInfo/update` | → `PATCH /api/proxies/{id}` | Cập nhật proxy |
| `POST` | `/api/proxyInfo/delete` | → `DELETE /api/proxies/{id}` | Xóa proxy |

#### POST /api/proxyInfo/page

```json
// Request
{ "page": 1, "pageSize": 20, "proxyType": "socks5", "label": "VN Proxy" }

// Response
{
  "data": {
    "list": [
      {
        "proxyId": "uuid",
        "proxyType": "socks5",
        "proxyHost": "proxy.example.com",
        "proxyPort": 1080,
        "proxyUser": "user1",
        "label": "VN Proxy 01",
        "profileCount": 3
      }
    ],
    "total": 10
  },
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

#### POST /api/proxyInfo/add

Thêm proxy mới (alias → `POST /api/proxies`).

```json
// Request
{
  "label": "US SOCKS5 #1",
  "type": "socks5",
  "host": "proxy.example.com",
  "port": 1080,
  "username": "user",
  "password": "pass",
  "refreshUrl": "https://api.provider.com/rotate"
}

// Response
{
  "code": 0,
  "msg": "success",
  "data": { "id": "uuid-of-new-proxy" },
  "requestId": "req-abc123"
}
```

#### POST /api/proxyInfo/delete

Xóa proxy (alias → `DELETE /api/proxies/{id}`).

```json
// Request
{ "id": "uuid-of-proxy" }

// Response
{
  "code": 0,
  "msg": "success",
  "data": null,
  "requestId": "req-abc123"
}
```

---

### 4A.5 Xử lý version gap

Mỗi endpoint trong `openapi.yaml` có extension `x-min-agent-version`. Client nên kiểm tra version trước khi gọi:

```bash
# Kiểm tra version agent
curl http://127.0.0.1:40000/health
# Response: { "version": "1.2.0", ... }
```

Nếu agent version thấp hơn `x-min-agent-version` của endpoint → trả `501 Not Implemented` với message gợi ý nâng cấp.

---

## 5. Webhook / Callback (tuỳ chọn)

### 5.1 Cấu hình webhook

```json
POST /api/webhooks
{
  "url": "https://your-backend.com/callback",
  "events": ["job.completed", "job.failed", "session.crashed"],
  "secret": "hmac_secret_for_signature"
}
```

### 5.2 Payload webhook

```json
{
  "event": "job.completed",
  "timestamp": "2026-02-18T10:30:00Z",
  "data": {
    "job_id": "uuid",
    "type": "run_script",
    "profile_id": "uuid",
    "status": "completed",
    "result": { ... }
  }
}
```

Header gửi kèm:
```
X-BM-Event: job.completed
X-BM-Signature: sha256={hmac_hex}
X-BM-Timestamp: 1708254600
```

Receiver phải verify signature: `HMAC-SHA256(secret, payload_body)`.

### 5.3 Retry policy

- Retry tối đa 3 lần nếu receiver trả `non-2xx`.
- Backoff: 5s, 30s, 120s.
- Sau 3 lần fail → đánh dấu webhook `inactive`, log warn.

---

## 6. SSE Log Stream

### Endpoint: `GET /api/logs/stream`

Dùng **Server-Sent Events (SSE)**:

```
GET /api/logs/stream?job_id={id}&level=INFO
Accept: text/event-stream
Authorization: Bearer {token}
```

Response format:
```
data: {"timestamp":"2026-02-18T10:30:00Z","level":"INFO","job_id":"uuid","message":"Script started"}

data: {"timestamp":"2026-02-18T10:30:01Z","level":"INFO","job_id":"uuid","message":"Navigating to https://example.com"}

data: {"timestamp":"2026-02-18T10:30:05Z","level":"INFO","job_id":"uuid","message":"Script completed","result":{"status":"ok"}}

event: close
data: {}
```

Parameters:
- `job_id` — filter theo job (optional)
- `level` — min level: `DEBUG|INFO|WARN|ERROR` (default: `INFO`)
- `tail` — số dòng history khi bắt đầu subscribe (default: `50`)

---

## 7. Definition of Done (DoD) — Local API

- [ ] Tất cả endpoints trong OpenAPI spec hoạt động đúng.
- [ ] `GET /health` trả `200` không cần auth.
- [ ] Request không có token → `401` chính xác.
- [ ] Rate limit: >100 req/s → `429`.
- [ ] Log masking: `Authorization` header không xuất hiện trong logs.
- [ ] Webhook: gửi đúng event + HMAC signature verifiable.
- [ ] SSE stream: client nhận log realtime, độ trễ < 1s.
- [ ] Postman collection / integration test bao phủ mọi endpoint.

---

*Tài liệu tiếp theo: [05-cli-spec.md](05-cli-spec.md)*
