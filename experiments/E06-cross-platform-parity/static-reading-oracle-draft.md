# E06: static reading of the catalogue-position oracle of CS-007 (decision point DP-3), DRAFT

| Field | Value |
|---|---|
| Status | DRAFT, preparation only. It freezes, starts, authorizes, and dispatches nothing, and it is not evidence about any system under test (SUT). |
| Date | 2026-11-20 |
| Serves | DP-3 of experiments/scenario-mappings/CS-007.yaml (DRAFT): "accept a provisional COMPARABLE for the Android cells with the item-level selector read from the pinned source and recorded before the freeze, or narrow the mobile oracle to arrival only". |
| Basis | Read-only fetch of six public source files at the pinned commits of manifests/sut-manifest.yaml; the files were kept only in a scratch folder and are not in the repository. No clone, no build, no run, no APK download. |
| Not read | The E01 adjudicated matrix (common rule 2); any qualification or smoke artifact (protocol/mobile-runner-policy-v3.md, section 3). |

## 1. Files read (SHA-256 of the fetched bytes)

| Surface | Repository at pinned commit | File | SHA-256 |
|---|---|---|---|
| SUT-01 Android | OmniPizza at 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a (release v1.1.8) | frontend-mobile/src/components/PizzaCard.tsx | ce4dceb80874247fc536d1f5129f9b50781d6437800e9830c1d0d0db331b991b |
| SUT-01 Android | same | frontend-mobile/src/screens/CatalogScreen.tsx | abc20792c4b0b03bbc300c77c877bd1a5d8293ab555e4762fa50cbf74227cd4a |
| SUT-01 Android | same | frontend-mobile/src/utils/qa.ts | caa1c15ef177b80fdefb0cbca9c6a62f620bd84f4425f98780074848912da64c |
| SUT-02 Android | my-demo-app-android at 36b012eecdf6a2b488b9504e16b3d0c3ca9a0e7b (release 2.2.0) | app/src/main/res/layout/item_products.xml | 40e6baead553a9beaa6452f721882f6de40d976baa2cfa239eec271233e69ff3 |
| SUT-02 Android | same | app/src/main/java/com/saucelabs/mydemoapp/android/viewModel/ProductCatalogViewModel.java | d90b8ddd24d4cddf6e9254d4472f93af5afff725dba3a97e44a0b04674e0311b |
| SUT-02 Android | same | app/src/main/java/com/saucelabs/mydemoapp/android/view/activities/MainActivity.java | 7097f2631f40beed4f2b25e6a3812cbf555c4354df2da0f98b8d1d589a334eab |

## 2. Findings

**SUT-01 Android.** Each catalogue entry is a `PizzaCard` (PizzaCard.tsx, line 23) whose root view carries `testID` and `accessibilityLabel` `card-pizza-<id>`; the name text carries `getReadableTextProps("text-pizza-name-<id>", pizza.name)` (line 41). On Android `getReadableTextProps` sets `testID` to the identifier and `accessibilityLabel` to the readable text (qa.ts, lines 36 to 45), so the name is exposed as the accessibility label of the node whose test identifier is `text-pizza-name-<id>`. The list is `useCatalogPizzas(country, language)` filtered by the search text and the category (CatalogScreen.tsx, lines 27 and 39 to 49): the entry at the first position is the first item the hosted backend returns for the market and language, after the default filters (search empty, category `all`). The pizza `<id>` therefore appears in the card identifier. The item set and its order come from the backend, which no pin governs for the release APK (the origin is a compile-time constant; qualification/compatibility-smoke-sut01/README.md, source finding).

**SUT-02 Android.** Each entry inflates `item_products.xml`: `productIV` (the image, content description "Displays selected product"), `titleTV` (the product title text), `priceTV`, and a rating view. The default sort is name ascending (`MainActivity.selectedSort = NAME_ASC`, line 101), so the first entry is the first title in ascending name order from the local database (`ProductCatalogViewModel.getAllProducts`, which queries `getPersonsSortByAscName`). Prices are randomized only under the visual-change mode (`hasVisualChanges`); titles are not changed by it.

**Web surfaces** (SUT-01 `pizza-name-<id>` of SUT01-EV-0003 and SUT01-EV-0019; SUT-02 inventory item name of SUT02-EV-0013) were not re-read here; they come from the E01 rows already cited by CS-007.

## 3. Reading for DP-3

- The identity of the entry at the fixed first catalogue position is statically readable on the two Android surfaces: SUT-01 by the accessibility label of the name node and the id inside the card identifier; SUT-02 by the text of `titleTV`. This supports the "accept" option of DP-3 for these two surfaces, as a configuration item.
- Not established by static reading, and only a run can show it: whether the Android accessibility tree exposes these nodes with the expected attributes and match counts (the SUT-01 smoke checks login controls only; the catalogue item identity is not read by it); whether the SUT-01 hosted backend returns the same first item as the web surface under the pinned controlled instance (the two surfaces then differ in backend, a threat to the cross-surface identity reading that has to be disclosed: HOSTED_MAPPING_UNVERIFIED); and whether the order of the SUT-01 catalogue is stable across executions and markets.
- If a non-measured DRY_RUN shows that an item identity cannot be read on a surface, the fallback of DP-3 applies to that surface (arrival only) and the change is recorded before the START, never after data.

This text decides nothing: DP-3 is a human decision, and CS-007 stays a DRAFT until its own freeze approval.
