const fs = require("fs");

for (const file of ["frontend/auth.html", "frontend/chat.html", "frontend/landing.html"]) {
  const html = fs.readFileSync(file, "utf8");
  const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)];
  scripts.forEach((match, index) => {
    try { new Function(match[1]); }
    catch (error) { throw new Error(`${file} inline script ${index}: ${error.message}`); }
  });
  console.log(`${file}: ${scripts.length} inline scripts valid`);
}
