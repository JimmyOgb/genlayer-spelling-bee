/**
 * Truncate an Ethereum address for display.
 * e.g. 0x1234...abcd
 */
export function formatAddress(address, chars = 4) {
  if (!address) return "";
  return `${address.slice(0, chars + 2)}…${address.slice(-chars)}`;
}

/**
 * Calculate Spelling Bee word points (mirrors contract logic).
 */
export function calculatePoints(word, allLetters) {
  const len = word.length;
  if (len < 4) return 0;
  if (len === 4) return 1;
  const isPangram = allLetters.every((l) =>
    word.toLowerCase().includes(l.toLowerCase())
  );
  return len + (isPangram ? 7 : 0);
}

/**
 * Determine rank title from points.
 */
export function getRankTitle(points) {
  const ranks = [
    [70, "Genius"],
    [50, "Amazing"],
    [40, "Great"],
    [25, "Nice"],
    [15, "Solid"],
    [8, "Good"],
    [5, "Moving Up"],
    [2, "Good Start"],
    [0, "Beginner"],
  ];
  for (const [threshold, title] of ranks) {
    if (points >= threshold) return title;
  }
  return "Beginner";
}

/**
 * Sleep for ms milliseconds.
 */
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Retry an async fn up to `times` times with `delay` ms between attempts.
 */
export async function retry(fn, times = 3, delay = 1000) {
  for (let i = 0; i < times; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === times - 1) throw err;
      await sleep(delay);
    }
  }
}
