/**
 * Rushmore TikTok Screen Recording
 * Records the actual rushmore.cards website: search players → select 5 → generate card.
 * Output: output/2026-04-10/tiktok_rushmore.webm
 *
 * Run: node tools/record_tiktok.js
 * Convert: ffmpeg -i tiktok_rushmore.webm -c:v libx264 -preset slow -crf 20 tiktok_rushmore.mp4
 */

const { chromium } = require("playwright");
const path = require("path");

const OUTPUT_DIR = path.resolve(__dirname, "../output/2026-04-10");

const PLAYERS = [
  "Jordan",
  "Kareem",
  "Magic Johnson",
  "Kobe Bryant",
  "LeBron James",
];

async function wait(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

(async () => {
  console.log("Launching browser…");

  const browser = await chromium.launch({ headless: true });

  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    recordVideo: {
      dir: OUTPUT_DIR,
      size: { width: 390, height: 844 },
    },
  });

  const page = await context.newPage();

  // ── 1. Homepage (2.5s) ────────────────────────────────────────────────────
  console.log("Homepage…");
  await page.goto("https://rushmore.cards", { waitUntil: "networkidle" });
  await wait(2500);

  // ── 2. Navigate to Build ──────────────────────────────────────────────────
  console.log("Build page…");
  await page.goto("https://rushmore.cards/build", { waitUntil: "networkidle" });
  await wait(1500);

  // ── 3. Search + select each player ────────────────────────────────────────
  const searchInput = page.locator("input[placeholder='Search ballers...']");

  for (const query of PLAYERS) {
    console.log(`Searching: ${query}`);

    await searchInput.click();
    await searchInput.fill("");
    await wait(300);
    await searchInput.pressSequentially(query, { delay: 80 });
    await wait(1200);

    // Click first unselected player card in list
    const playerCards = page.locator(".rounded-xl.border.cursor-pointer");
    const first = playerCards.first();
    await first.waitFor({ state: "visible", timeout: 5000 });
    await first.click();
    await wait(900);

    // Clear search for next player
    await searchInput.fill("");
    await wait(400);
  }

  // ── 4. Short pause — show the filled list ─────────────────────────────────
  await wait(1500);

  // ── 5. Click "Build Your Card" in the SelectionBar ───────────────────────
  console.log("Building card…");
  const buildBtn = page.getByRole("button", { name: "Build Your Card", exact: true });
  await buildBtn.waitFor({ state: "visible", timeout: 8000 });

  // Scroll it into view (it's at the bottom bar)
  await buildBtn.scrollIntoViewIfNeeded();
  await wait(500);
  await buildBtn.click();

  // ── 6. Wait for card preview modal ────────────────────────────────────────
  console.log("Waiting for card…");
  await wait(5000);

  // ── 7. Hold on the result ─────────────────────────────────────────────────
  await wait(3000);

  // ── 8. Done ───────────────────────────────────────────────────────────────
  const videoPath = await page.video().path();
  await context.close();
  await browser.close();

  // Rename to a predictable filename
  const fs = require("fs");
  const finalPath = path.join(OUTPUT_DIR, "tiktok_rushmore.webm");
  if (fs.existsSync(finalPath)) fs.unlinkSync(finalPath);
  fs.renameSync(videoPath, finalPath);

  console.log(`\n✓ Video saved: ${finalPath}`);
  console.log(
    "Convert to MP4:\n  ffmpeg -i output/2026-04-10/tiktok_rushmore.webm -c:v libx264 -preset slow -crf 20 -vf scale=1080:1848 output/2026-04-10/tiktok_rushmore.mp4"
  );
})();
