"""Unit tests of executor/identity.py: the replayable identity read of the first catalogue position (pure; no browser, no device).

DRAFT (operation OP-PREP-E06-EXECUTOR). The Android fixtures are shaped like an Appium page source (XML with content-desc, resource-id,
and text attributes); they are fictitious, not captured from a device.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))

from executor import identity as I  # noqa: E402

CARDS_SOURCE = """<?xml version="1.0" encoding="UTF-8"?>
<hierarchy>
  <android.widget.ScrollView content-desc="screen-catalog">
    <android.view.View content-desc="card-pizza-p07" resource-id="card-pizza-p07">
      <android.widget.TextView content-desc="Pizza Margherita" resource-id="text-pizza-name-p07" text="Pizza Margherita"/>
    </android.view.View>
    <android.view.View content-desc="card-pizza-p02" resource-id="card-pizza-p02">
      <android.widget.TextView content-desc="Pepperoni" resource-id="text-pizza-name-p02" text="Pepperoni"/>
    </android.view.View>
    <android.view.View content-desc="Something else"/>
  </android.widget.ScrollView>
</hierarchy>
"""

TITLES_SOURCE = """<?xml version="1.0" encoding="UTF-8"?>
<hierarchy>
  <android.widget.TextView resource-id="com.saucelabs.mydemoapp.android:id/titleTV" text="Sauce Labs Backpack"/>
  <android.widget.TextView resource-id="com.saucelabs.mydemoapp.android:id/priceTV" text="$29.99"/>
  <android.widget.TextView resource-id="com.saucelabs.mydemoapp.android:id/titleTV" text="  Sauce   Labs  Bike Light "/>
</hierarchy>
"""


class WebIdentityTests(unittest.TestCase):
    def test_the_suffix_follows_the_breakpoint(self):
        self.assertEqual(I.expected_suffix(1280), '-desktop')
        self.assertEqual(I.expected_suffix(768), '-desktop')
        self.assertEqual(I.expected_suffix(767), '-responsive')

    def test_either_suffix_is_stripped_and_the_raw_value_is_kept_by_the_parser(self):
        self.assertEqual(I.web_pizza_id('pizza-name-p02-desktop'), ('p02', '-desktop'))
        self.assertEqual(I.web_pizza_id('pizza-name-p02-responsive'), ('p02', '-responsive'))
        self.assertEqual(I.web_pizza_id('pizza-name-p02'), ('p02', None))

    def test_other_identifiers_are_not_pizza_names(self):
        self.assertEqual(I.web_pizza_id('pizza-desc-p02-desktop'), (None, None))
        self.assertEqual(I.web_pizza_id('pizza-name--desktop'), (None, None))
        self.assertEqual(I.web_pizza_id(None), (None, None))

    def test_parse_keeps_document_order_and_both_forms(self):
        records = I.parse_web_testids(['pizza-name-p07-desktop', 'pizza-price-p07-desktop', 'pizza-name-p02-desktop'])
        self.assertEqual([r['id'] for r in records], ['p07', 'p02'])
        self.assertEqual(records[0]['raw'], 'pizza-name-p07-desktop')

    def test_first_identity_of_sut01_is_the_first_pizza_id(self):
        self.assertEqual(I.first_identity('SUT-01', I.parse_web_testids(['pizza-name-p07-desktop', 'pizza-name-p02-desktop'])), 'p07')
        self.assertIsNone(I.first_identity('SUT-01', []))


class AndroidIdentityTests(unittest.TestCase):
    def test_card_labels_are_read_in_document_order_and_normalized(self):
        records = I.parse_android_card_source(CARDS_SOURCE)
        self.assertEqual([r['id'] for r in records], ['p07', 'p02'])
        self.assertEqual(records[0]['raw'], 'card-pizza-p07')

    def test_a_source_without_cards_gives_no_identity(self):
        records = I.parse_android_card_source('<hierarchy><node content-desc="screen-catalog"/></hierarchy>')
        self.assertEqual(records, [])
        self.assertIsNone(I.first_identity('SUT-01', records))

    def test_titles_are_the_texts_of_the_title_resource_only_in_document_order(self):
        titles = I.parse_android_titles_source(TITLES_SOURCE)
        self.assertEqual(titles, ['Sauce Labs Backpack', 'Sauce Labs Bike Light'])
        self.assertEqual(I.first_identity('SUT-02', titles), 'Sauce Labs Backpack')

    def test_an_empty_first_title_is_skipped_by_first_identity(self):
        self.assertEqual(I.first_identity('SUT-02', [None, 'Sauce Labs Bike Light']), 'Sauce Labs Bike Light')
        self.assertIsNone(I.first_identity('SUT-02', [None]))

    def test_malformed_or_empty_sources_raise(self):
        with self.assertRaises(ValueError):
            I.parse_android_card_source('<hierarchy><unclosed></hierarchy>')
        with self.assertRaises(ValueError):
            I.parse_android_titles_source('   ')
        with self.assertRaises(ValueError):
            I.parse_android_card_source(None)

    def test_normalize_title_collapses_white_space(self):
        self.assertEqual(I.normalize_title('  Sauce   Labs  Bike Light '), 'Sauce Labs Bike Light')
        self.assertIsNone(I.normalize_title('   '))
        self.assertIsNone(I.normalize_title(None))

    def test_an_unknown_sut_has_no_identity_key(self):
        with self.assertRaises(ValueError):
            I.first_identity('SUT-03', [])


if __name__ == '__main__':
    unittest.main()
