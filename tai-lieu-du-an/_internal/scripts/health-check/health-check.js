#!/usr/bin/env node
// health-check.js — BrowserManager Agent Health Check Script
// Usage: node health-check.js [--port 40000] [--token <token>] [--quick] [--json]
// Requires: Node.js >=18, @playwright/test

const { chromium } = require('@playwright/test');
const http = require('http');

// ─── Configuration ─────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const getArg = (flag, def) => {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] : def;
};
const hasFlag = (flag) => args.includes(flag);

const PORT = Number(getArg('--port', process.env.BM_PORT || '40000'));
const TOKEN = getArg('--token', process.env.BM_TOKEN || '');
const QUICK = hasFlag('--quick');
const JSON_OUTPUT = hasFlag('--json');
const TIMEOUT = Number(getArg('--timeout', process.env.BM_TIMEOUT || '30000'));
const BASE_URL = `http://127.0.0.1:${PORT}`;

// ─── Helpers ────────────────────────────────────────────────────────────────────
let passed = 0;
let failed = 0;
const results = [];

function log(msg) {
  if (!JSON_OUTPUT) console.log(msg);
}

async function fetchApi(path, opts = {}) {
  const url = `${BASE_URL}${path}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT);
  try {
    const res = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(opts.auth !== false && TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}),
      },
      ...opts,
    });
    return { status: res.status, body: await res.json().catch(() => ({})) };
  } finally {
    clearTimeout(timer);
  }
}

async function check(name, fn) {
  const start = Date.now();
  try {
    await fn();
    const ms = Date.now() - start;
    passed++;
    results.push({ name, status: 'PASS', ms });
    log(`[${passed + failed}/${QUICK ? 3 : 7}] ${name.padEnd(25, '.')} ✅ PASS (${ms}ms)`);
  } catch (err) {
    const ms = Date.now() - start;
    failed++;
    results.push({ name, status: 'FAIL', ms, error: err.message });
    log(`[${passed + failed}/${QUICK ? 3 : 7}] ${name.padEnd(25, '.')} ❌ FAIL (${ms}ms) — ${err.message}`);
  }
}

// ─── Checks ────────────────────────────────────────────────────────────────────
async function checkHealth() {
  const { status, body } = await fetchApi('/health', { auth: false });
  if (status !== 200) throw new Error(`HTTP ${status}`);
  if (body.status !== 'healthy') throw new Error(`status = ${body.status}`);
}

async function checkAuthToken() {
  if (!TOKEN) throw new Error('No token provided (set BM_TOKEN or use --token)');
  const { status } = await fetchApi('/api/agent/status');
  if (status !== 200) throw new Error(`HTTP ${status}`);
}

async function checkAuthRejection() {
  const { status } = await fetchApi('/api/agent/status', { auth: false });
  if (status !== 401) throw new Error(`Expected 401, got HTTP ${status}`);
}

let testProfileId = null;

async function checkCreateProfile() {
  const { status, body } = await fetchApi('/api/profiles', {
    method: 'POST',
    body: JSON.stringify({ name: `__health_check_${Date.now()}` }),
  });
  if (status !== 201) throw new Error(`HTTP ${status}: ${JSON.stringify(body)}`);
  testProfileId = body.data?.id || body.id;
  if (!testProfileId) throw new Error('No profile id in response');
}

let testSessionId = null;
let testDebugPort = null;

async function checkLaunchSession() {
  const { status, body } = await fetchApi('/api/sessions/start', {
    method: 'POST',
    body: JSON.stringify({ profile_id: testProfileId, headless: true }),
  });
  if (status !== 200) throw new Error(`HTTP ${status}: ${JSON.stringify(body)}`);
  const session = body.data || body;
  testSessionId = session.id;
  testDebugPort = session.debug_port;
  if (!testDebugPort) throw new Error('No debug_port in session response');
}

async function checkCDPConnect() {
  if (!testDebugPort) throw new Error('No debug_port available (launch session first)');
  const browser = await chromium.connectOverCDP(`http://127.0.0.1:${testDebugPort}`, {
    timeout: TIMEOUT,
  });
  const contexts = browser.contexts();
  await browser.close();
  if (!contexts) throw new Error('Could not get browser contexts');
}

async function checkStopSession() {
  if (!testSessionId) throw new Error('No session id available');
  const { status } = await fetchApi(`/api/sessions/${testSessionId}/stop`, { method: 'POST' });
  if (status !== 200) throw new Error(`HTTP ${status}`);
  // Cleanup: delete test profile
  if (testProfileId) {
    await fetchApi(`/api/profiles/${testProfileId}`, { method: 'DELETE' }).catch(() => {});
  }
}

// ─── Main ───────────────────────────────────────────────────────────────────────
(async () => {
  const startAll = Date.now();

  if (!JSON_OUTPUT) {
    console.log(`\nBrowserManager Health Check v1.0.0`);
    console.log(`Agent URL: ${BASE_URL}`);
    console.log(`─────────────────────────────────────────`);
  }

  await check('Agent health', checkHealth);
  await check('Auth token', checkAuthToken);
  await check('Auth rejection', checkAuthRejection);

  if (!QUICK) {
    await check('Create test profile', checkCreateProfile);
    await check('Launch session', checkLaunchSession);
    await check('CDP connect', checkCDPConnect);
    await check('Stop session', checkStopSession);
  }

  const totalMs = Date.now() - startAll;
  const totalChecks = passed + failed;

  if (JSON_OUTPUT) {
    console.log(JSON.stringify({
      agent: BASE_URL,
      total: totalChecks,
      passed,
      failed,
      duration_ms: totalMs,
      results,
    }, null, 2));
  } else {
    console.log(`─────────────────────────────────────────`);
    if (failed === 0) {
      console.log(`Result: ${totalChecks}/${totalChecks} PASSED ✅`);
    } else {
      console.log(`Result: ${passed}/${totalChecks} PASSED ❌ (${failed} failed)`);
    }
    console.log(`Duration: ${(totalMs / 1000).toFixed(2)}s\n`);
  }

  // Cleanup on error exit
  if (testProfileId && failed > 0) {
    await fetchApi(`/api/profiles/${testProfileId}`, { method: 'DELETE' }).catch(() => {});
  }

  process.exit(failed === 0 ? 0 : results[0]?.error?.includes('No token') ? 3 : 1);
})();
