"""E05 expected values and projections of SUT-01 (API-01, API-02, API-04, API-05). DRAFT (operation OP-PREP-E05).

The expected values are computed from the pinned source before any run (executor/expected-sut01.json, derived statically by
executor/tools/derive_sut01_expected.py from backend/constants.py at commit 9ca37674d374e9303912e259641ee86baf3aabe1, whose sha256 is
the one recorded in manifests/source-reads-v1.yaml) with the arithmetic of backend/database.py (calculate_order_total, _convert_price,
round_currency_amount) transcribed as read in manifests/source-reads-v3.yaml. Nothing here is read from a run. Pure functions; no SUT is
contacted. Projections follow config s.7: identifiers, tokens and timestamps are excluded; the SUT's own response values are compared."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, '..', 'expected-sut01.json')
LOCKOUT_STATUS, LOCKOUT_DETAIL = 403, 'Sorry, this user has been locked out.'  # backend/auth.py lines 25-29, carried in the body key `error` (backend/main.py 75-84; SOURCE-READS-04, F25)
ERROR_USER_DETAIL = 'Random checkout error triggered for testing purposes'  # backend/routers/checkout.py line 71 (F03)
CHECKOUT_ITEM = {'pizza_id': 'p02', 'quantity': 1, 'size': 'small', 'toppings': []}
CHECKOUT_BODY = {'country_code': 'MX', 'items': [CHECKOUT_ITEM], 'name': 'E05 Tester', 'address': 'Calle Uno 123', 'phone': '5512345678',
                 'colonia': 'Centro', 'propina': 0}
ORDER_NUMBERS = ('subtotal', 'delivery_fee', 'tax_rate', 'tip_percentage', 'tax', 'tip', 'total', 'currency')


def load(path=None):
    with open(path or DATA_FILE, encoding='utf-8') as f:
        return json.load(f)


def round_currency_amount(amount, decimal_places):
    return float(round(amount)) if decimal_places == 0 else round(amount, decimal_places)


def convert_price(base, rate, decimal_places):
    converted = base * rate
    return round(converted) if decimal_places == 0 else round(converted, decimal_places)


def expected_catalog(data=None):
    """Market MX, language en (the catalog route's default when X-Language is absent): name, description, price, currency per item."""
    d = data or load()
    mx = d['market_MX']
    rate = d['currency_rates'][mx['currency']]
    return [{'id': p['id'], 'name': p['name']['en'], 'description': p['description']['en'],
             'price': convert_price(p['base_price'], rate, mx['decimal_places']), 'currency': mx['currency']} for p in d['pizzas']]


def project_catalog(body):
    """The comparable projection of a GET /api/pizzas body, or None when the body is not the catalog shape {"pizzas": [...]}."""
    pizzas = body.get('pizzas') if isinstance(body, dict) else None
    if not isinstance(pizzas, list) or not all(isinstance(p, dict) for p in pizzas):
        return None
    return [{'id': p.get('id'), 'name': p.get('name'), 'description': p.get('description'), 'price': p.get('price'), 'currency': p.get('currency')}
            for p in pizzas]


def expected_order(items, tip_percentage, data=None):
    """calculate_order_total of backend/database.py lines 308-359 for market MX."""
    d = data or load()
    mx = d['market_MX']
    by_id = {p['id']: p for p in d['pizzas']}
    rate, dp, tax_rate = d['currency_rates'][mx['currency']], mx['decimal_places'], mx['tax_rate']
    delivery_fee = round(mx['delivery_fee_usd'] * rate, dp) if dp else float(round(mx['delivery_fee_usd'] * rate))
    subtotal = 0.0
    for item in items:
        pizza = by_id.get(item['pizza_id'])
        if pizza:
            converted = pizza['base_price'] * rate
            base_price = round(converted) if dp == 0 else round(converted, dp)
            r = base_price / pizza['base_price'] if pizza['base_price'] > 0 else 1
            size_add = math.ceil(d['size_upcharge_usd'].get(str(item.get('size', 'small')).lower(), 0) * r)
            topping_add = math.ceil(d['topping_upcharge_usd'] * r) * len(item.get('toppings') or [])
            subtotal += (base_price + size_add + topping_add) * item['quantity']
    subtotal = round_currency_amount(subtotal, dp)
    tax = round_currency_amount(subtotal * tax_rate, dp)
    tip = round_currency_amount(subtotal * (tip_percentage / 100), dp)
    total = round_currency_amount(subtotal + delivery_fee + tax + tip, dp)
    return {'subtotal': subtotal, 'delivery_fee': round_currency_amount(delivery_fee, dp), 'tax_rate': tax_rate,
            'tip_percentage': round(tip_percentage, 2), 'tax': tax, 'tip': tip, 'total': total, 'currency': mx['currency'],
            'items': [{'pizza_id': i['pizza_id'], 'quantity': i['quantity'], 'size': i.get('size', 'small'), 'toppings': i.get('toppings') or []}
                      for i in items]}


def expected_checkout(data=None):
    return expected_order(CHECKOUT_BODY['items'], float(CHECKOUT_BODY['propina'] or 0.0), data)


def project_order(body):
    """Order identifiers, timestamps, status text and currency symbol are excluded; None when the body is not an order object."""
    if not isinstance(body, dict) or 'total' not in body:
        return None
    out = {k: body.get(k) for k in ORDER_NUMBERS}
    out['items'] = [{'pizza_id': i.get('pizza_id'), 'quantity': i.get('quantity'), 'size': i.get('size'), 'toppings': i.get('toppings')}
                    for i in (body.get('items') or []) if isinstance(i, dict)]
    return out


def a11y_mode(body, data=None):
    """The a11y_glitch mode that one GET /api/pizzas body (language en) realizes, decided from the pinned catalog: 'missing_name' (every name is
    empty), 'extreme_text' (every name and description is the English text repeated 15 times), 'wrong_lang' (every name and description is a
    translation of its own pizza, and at least one name differs from the English one), or None (the body is none of them, including a
    wrong_lang draw whose every name happens to equal the English one: such a draw cannot be told from the standard catalog)."""
    d = data or load()
    pizzas = body.get('pizzas') if isinstance(body, dict) else None
    if not isinstance(pizzas, list) or not pizzas:
        return None
    ref = {p['id']: p for p in d['pizzas']}
    if any(not isinstance(p, dict) or p.get('id') not in ref for p in pizzas):
        return None
    names, descs = [p.get('name') for p in pizzas], [p.get('description') for p in pizzas]
    if all(n == '' for n in names):
        return 'missing_name'
    en_n = [ref[p['id']]['name']['en'] for p in pizzas]
    en_d = [ref[p['id']]['description']['en'] for p in pizzas]
    if all(n == ' '.join([e] * 15) for n, e in zip(names, en_n)) and all(x == ' '.join([e] * 15) for x, e in zip(descs, en_d)):
        return 'extreme_text'
    in_langs = all(n in {v for v in ref[p['id']]['name'].values()} for n, p in zip(names, pizzas)) and \
        all(x in {v for v in ref[p['id']]['description'].values()} for x, p in zip(descs, pizzas))
    if in_langs and any(n != e for n, e in zip(names, en_n)):
        return 'wrong_lang'
    return None
