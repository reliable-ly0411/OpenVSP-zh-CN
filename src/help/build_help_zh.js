// Regenerate the bundled Simplified-Chinese HTML help from the Markdown sources.
// Usage: node build_help_zh.js <path-to-node_modules> [--check | --test]

const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

function headingText(tokens) {
    return tokens.map((token) => {
        // Inline markup must not become part of a heading's fragment identifier.
        if (token.type === "html" || token.type === "br") {
            return "";
        }
        return token.tokens ? headingText(token.tokens) : (token.text || "");
    }).join("");
}

function decodeHeadingEntities(text) {
    const entities = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " " };
    return text.replace(/&(#x[0-9a-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi, (entity, value) => {
        if (value[0] !== "#") {
            return entities[value.toLowerCase()];
        }
        const number = value[1].toLowerCase() === "x"
            ? parseInt(value.slice(2), 16) : parseInt(value.slice(1), 10);
        return number > 0 && number <= 0x10ffff && !(number >= 0xd800 && number <= 0xdfff)
            ? String.fromCodePoint(number) : "\ufffd";
    });
}

function createHeadingSlugger() {
    const used = new Set();
    return (text) => {
        // GitHub-style fragments: retain Chinese/other Unicode letters, lowercase
        // English, remove punctuation, and replace spaces with hyphens. Do not
        // collapse repeated spaces: existing Markdown links may use two hyphens.
        const base = decodeHeadingEntities(text).trim().toLowerCase()
            .replace(/[^\p{L}\p{M}\p{N}_\-\s]/gu, "").replace(/\s/g, "-") || "section";
        let slug = base;
        let suffix = 0;
        while (used.has(slug)) {
            slug = `${base}-${++suffix}`;
        }
        used.add(slug);
        return slug;
    };
}

function renderBody(marked, markdown) {
    // The slugger belongs to one document, not the whole regeneration run.
    const slug = createHeadingSlugger();
    const renderer = new marked.Renderer();
    renderer.heading = function (token) {
        const text = this.parser.parseInline(token.tokens);
        const id = slug(headingText(token.tokens));
        return `<h${token.depth} id="${id}">${text}</h${token.depth}>\n`;
    };
    return marked.parse(markdown, { gfm: true, renderer })
        .replace(/href="([^"]+)\.md(#[^"]*)?"/g, 'href="$1.html$2"');
}

function renderDocument(marked, markdown, name) {
    let title = path.basename(name, ".md");
    const header = markdown.match(/^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n/);
    if (header) {
        const titleMatch = header[1].match(/^title:\s*['"]?(.+?)['"]?\s*$/m);
        if (titleMatch) {
            title = titleMatch[1];
        }
        markdown = markdown.slice(header[0].length);
    }

    const body = renderBody(marked, markdown);
    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<link rel="stylesheet" href="github-pandoc.css">
</head>
<body>
${body}
</body>
</html>
`;
}

function testGenerator(marked) {
    const slug = createHeadingSlugger();
    assert.deepEqual([
        "外部干涉", "外部干涉", "外部干涉", "OpenVSP API", "OpenVSP API",
        "循环顺序预设（短舱）", "A  B", "foo", "foo-1", "foo", "foo-1", "!!!", "!!!",
    ].map(slug), [
        "外部干涉", "外部干涉-1", "外部干涉-2", "openvsp-api", "openvsp-api-1",
        "循环顺序预设短舱", "a--b", "foo", "foo-1", "foo-2", "foo-1-1", "section", "section-1",
    ]);
    assert.equal(slug("Caf\u00e9 中文_测试"), "caf\u00e9-中文_测试");
    assert.equal(slug("&#x4e2d;&#25991; &amp; API"), "中文--api");

    const source = [
        "[中文](#外部干涉) [重复](#外部干涉-1) [English](#openvsp-api)",
        "## 外部干涉", "## 外部干涉", "## OpenVSP API",
        "### **中文** &amp; [API](index.md) `X/Y`",
        "#### <em>中文</em> ![示例](image.png)",
        "Setext Title\n------------", "[跨页](GeometryAnalysis.md#外部干涉)",
    ].join("\n\n");
    const html = renderBody(marked, source);
    assert.deepEqual([...html.matchAll(/<h[1-6] id="([^"]+)"/g)].map((match) => match[1]),
        ["外部干涉", "外部干涉-1", "openvsp-api", "中文--api-xy", "中文-示例", "setext-title"]);
    const ids = new Set([...html.matchAll(/<h[1-6] id="([^"]+)"/g)].map((match) => match[1]));
    for (const [, fragment] of html.matchAll(/href="#([^"]+)"/g)) {
        assert.ok(ids.has(decodeURIComponent(fragment)), `Missing generated heading: ${fragment}`);
    }
    assert.ok(html.includes('<strong>中文</strong> &amp; <a href="index.html">API</a> <code>X/Y</code>'));
    assert.ok(html.includes(`href="GeometryAnalysis.html#${encodeURIComponent("外部干涉")}"`));
    assert.equal(renderBody(marked, "## 外部干涉"), '<h2 id="外部干涉">外部干涉</h2>\n');
    assert.equal(renderBody(marked, source), html, "Rendering must be repeatable and reset duplicate counts.");
    assert.ok(renderDocument(marked, "---\ntitle: '中文帮助'\n---\n\n## API", "test.md")
        .includes('<title>中文帮助</title>'));
    console.log("Help generator self-tests passed (Chinese/English, formatting, duplicate collisions, per-page reset).");
}

async function main() {
    const [moduleRoot, mode] = process.argv.slice(2);
    if (!moduleRoot || (mode && !["--check", "--test"].includes(mode)) || process.argv.length > 4) {
        throw new Error("Usage: node build_help_zh.js <path-to-node_modules> [--check | --test]");
    }
    // Dynamic import supports both current ESM-only marked and CommonJS packages.
    const modulePath = require.resolve(path.join(path.resolve(moduleRoot), "marked"));
    const { marked } = await import(pathToFileURL(modulePath).href);
    if (mode === "--test") {
        testGenerator(marked);
        return;
    }
    const outputDir = path.join(__dirname, "html");
    const names = fs.readdirSync(__dirname).filter((file) => file.endsWith(".md")).sort();
    if (mode !== "--check") {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    for (const name of names) {
        const markdown = fs.readFileSync(path.join(__dirname, name), "utf8");
        const html = renderDocument(marked, markdown, name);
        const output = path.join(outputDir, path.basename(name, ".md") + ".html");
        if (mode === "--check") {
            assert.equal(fs.readFileSync(output, "utf8"), html, `Regenerate stale help: ${name}`);
        } else {
            fs.writeFileSync(output, html, "utf8");
        }
    }
    console.log(`${mode === "--check" ? "Checked" : "Generated"} ${names.length} help pages.`);
}

if (require.main === module) {
    main().catch((error) => {
        console.error(error);
        process.exitCode = 1;
    });
}

module.exports = { createHeadingSlugger, renderBody, renderDocument, testGenerator };
