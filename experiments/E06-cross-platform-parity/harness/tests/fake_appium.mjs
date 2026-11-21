// A fake W3C WebDriver server for the Android harness tests (DRAFT, operation OP-PREP-E06-EXECUTOR). It models the login and catalogue
// screens of the two SUTs closely enough to run the harness flows end to end; it is not an emulator and says nothing about the apps.

import http from 'node:http';

const ELEMENT_KEY = 'element-6066-11e4-a52e-4f735466cecf';
const PKG = 'com.saucelabs.mydemoapp.android:id/';

export function startFakeAppium({ sut, signIn = 'ok', errorText = null, cards = ['p07', 'p02'], titles = ['Sauce Labs Backpack', 'Sauce Labs Bike Light'], failSession = false } = {}) {
  const requests = [];
  const st = { screen: sut === 'SUT-01' ? 'login' : 'landing', menuOpen: false, error: null, typed: {}, session: null, ids: new Map(), next: 1 };

  function elementsNow() {
    if (sut === 'SUT-01') {
      if (st.screen === 'catalog') {
        return [{ desc: 'screen-catalog' }, ...cards.map((id) => ({ desc: `card-pizza-${id}`, rid: `card-pizza-${id}` }))];
      }
      const list = [{ desc: 'screen-login' }, { desc: 'Standard' }, { desc: 'Sign In' }];
      if (st.error) list.push({ rid: 'text-login-error', desc: st.error });
      return list;
    }
    if (st.screen === 'login') {
      const list = [{ rid: `${PKG}nameET`, text: st.typed.name ?? '' }, { rid: `${PKG}passwordET`, text: st.typed.password ?? '' }, { rid: `${PKG}loginBtn` }];
      if (st.error) list.push({ rid: `${PKG}nameErrorTV`, text: st.error });
      return list;
    }
    const list = [{ rid: `${PKG}productRV` }, { rid: `${PKG}menuIV`, desc: 'tap to view menu' }, ...titles.map((t) => ({ rid: `${PKG}titleTV`, text: t }))];
    if (st.menuOpen) list.push({ desc: 'Login Menu Item' });
    return list;
  }

  function matches(el, using, value) {
    if (using === 'accessibility id') return el.desc === value;
    if (using === 'id') return el.rid === value;
    if (using === '-android uiautomator') {
      if (value.includes('descriptionStartsWith("')) {
        const prefix = value.split('descriptionStartsWith("')[1].split('"')[0];
        return typeof el.desc === 'string' && el.desc.startsWith(prefix);
      }
      if (value.includes('resourceIdMatches')) return typeof el.rid === 'string' && /text-login-error/.test(el.rid);
      if (value.includes('new UiScrollable')) return el.desc === 'Login Menu Item';
    }
    return false;
  }

  function register(el) {
    const id = `el-${st.next++}`;
    st.ids.set(id, el);
    return id;
  }

  function act(id, action) {
    const el = st.ids.get(id);
    if (!el) return;
    if (sut === 'SUT-01') {
      if (el.desc === 'Sign In') {
        if (signIn === 'ok') st.screen = 'catalog';
        else if (signIn === 'error') { st.error = errorText; st.screen = 'login'; }
      }
      return;
    }
    if (el.rid === `${PKG}menuIV`) st.menuOpen = true;
    if (el.desc === 'Login Menu Item') { st.menuOpen = false; st.screen = 'login'; }
    if (el.rid === `${PKG}loginBtn`) {
      if (signIn === 'ok') { st.screen = 'landing'; st.error = null; }
      else if (signIn === 'error') st.error = 'Username is required';
    }
    void action;
  }

  function source() {
    const nodes = elementsNow().map((el) => `  <android.view.View content-desc="${el.desc ?? ''}" resource-id="${el.rid ?? ''}" text="${el.text ?? ''}"/>`);
    return `<?xml version="1.0" encoding="UTF-8"?>\n<hierarchy>\n${nodes.join('\n')}\n</hierarchy>\n`;
  }

  const server = http.createServer((req, res) => {
    let body = '';
    req.on('data', (c) => { body += c; });
    req.on('end', () => {
      const json = body ? JSON.parse(body) : {};
      const path = req.url.replace(/\?.*$/, '');
      requests.push({ method: req.method, path, body: json });
      const send = (status, value) => { res.writeHead(status, { 'content-type': 'application/json' }); res.end(JSON.stringify({ value })); };
      const fail = (status, error, message) => send(status, { error, message });
      const sid = st.session;

      if (req.method === 'GET' && path === '/status') return send(200, { ready: true });
      if (req.method === 'POST' && path === '/session') {
        if (failSession) return fail(500, 'session not created', 'simulated session failure');
        st.session = 'fake-session';
        st.screen = sut === 'SUT-01' ? 'login' : 'landing';
        st.error = null;
        st.menuOpen = false;
        st.typed = {};
        return send(200, { sessionId: st.session, capabilities: { platformName: 'Android', 'appium:deviceApiLevel': 35, 'appium:appPackage': json.capabilities?.alwaysMatch?.['appium:appPackage'] } });
      }
      if (req.method === 'DELETE' && path === `/session/${sid}`) { st.session = null; return send(200, null); }
      if (!sid || !path.startsWith(`/session/${sid}`)) return fail(404, 'invalid session id', 'no active session');
      const rest = path.slice(`/session/${sid}`.length);
      if (req.method === 'POST' && (rest === '/element' || rest === '/elements')) {
        const found = elementsNow().filter((el) => matches(el, json.using, json.value));
        if (rest === '/elements') return send(200, found.map((el) => ({ [ELEMENT_KEY]: register(el) })));
        if (!found.length) return fail(404, 'no such element', `no element for ${json.using} "${json.value}"`);
        return send(200, { [ELEMENT_KEY]: register(found[0]) });
      }
      let m = rest.match(/^\/element\/([^/]+)\/(click|value|displayed|attribute\/([^/]+)|text)$/);
      if (m) {
        const [, id, op, attr] = m;
        const el = st.ids.get(id);
        if (!el) return fail(404, 'stale element reference', 'element is gone');
        if (req.method === 'POST' && op === 'click') { act(id, 'click'); return send(200, null); }
        if (req.method === 'POST' && op === 'value') {
          const text = json.text ?? '';
          if (el.rid === `${PKG}nameET`) st.typed.name = text;
          if (el.rid === `${PKG}passwordET`) st.typed.password = text;
          return send(200, null);
        }
        if (req.method === 'GET' && op === 'displayed') return send(200, true);
        if (req.method === 'GET' && attr) return send(200, attr === 'content-desc' ? (el.desc ?? null) : attr === 'resource-id' ? (el.rid ?? null) : null);
        if (req.method === 'GET' && op === 'text') return send(200, el.text ?? '');
      }
      if (req.method === 'GET' && rest === '/source') return send(200, source());
      if (req.method === 'GET' && rest === '/screenshot') return send(200, Buffer.from('fake-png').toString('base64'));
      return fail(404, 'unknown command', `${req.method} ${path}`);
    });
  });

  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      resolve({ url: `http://127.0.0.1:${port}`, requests, close: () => new Promise((r) => server.close(() => r())) });
    });
  });
}
