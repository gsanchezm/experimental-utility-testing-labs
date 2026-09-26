// Minimal W3C WebDriver client for the Appium 3 compatibility smoke (EUS-2026-001).
// Speaks only the standard W3C endpoints Appium serves; no client library is used (the pinned stack is
// Appium 3.7.0 core plus exactly one platform driver). The fetch implementation is injectable so that the
// control flow can be checked statically without any Appium server or device.
// Every error that concerns the runner is a WebDriverError carrying its kind, recorded for the attribution of
// protocol/mobile-runner-policy-v2.md, section 9: 'response' (the runner answered with an error), 'transport'
// (no answer), 'protocol' (an answer without the required reference), 'not_reached' (the required element or
// state was not reached within the step's time limit). Any other exception is study-authored harness code.

const ELEMENT_KEY = 'element-6066-11e4-a52e-4f735466cecf';

export class WebDriverError extends Error {
  constructor(message, { status = null, error = null, kind = 'response' } = {}) {
    super(message);
    this.name = 'WebDriverError';
    this.status = status;
    this.w3cError = error;
    this.kind = kind;
  }
}

export function createClient(serverUrl, { fetchImpl = globalThis.fetch, requestTimeoutMs = 120000 } = {}) {
  const base = serverUrl.replace(/\/+$/, '');
  let sessionId = null;

  async function call(method, path, body, timeoutMs = requestTimeoutMs) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    let res;
    try {
      res = await fetchImpl(base + path, {
        method,
        headers: { 'content-type': 'application/json; charset=utf-8' },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: ctrl.signal,
      });
    } catch (e) {
      throw new WebDriverError(`${method} ${path}: transport failure: ${e.name === 'AbortError' ? `no response within ${timeoutMs} ms` : e.message}`, { kind: 'transport' });
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
