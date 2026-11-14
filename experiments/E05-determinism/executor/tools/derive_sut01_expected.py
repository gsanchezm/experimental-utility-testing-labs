"""Derive expected-sut01.json from backend/constants.py of SUT-01 at the pinned commit (operation OP-PREP-E05). DRAFT.

Usage: python3 -I derive_sut01_expected.py <path to backend/constants.py> <output json>

The file is parsed statically (ast.literal_eval of the PIZZA_CATALOG, CURRENCY_RATES, A11Y_GLITCH_MODES and A11Y_GLITCH_LANGS literals):
no SUT code is imported or executed. The input must have the sha256 recorded in manifests/source-reads-v1.yaml (SOURCE-READS-01) for
backend/constants.py at commit 9ca37674d374e9303912e259641ee86baf3aabe1; otherwise the tool stops. The values that are not literals in the
file (the MX market configuration, whose keys are enum members) and the size and topping upcharges of backend/database.py are transcribed
below with their line numbers, as read in manifests/source-reads-v3.yaml (SOURCE-READS-03). Expected values are written before any run and
are never taken from a run."""
import ast
import hashlib
import json
import sys

PIN = {'repository': 'https://github.com/gsanchezm/OmniPizza', 'commit': '9ca37674d374e9303912e259641ee86baf3aabe1'}
CONSTANTS_SHA256 = 'f40cad1f571cb64a2a09e298abcd6c7818c2e7f4cec1dc65fc02f6c7d6065dc7'
# backend/constants.py lines 90-100 (CountryCode.MX); decimal_places is absent there, and database.py reads country_config.get("decimal_places", 2).
MX = {'currency': 'MXN', 'currency_symbol': '$', 'required_fields': ['colonia'], 'tip_field': 'propina', 'tip_percentages': [0, 5, 10, 15],
      'delivery_fee_usd': 2.0, 'tax_rate': 0.16, 'languages': ['es'], 'decimal_places': 2}
# backend/database.py lines 11-17.
SIZE_UPCHARGE_USD = {'small': 0, 'medium': 3, 'large': 4, 'family': 5}
TOPPING_UPCHARGE_USD = 1


def literal(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(f'{name} not found as a literal assignment')


def main(src_path, out_path):
    raw = open(src_path, 'rb').read()
    if hashlib.sha256(raw).hexdigest() != CONSTANTS_SHA256:
        raise SystemExit('backend/constants.py does not have the sha256 recorded in SOURCE-READS-01')
    tree = ast.parse(raw.decode('utf-8'))
    catalog, rates = literal(tree, 'PIZZA_CATALOG'), literal(tree, 'CURRENCY_RATES')
    out = {'record': 'expected values of SUT-01 derived statically from the pinned source (DRAFT, OP-PREP-E05)', 'source': PIN,
           'constants_sha256': CONSTANTS_SHA256, 'currency_rates': rates, 'market_MX': MX, 'size_upcharge_usd': SIZE_UPCHARGE_USD,
           'topping_upcharge_usd': TOPPING_UPCHARGE_USD, 'a11y_modes': literal(tree, 'A11Y_GLITCH_MODES'),
           'a11y_langs': literal(tree, 'A11Y_GLITCH_LANGS'),
           'pizzas': [{'id': p['id'], 'base_price': p['base_price'], 'name': p['name'], 'description': p['description']} for p in catalog]}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write('\n')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
