// Invoked by build_help_zh.js --test with the same marked version as generation.
const assert = require("assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { buildHelp, loadLocalizedPages, renderDocument } = require("../src/help/build_help_zh.js");

function testBuildScope(marked) {
    const temp = fs.mkdtempSync(path.join(os.tmpdir(), "openvsp-help-test-"));
    try {
        const help = path.join(temp, "help");
        fs.mkdirSync(path.join(help, "html"), { recursive: true });
        const manifest = (pages) => fs.writeFileSync(path.join(help, "localized_pages.json"), JSON.stringify(pages));
        const source = "## 中文帮助\n";
        fs.writeFileSync(path.join(help, "index.md"), source);
        const output = path.join(help, "html", "index.html");
        fs.writeFileSync(output, "stale localized page");
        fs.writeFileSync(path.join(help, "upstream.md"), "## English with $x^2$\n");
        const upstream = path.join(help, "html", "upstream.html");
        const preserved = Buffer.from('<html>\r\n<math><msup><mi>x</mi><mn>2</mn></msup></math>\r\n</html>');
        fs.writeFileSync(upstream, preserved);
        manifest(["index.md"]);
        assert.throws(() => buildHelp(marked, help, true), /Regenerate stale help/);
        assert.equal(fs.readFileSync(output, "utf8"), "stale localized page", "--check must not write");
        assert.equal(buildHelp(marked, help, false), 1);
        assert.equal(fs.readFileSync(output, "utf8"), renderDocument(marked, source, "index.md"));
        assert.equal(buildHelp(marked, help, true), 1);
        assert.deepEqual(fs.readFileSync(upstream), preserved, "Unlisted HTML must retain its exact bytes");
        for (const pages of [[], {}, ["index.md", "index.md"], [null], ["../index.md"],
            ["/tmp/index.md"], ["html/index.md"], ["..\\index.md"], ["C:\\index.md"], ["index.html"],
            ["index.md", "missing.md"]]) {
            manifest(pages);
            fs.writeFileSync(output, "do not write before validation");
            assert.throws(() => buildHelp(marked, help, false), undefined, JSON.stringify(pages));
            assert.equal(fs.readFileSync(output, "utf8"), "do not write before validation");
        }
        manifest(["index.md"]);
        fs.unlinkSync(output);
        assert.throws(() => loadLocalizedPages(help), /ENOENT/);
        const outside = path.join(temp, "outside.html");
        fs.writeFileSync(outside, "outside");
        fs.symlinkSync(outside, output);
        assert.throws(() => buildHelp(marked, help, false), /escapes help directory/);
        assert.equal(fs.readFileSync(outside, "utf8"), "outside");
        fs.unlinkSync(output);
        fs.symlinkSync(upstream, output);
        assert.throws(() => buildHelp(marked, help, false), /must not alias another path/);
        assert.deepEqual(fs.readFileSync(upstream), preserved);
        fs.unlinkSync(output);
        fs.writeFileSync(output, "safe output");
        fs.unlinkSync(path.join(help, "index.md"));
        fs.symlinkSync(outside, path.join(help, "index.md"));
        assert.throws(() => loadLocalizedPages(help), /escapes help directory/);
    } finally {
        fs.rmSync(temp, { recursive: true, force: true });
    }
    console.log("Help scope tests passed (manifest, paths, missing files, symlinks, check-only, upstream byte preservation).");
}
module.exports = { testBuildScope };
