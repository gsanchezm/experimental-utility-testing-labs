// Starts the fake WebDriver server of fake_appium.mjs as a child process for the Python tests (DRAFT, operation OP-PREP-E06-EXECUTOR).
// Prints one line "URL <base url>" on standard output and runs until its standard input closes.
// Options: --sut=SUT-01|SUT-02 --sign-in=ok|error|stay --error-text=TEXT --cards=p07,p02 --titles=A|B --fail-session=1

import { startFakeAppium } from './fake_appium.mjs';

const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split(/=(.*)/s).slice(0, 2)));
const server = await startFakeAppium({
  sut: args.sut ?? 'SUT-01',
  signIn: args['sign-in'] ?? 'ok',
  errorText: args['error-text'] ?? null,
  cards: args.cards ? args.cards.split(',') : undefined,
  titles: args.titles ? args.titles.split('|') : undefined,
  failSession: args['fail-session'] === '1',
  logout: args.logout ?? 'shown',
  sourceFailsWhenMenuOpen: args['source-fails-when-menu-open'] === '1',
});
process.stdout.write(`URL ${server.url}\n`);
process.stdin.resume();
process.stdin.on('end', async () => {
  await server.close();
  process.exit(0);
});
