"""Replay helper for the tests: the DOM records of a saved snapshot, read the way the in-page extraction reads the live DOM.

DRAFT (operation OP-PREP-E09). sut01_catalog.DOM_RECORDS_JS reads the live page; this module reads a saved DOM snapshot
(page.content() output, kept as dom-snapshot.html in every bundle) with the same selector and fields, so that the ground-truth
decision can be replayed from the evidence. Standard library only.
"""
from html.parser import HTMLParser

PREFIX = 'pizza-name-'


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.records = []
        self._open = []

    def handle_starttag(self, tag, attrs):
        if tag != 'h2':
            return
        a = dict(attrs)
        testid = a.get('data-testid') or ''
        if testid.startswith(PREFIX):
            self._open.append({'data_testid': testid, 'text': '', 'aria_label': a.get('aria-label'),
                               'aria_labelledby': a.get('aria-labelledby'), 'title': a.get('title')})
        else:
            self._open.append(None)

    def handle_endtag(self, tag):
        if tag == 'h2' and self._open:
            rec = self._open.pop()
            if rec is not None:
                self.records.append(rec)

    def handle_data(self, data):
        for rec in self._open:
            if rec is not None:
                rec['text'] += data


def dom_records(html_text):
    """One record per h2 whose data-testid starts with pizza-name-, in document order (the selector of sut01_catalog)."""
    parser = _Collector()
    parser.feed(html_text)
    parser.close()
    return parser.records
