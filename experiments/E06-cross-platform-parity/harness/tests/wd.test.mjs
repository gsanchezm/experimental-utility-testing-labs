// Tests of the WebDriver client of harness/wd.mjs: the two commands added for E06 (findElements, sendKeys) and the transport error.
// DRAFT (operation OP-PREP-E06-EXECUTOR). Uses the fake server of tests/fake_appium.mjs; no device.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createClient, WebDriverError } from '../wd.mjs';
import { startFakeAppium } from './fake_appium.mjs';

test('findElements returns the element references of every match, and an empty list when nothing matches', async () => {
  const server = await startFakeAppium({ sut: 'SUT-02' });
  try {
    const client = createClient(server.url);
    await client.newSession({ platformName: 'Android' }, 10000);
    const ids = await client.findElements('id', 'com.saucelabs.mydemoapp.android:id/titleTV');
    assert.equal(ids.length, 2);
    const none = await client.findElements('id', 'no.such:id/thing');
    assert.deepEqual(none, []);
    await client.deleteSession();
  } finally {
    await server.close();
  }
});

test('sendKeys posts the text as the W3C value array', async () => {
  const server = await startFakeAppium({ sut: 'SUT-02' });
  try {
    const client = createClient(server.url);
    await client.newSession({ platformName: 'Android' }, 10000);
    // the login field exists only on the login screen: open the drawer and the Log In row first
    await client.click(await client.findElement('id', 'com.saucelabs.mydemoapp.android:id/menuIV'));
    await client.click(await client.findElement('accessibility id', 'Login Menu Item'));
    const id = await client.findElement('id', 'com.saucelabs.mydemoapp.android:id/nameET');
    await client.sendKeys(id, 'ab');
    const sent = server.requests.find((r) => r.path.endsWith('/value'));
    assert.equal(sent.body.text, 'ab');
    assert.deepEqual(sent.body.value, ['a', 'b']);
    await client.deleteSession();
  } finally {
    await server.close();
  }
});

test('a command without a session refuses before any request', async () => {
  const client = createClient('http://127.0.0.1:9');
  await assert.rejects(() => client.findElements('id', 'x'), /without an active session/);
});

test('an unreachable server is a transport error, never a response error', async () => {
  const client = createClient('http://127.0.0.1:9', { requestTimeoutMs: 2000 });
  await assert.rejects(() => client.status(), (e) => e instanceof WebDriverError && e.kind === 'transport');
});
