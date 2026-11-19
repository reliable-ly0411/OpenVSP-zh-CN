# OpenVSP 3.56 Chinese help integration preflight

Source baseline: `ed364d66fe64309ce886b53c5911bba404c265cd`. Draft snapshot: `ddc69d585aba6a460a285aeb9e6cb2c287139181`. Neither source help nor checked-in HTML has been changed by this preflight.

## Static evidence

- Fetched all 19 original Markdown files, staged translations and baseline bundled HTML from the exact snapshots above.
- Matched 421 literal Markdown link and HTML image-source occurrences as multisets, with no translated-page mismatch.
- Matched all 193 explicit draft anchors to actual IDs in the corresponding baseline bundled HTML. No duplicate explicit IDs were found in the draft pages. This does not prove that a generated page has no collisions.
- Draft index omits Airfoils, FuselageStack, XFormTab and XSecSkinning. The first three include draft provenance in the body, and XFormTab also has a draft suffix in the title. Keep the source references in the integration review record instead of rendering the draft notices.
- The following pages contain apparent TeX math without the explicit Pandoc renderer: Airfoils, Chevron, EngineModel, FuselageStack, Gear, Human, Mesh, PtCloud, Routing, SubTab, Wire, XFormTab, XSecSkinning. Review the expressions and add `help-renderer: pandoc` where needed because the marked renderer does not produce MathML. Six drafts already opt in. NGonMesh did not match the lexical math probe.

## Integration gates

1. Work from a fresh independent combined candidate. Recheck target files against the integration base. Copy the reviewed drafts to `src/help/`, remove only draft metadata, and retain actual upstream migration notices.
2. Add exactly the 19 pages to `src/help/localized_pages.json` and the exact-set tests in `scripts/test_help_anchors.py` (11 to 30); do not overwrite non-localized upstream HTML.
3. Use the repository's Node/marked and Pandoc MathML paths. Run `node src/help/build_help_zh.js <node_modules> --test`, generate without a mode argument, rerun with `--check`, and run `python3 scripts/test_help_anchors.py -v`.
4. Check rendered titles, old fragment targets, MathML, tables, links/images, and installed help under both `help` and `python/openvsp/openvsp/help_vsp`. Existing Python CI does not replace HTML generation and visual review.

This branch records source-level evidence only. No generator, build, browser check, merge or release ran in this preflight.
