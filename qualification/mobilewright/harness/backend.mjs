// qualification/mobilewright/harness/backend.mjs
// Harness-side interactions with the qualification SUT's hosted backend. These run OUTSIDE the runner
// under qualification (protocol/mobile-runner-policy-v1.md, section 5: "The API seed step of MQ3 is
// performed outside the runner"). Only the documented session-scoped interactions of a documented test
// account are used (manifests/mobile-qualification-package-v1.yaml, backend_for_mq3_seed). A failure
// here is attributed SUT_INSTANCE or API_SEED, never RUNNER (policy section 7.3). Nothing here is
// evidence about the SUT. Record class: QUALIFICATION (or DEVELOPMENT for local harness development).

export const BACKEND_ORIGIN = process.env.GATE_BACKEND_ORIGIN || 'https://omnipizza-backend.onrender.com';
export const ACCOUNT = { username: 'standard_user', password: 'pizza123' }; // documented test account (SUT README, "Test Users")
export const MARKET = 'US';

const JWT = /eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}/g;

export function redact(value) {
  if (typeof value === 'string') return value.replace(JWT, (m) => m.slice(0, 12) + '<redacted-token>');
  if (Array.isArray(value)) return value.map(redact);
  if (value && typeof value === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(value)) out[k] = k === 'access_token' ? redact(String(v)) : redact(v);
    return out;
  }
  return value;
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

async function call(method, path, { body, headers = {}, timeoutMs = 60000 } = {}) {
  const t0 = Date.now();
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(BACKEND_ORIGIN + path, {
      method,
      headers: { 'Content-Type': 'application/json', ...headers },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: ctrl.signal,
    });
    const text = await res.text();
    let json = null;
    try { json = JSON.parse(text); } catch { /* non-JSON body */ }
    return { ok: res.ok, status: res.status, latency_ms: Date.now() - t0, body: json ?? text.slice(0, 500) };
  } catch (err) {
    return { ok: false, status: null, latency_ms: Date.now() - t0, error: String((err && err.message) || err) };
  } finally {
    clearTimeout(timer);
  }
}

/** GET /health with bounded retries. The hosted backend may be cold (observed 32 s first response). */
export async function healthCheck({ attempts = 6, timeoutMs = 45000, pauseMs = 5000 } = {}) {
  const log = [];
  for (let i = 1; i <= attempts; i++) {
    const r = await call('GET', '/health', { timeoutMs });
    log.push({ attempt: i, at: new Date().toISOString(), ...r });
    if (r.ok && r.body && r.body.status === 'healthy') return { healthy: true, attempts: log };
    if (i < attempts) await sleep(pauseMs);
  }
  return { healthy: false, attempts: log };
}

/** POST /api/auth/login with the documented test account. Returns the token (kept out of records). */
export async function login() {
  const r = await call('POST', '/api/auth/login', { body: ACCOUNT });
  const token = r.ok && r.body && r.body.access_token ? r.body.access_token : null;
  return { ok: !!token, token, response: redact({ status: r.status, latency_ms: r.latency_ms, body: r.body, error: r.error }) };
}

function authHeaders(token, withMarket) {
  const h = { Authorization: 'Bearer ' + token };
  if (withMarket) { h['X-Country-Code'] = MARKET; h['X-Language'] = 'en'; }
  return h;
}

/** GET /api/pizzas snapshot (names, prices) for anchoring the pre-declared oracles. Read-only. */
export async function catalogSnapshot(token) {
  const r = await call('GET', '/api/pizzas', { headers: authHeaders(token, true) });
  const pizzas = r.ok && r.body && Array.isArray(r.body.pizzas) ? r.body.pizzas : null;
  return {
    ok: !!pizzas,
    status: r.status,
    latency_ms: r.latency_ms,
    market: MARKET,
    currency: r.body && r.body.currency,
    pizzas: pizzas ? pizzas.map((p) => ({ id: p.id, name: p.name, price: p.price, base_price: p.base_price, currency: p.currency, currency_symbol: p.currency_symbol, category: p.category })) : null,
    error: r.error,
  };
}

/**
 * MQ3 seed: POST /api/cart replaces the account's server-side cart with `item`, then GET /api/cart
 * (market header required) verifies the seeded state. Both request and responses are recorded
 * (token redacted). `verified` is true only when the enriched cart holds exactly the seeded line.
 */
export async function seedCart(token, item) {
  const seed = await call('POST', '/api/cart', { body: { items: [item] }, headers: authHeaders(token, false) });
  const read = seed.ok ? await call('GET', '/api/cart', { headers: authHeaders(token, true) }) : null;
  const items = read && read.ok && read.body && Array.isArray(read.body.cart_items) ? read.body.cart_items : [];
  const line = items.length === 1 ? items[0] : null;
  const verified = !!line && line.pizza_id === item.pizza_id && Number(line.quantity) === Number(item.quantity) && String(line.size).toLowerCase() === String(item.size).toLowerCase();
  return {
    seeded: seed.ok,
    verified,
    request: { method: 'POST', path: '/api/cart', body: { items: [item] } },
    seed_response: redact({ status: seed.status, latency_ms: seed.latency_ms, body: seed.body, error: seed.error }),
    verify_request: { method: 'GET', path: '/api/cart', headers: { 'X-Country-Code': MARKET, 'X-Language': 'en' } },
    verify_response: read ? redact({ status: read.status, latency_ms: read.latency_ms, body: read.body, error: read.error }) : null,
    enriched_line: line,
  };
}

/** Re-read the cart (attribution artifact after an MQ3 failure). */
export async function readCart(token) {
  const r = await call('GET', '/api/cart', { headers: authHeaders(token, true) });
  return redact({ status: r.status, latency_ms: r.latency_ms, body: r.body, error: r.error });
}

/** POST /api/session/reset: documented session-reset endpoint; leaves the shared test account's cart empty. */
export async function resetSession(token) {
  const r = await call('POST', '/api/session/reset', { headers: authHeaders(token, false) });
  return redact({ status: r.status, latency_ms: r.latency_ms, body: r.body, error: r.error });
}
