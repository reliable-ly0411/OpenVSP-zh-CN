# OpenVSP 3.55.0 rc.2 recovered desktop evidence

The attached archive is the unchanged original desktop acceptance receipt recorded at 2026-10-20T05:47:44Z, not a new run and not the older CI captured_not_reviewed screenshots.

- Archive SHA-256: `6f6dcf4a06115c44cd0ab3e345ff73cc4c309e257fafe9d81cc3275127137cb7`.
- Original Ubuntu 24.04 AMD64 ZIP SHA-256: `1220a109b037681fd77f468245f3300f78878fbd96561012ff8e41b24fbb5c5b`.
- Source: `85a1a1a2029d0ab35e1a5f685a117061fe89aa21`; original build run: [39351908980](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39351908980).
- Recovery verification on 2026-10-20 UTC: all nine screenshot hashes match the receipt; screenshots were independently visually inspected. Saved and reopened model XML retain the exact names `Wing & Body_100% 中文` and `Fuselage` with unchanged geometry IDs.
- Covered: main window, geometry tree, wing general and planform pages, About software/localization version, GUI save and reopen using spaces, percent sign and Chinese in the file name.
- Environment: Debian 13 Linux x86_64 cloud desktop, running the original Ubuntu 24.04-built ZIP. Other platform GUI and complete engineering validation are not covered.
- At the original recovery checkpoint, the four remaining version-family desktop reviews were pending. Those reviews are now complete; see the [consolidated five-family acceptance report](../../../five-family-rc2-acceptance-20261020.md). This preserved 3.55.0 receipt alone is not a five-family promotion decision.

The original receipt is preserved as `recovered-gui-review.json`; full screenshots and saved model files are in `recovered-desktop-acceptance.zip`.
