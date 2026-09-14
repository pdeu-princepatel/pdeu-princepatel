// Fetches the public GitHub contribution calendar for a user and renders it
// as an animated SVG: each square drops down and fades out at the bottom,
// pauses, then drops in from the top back into its original spot — looping.

const fs = require("fs");

const USERNAME = process.argv[2];
if (!USERNAME) {
  console.error("Usage: node generate.js <github-username> [output-path]");
  process.exit(1);
}
const OUT = process.argv[3] || "contribution-drop.svg";

const CELL = 11;      // pitch between squares (matches GitHub's own spacing)
const SIZE = 10;      // square size
const RADIUS = 2;
const MARGIN_LEFT = 20;
const MARGIN_TOP = 10;
const DROP_DISTANCE = 46; // how far squares fall before vanishing

// GitHub's contribution colors, level 0-4
const LIGHT_COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"];
const DARK_COLORS  = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"];

async function main() {
  const res = await fetch(`https://github.com/users/${USERNAME}/contributions`, {
    headers: { "User-Agent": "Mozilla/5.0" },
  });
  if (!res.ok) throw new Error(`Failed to fetch contributions: ${res.status}`);
  const html = await res.text();

  const tdRegex = /<td\b[^>]*class="ContributionCalendar-day"[^>]*>/g;
  const cells = [];
  let match;
  while ((match = tdRegex.exec(html))) {
    const tag = match[0];
    const dateMatch = tag.match(/data-date="([^"]+)"/);
    const levelMatch = tag.match(/data-level="(\d+)"/);
    const idMatch = tag.match(/id="contribution-day-component-(\d+)-(\d+)"/);
    if (!dateMatch || !levelMatch || !idMatch) continue;
    cells.push({
      date: dateMatch[1],
      level: parseInt(levelMatch[1], 10),
      row: parseInt(idMatch[1], 10), // 0-6, day of week
      col: parseInt(idMatch[2], 10), // 0-52, week index
    });
  }

  if (cells.length === 0) throw new Error("No contribution cells parsed — GitHub markup may have changed.");

  const maxCol = Math.max(...cells.map((c) => c.col));
  const width = MARGIN_LEFT + (maxCol + 1) * CELL + 10;
  const height = MARGIN_TOP + 7 * CELL + 10;
  const totalCycle = 6; // seconds for one full loop

  const rects = cells
    .map((c) => {
      const x = MARGIN_LEFT + c.col * CELL;
      const y = MARGIN_TOP + c.row * CELL;
      const delay = (c.col * 0.025).toFixed(3); // staggers columns into a wave
      return `<rect x="${x}" y="${y}" width="${SIZE}" height="${SIZE}" rx="${RADIUS}" ry="${RADIUS}" fill="${DARK_COLORS[c.level]}" class="cell lvl-${c.level}" style="animation-delay:${delay}s"><title>${c.date}: level ${c.level}</title></rect>`;
    })
    .join("\n    ");

  const svg = `<svg viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {
      --color-0: ${LIGHT_COLORS[0]};
      --color-1: ${LIGHT_COLORS[1]};
      --color-2: ${LIGHT_COLORS[2]};
      --color-3: ${LIGHT_COLORS[3]};
      --color-4: ${LIGHT_COLORS[4]};
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --color-0: ${DARK_COLORS[0]};
        --color-1: ${DARK_COLORS[1]};
        --color-2: ${DARK_COLORS[2]};
        --color-3: ${DARK_COLORS[3]};
        --color-4: ${DARK_COLORS[4]};
      }
    }
    .cell {
      animation-name: dropRise;
      animation-duration: ${totalCycle}s;
      animation-timing-function: ease-in-out;
      animation-iteration-count: infinite;
      transform-box: fill-box;
      transform-origin: center;
    }
    .lvl-0 { fill: var(--color-0); }
    .lvl-1 { fill: var(--color-1); }
    .lvl-2 { fill: var(--color-2); }
    .lvl-3 { fill: var(--color-3); }
    .lvl-4 { fill: var(--color-4); }

    @keyframes dropRise {
      0%   { transform: translateY(0); opacity: 1; }
      28%  { transform: translateY(${DROP_DISTANCE}px); opacity: 0; }
      38%  { transform: translateY(${DROP_DISTANCE}px); opacity: 0; }
      39%  { transform: translateY(-${DROP_DISTANCE}px); opacity: 0; }
      55%  { transform: translateY(-${DROP_DISTANCE}px); opacity: 0; }
      85%  { transform: translateY(0); opacity: 1; }
      100% { transform: translateY(0); opacity: 1; }
    }
  </style>
  <g>
    ${rects}
  </g>
</svg>
`;

  fs.writeFileSync(OUT, svg);
  console.log(`Wrote ${OUT} with ${cells.length} cells.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});