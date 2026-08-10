// Regenerate the bundled Simplified-Chinese HTML help from the Markdown sources.
// Usage: node build_help_zh.js <path-to-node_modules>

const fs = require("fs");
const path = require("path");

const moduleRoot = process.argv[2];
if (!moduleRoot) {
    throw new Error("The Node.js module root is required.");
}

const { marked } = require(path.join(moduleRoot, "marked"));
const sourceDir = __dirname;
const outputDir = path.join(sourceDir, "html");
fs.mkdirSync(outputDir, { recursive: true });

for (const name of fs.readdirSync(sourceDir).filter((file) => file.endsWith(".md"))) {
    let markdown = fs.readFileSync(path.join(sourceDir, name), "utf8");
    let title = path.basename(name, ".md");
    const header = markdown.match(/^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n/);
    if (header) {
        const titleMatch = header[1].match(/^title:\s*['"]?(.+?)['"]?\s*$/m);
        if (titleMatch) {
            title = titleMatch[1];
        }
        markdown = markdown.slice(header[0].length);
    }

    let body = marked.parse(markdown, { gfm: true });
    body = body.replace(/href="([^"]+)\.md(#[^"]*)?"/g, 'href="$1.html$2"');
    const html = `<!DOCTYPE html>
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
    fs.writeFileSync(path.join(outputDir, path.basename(name, ".md") + ".html"), html, "utf8");
}
