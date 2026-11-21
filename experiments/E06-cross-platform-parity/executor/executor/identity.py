"""E06-cross-platform-parity executor: pure parsers of the catalogue identity (no browser, no device, no network).

DRAFT (operation OP-PREP-E06-EXECUTOR). Each parser takes what the executor captured (the test identifiers read from the DOM, the
accessibility labels and texts read from an Appium page source) and returns the identity of the first catalogue position. The parsers
are the replayable part of the identity read: a kept page source or DOM list gives the same answer when parsed again.

Identity keys (decision D-E06-9): SUT-01 the pizza id; SUT-02 the product title of the first entry in the default ascending name order.
"""
import xml.etree.ElementTree as ET

WEB_TESTID_PREFIX = 'pizza-name-'
WEB_SUFFIXES = ('-desktop', '-responsive')
DESKTOP_BREAKPOINT_PX = 768
ANDROID_CARD_LABEL_PREFIX = 'card-pizza-'
ANDROID_TITLE_RESOURCE_ID = 'com.saucelabs.mydemoapp.android:id/titleTV'


def expected_suffix(viewport_width):
    """The suffix the SUT-01 web application appends to its test identifiers (frontend/src/hooks/useResponsive.js)."""
    return '-desktop' if viewport_width >= DESKTOP_BREAKPOINT_PX else '-responsive'


def web_pizza_id(testid):
    """(pizza id, suffix) of one SUT-01 web test identifier pizza-name-<id>[-desktop|-responsive]; (None, None) if it is not one."""
    if not isinstance(testid, str) or not testid.startswith(WEB_TESTID_PREFIX):
        return None, None
    rest = testid[len(WEB_TESTID_PREFIX):]
    suffix = next((s for s in WEB_SUFFIXES if rest.endswith(s)), None)
    core = rest[: -len(suffix)] if suffix else rest
    if not core:
        return None, None
    return core, suffix


def parse_web_testids(testids):
    """The SUT-01 web catalogue in document order: one record per pizza-name test identifier, raw and normalized."""
    out = []
    for raw in testids or []:
        pid, suffix = web_pizza_id(raw)
        if pid is not None:
            out.append({'raw': raw, 'id': pid, 'suffix': suffix})
    return out


def pizza_id_from_card_label(label):
    """The pizza id of an Android card label card-pizza-<id>, or None."""
    if not isinstance(label, str) or not label.startswith(ANDROID_CARD_LABEL_PREFIX):
        return None
    return label[len(ANDROID_CARD_LABEL_PREFIX):] or None


def parse_android_card_source(xml_text):
    """The SUT-01 Android catalogue in document order, read from a kept Appium page source (XML).

    Each element whose content-desc starts with card-pizza- is a card; the label is the raw value, the id the normalized one.
    Raises ValueError when the source is not well-formed XML (the caller records the identity as unreadable)."""
    root = _parse(xml_text)
    out = []
    for el in root.iter():
        label = el.attrib.get('content-desc')
        pid = pizza_id_from_card_label(label)
        if pid is not None:
            out.append({'raw': label, 'id': pid})
    return out


def parse_android_titles_source(xml_text):
    """The SUT-02 Android catalogue titles in document order, read from a kept Appium page source (XML): the text of every titleTV."""
    root = _parse(xml_text)
    out = []
    for el in root.iter():
        if el.attrib.get('resource-id') == ANDROID_TITLE_RESOURCE_ID:
            out.append(normalize_title(el.attrib.get('text')))
    return out


def normalize_title(text):
    """A product title with its internal white space collapsed; None for a missing or empty title."""
    if not isinstance(text, str):
        return None
    collapsed = ' '.join(text.split())
    return collapsed or None


def first_identity(sut_id, items):
    """The identity of the first catalogue position for a SUT, or None when no item was read.

    items: for SUT-01 the records of parse_web_testids or parse_android_card_source (dicts with 'id'); for SUT-02 a list of titles.
    """
    if sut_id == 'SUT-01':
        for item in items or []:
            if isinstance(item, dict) and item.get('id'):
                return item['id']
        return None
    if sut_id == 'SUT-02':
        for title in items or []:
            if title:
                return title
        return None
    raise ValueError(f'no identity key is defined for {sut_id}')


def _parse(xml_text):
    if not isinstance(xml_text, str) or not xml_text.strip():
        raise ValueError('the page source is empty')
    try:
        return ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise ValueError(f'the page source is not well-formed XML: {e}') from e
