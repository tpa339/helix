#!/usr/bin/env node
const fs = require("fs");

try {
  const input = fs.readFileSync(0, "utf8");
  const payload = JSON.parse(input || "{}");
  const text = JSON.stringify(payload.tool_input || {});

  if (text.length > 20000) {
    console.error("BLOCKED: tool input too large. Compress the context before writing or editing.");
    process.exit(2);
  }
} catch {
  process.exit(0);
}
