// Minimal W3C WebDriver client for the Appium 3 compatibility smoke (EUS-2026-001).
// Speaks only the standard W3C endpoints Appium serves; no client library is used (the pinned stack is
// Appium 3.7.0 core plus exactly one platform driver). The transport is injectable so that the control flow can
// be checked statically without any Appium server or device.
// Every error that concerns the runner is a WebDriverError carrying its kind, recorded for the attribution of
// protocol/mobile-runner-policy-v3.md, section 9 (9.1-9.4 as carried from v2): 'response' (the runner answered
// with an error), 'transport' (no answer), 'protocol' (an answer without the required reference), 'not_reached'
// (the required element or state was not reached within the step's time limit). Any other exception is
// study-authored harness code.
// Transport (QUAL-U06; protocol/mobile-runner-policy-v3.md, 9.7.4): the default transport is Node's built-in
// node:http, so no HTTP-layer timeout exists below the explicit per-request budget (the built-in fetch applies
// its own undici header and body timeouts, which this client neither sets nor can raise without a new
// dependency). The explicit budget (requestTimeoutMs, or the timeoutMs of the call, for example the session-start
// budget of the platform realization) is therefore the only limit, and a shorter one is never imposed silently.
// A transport failure keeps the underlying error and its cause (name, code, message) in WebDriverError.transport.

import http from 'node:http';
import https from 'node:https';

const ELEMENT_KEY = 'element-6066-11e4-a52e-4f735466cecf';

export class WebDriverError extends Error {
  constructor(message, { status = null, error = null, kind = 'response', transport = null } = {}) {
    super(message);
    this.name = 'WebDriverError';
    this.status = status;
    this.w3cError = error;
    this.kind = kind;
    this.transport = transport;
  }
}

export const TRANSPORT = Object.freeze({
  kind: 'node:http',
  agent: 'one connection per request (agent: false)',
  http_layer_timeouts: 'none: no socket, header, or body timeout is set; the explicit per-request budget is the only limit',
});

const detail = (e) => (e && typeof e === 'object'
  ? { name: e.name ?? null, code: e.code ?? null, message: String(e.message ?? e).split('\n')[0] }
  : { name: null, code: null, message: String(e) });

// A minimal fetch-compatible request over node:http / node:https: resolves once the whole response body has been
// read, with ok, status, text(), and json(); rejects with the underlying error (and its cause) on any transport
// failure, including an abort through the signal.
export function nodeHttpFetch(url, { method = 'GET', headers = {}, body, signal } = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const payload = body === undefined ? null : Buffer.from(body, 'utf8');
    const req = (u.protocol === 'https:' ? https : http).request(u, {
      method,
      agent: false,
      signal,
      headers: { accept: '*/*', ...headers, ...(payload ? { 'content-length': String(payload.length) } : {}) },
    }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('error', reject);
      res.on('end', () => {
        const buf = Buffer.concat(chunks);
        resolve({
          ok: res.statusCode >= 200 && res.statusCode < 300,
          status: res.statusCode,
          text: async () => buf.toString('utf8'),
          json: async () => JSON.parse(buf.toString('utf8')),
        });
      });
    });
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

export function createClient(serverUrl, { fetchImpl = nodeHttpFetch, requestTimeoutMs = 120000, now = () => Date.now() } = {}) {
  const base = serverUrl.replace(/\/+$/, '');
  let sessionId = null;

  async function call(method, path, body, timeoutMs = requestTimeoutMs) {
    const ctrl = new AbortController();
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; ctrl.abort(); }, timeoutMs);
    const t0 = now();
    let res;
    try {
      res = await fetchImpl(base + path, {
        method,
        headers: { 'content-type': 'application/json; charset=utf-8' },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: ctrl.signal,
      });
    } catch (e) {
      const transport = { error: detail(e), cause: e && e.cause ? detail(e.cause) : null, timed_out: timedOut, timeout_ms: timeoutMs, elapsed_ms: now() - t0 };
      const tag = (d) => [d.name, d.code].filter(Boolean).join('/') || 'unnamed';
      const shown = `[error ${tag(transport.error)}${transport.cause ? `; cause ${tag(transport.cause)}: ${transport.cause.message}` : ''}; after ${transport.elapsed_ms} ms]`;
      throw new WebDriverError(`${method} ${path}: transport failure: ${timedOut ? `no response within ${timeoutMs} ms` : transport.error.message} ${shown}`, { kind: 'transport', transport });
    } finally {
      clearTimeout(timer);
    }
    let payload = null;
    try { payload = await res.json(); } catch { payload = null; }
    const value = payload && typeof payload === 'object' ? payload.value : null;
    if (!res.ok || (value && typeof value === 'object' && value.error)) {
      const err = value && value.error ? value.error : `http ${res.status}`;
      const msg = value && value.message ? String(value.message).split('\n')[0] : '';
      throw new WebDriverError(`${method} ${path}: ${err}${msg ? `: ${msg}` : ''}`, { status: res.status, error: err, kind: 'response' });
    }
    return value;
  }

  const s = () => {
    if (!sessionId) throw new Error('harness called a session command without an active session');
    return `/session/${sessionId}`;
  };
  const elementId = (value) => {
    const id = value && (value[ELEMENT_KEY] || value.ELEMENT);
    if (!id) throw new WebDriverError('the server returned no element reference', { kind: 'protocol' });
    return id;
  };

  return {
    transport: fetchImpl === nodeHttpFetch ? TRANSPORT : { kind: 'injected' },
    get sessionId() { return sessionId; },
    status: () => call('GET', '/status', undefined, 10000),
    async newSession(capabilities, timeoutMs) {
      const value = await call('POST', '/session', { capabilities: { alwaysMatch: capabilities, firstMatch: [{}] } }, timeoutMs);
      sessionId = value && value.sessionId;
      if (!sessionId) throw new WebDriverError('the server returned no session id', { kind: 'protocol' });
      return value.capabilities || {};
    },
    async deleteSession() {
      if (!sessionId) return;
      try { await call('DELETE', s(), undefined, 60000); } finally { sessionId = null; }
    },
    async findElement(using, value, fromElement = null) {
      const path = fromElement ? `${s()}/element/${fromElement}/element` : `${s()}/element`;
      return elementId(await call('POST', path, { using, value }));
    },
    click: (id) => call('POST', `${s()}/element/${id}/click`, {}),
    text: (id) => call('GET', `${s()}/element/${id}/text`),
    attribute: (id, name) => call('GET', `${s()}/element/${id}/attribute/${encodeURIComponent(name)}`),
    displayed: (id) => call('GET', `${s()}/element/${id}/displayed`),
    screenshot: () => call('GET', `${s()}/screenshot`, undefined, 120000),
    source: () => call('GET', `${s()}/source`, undefined, 120000),
  };
}

// Poll findElement until the element exists (and, if requested, a predicate on it holds) or the timeout expires.
// A WebDriverError is retried until the deadline; any other exception is a harness defect and is rethrown at once.
export async function waitFor(client, { using, value, from = null, timeoutMs, intervalMs = 1000, until = null, sleep = (ms) => new Promise((r) => setTimeout(r, ms)), now = () => Date.now() }) {
  const deadline = now() + timeoutMs;
  let last = null;
  for (;;) {
    try {
      const id = await client.findElement(using, value, from);
      if (!until || (await until(id))) return id;
      last = new WebDriverError(`condition not met for ${using} "${value}"`, { kind: 'not_reached' });
    } catch (e) {
      if (!(e instanceof WebDriverError)) throw e;
      last = e;
    }
    if (now() >= deadline) throw new WebDriverError(`not found within ${timeoutMs} ms: ${using} "${value}"${last ? ` (last: ${last.message})` : ''}`, { kind: 'not_reached' });
    await sleep(intervalMs);
  }
}
