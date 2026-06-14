// ============================================================
// ScorePanel.jsx
// ============================================================
export function ScorePanel({ score }) {
  const RANKS = [
    { label: "Beginner", min: 0 },
    { label: "Good Start", min: 2 },
    { label: "Moving Up", min: 5 },
    { label: "Good", min: 8 },
    { label: "Solid", min: 15 },
    { label: "Nice", min: 25 },
    { label: "Great", min: 40 },
    { label: "Amazing", min: 50 },
    { label: "Genius", min: 70 },
  ];

  const points = score?.total_points ?? 0;
  const rankTitle = score?.rank_title ?? "Beginner";
  const hasPangram = score?.has_pangram ?? false;

  const currentIdx = RANKS.findIndex((r) => r.label === rankTitle);
  const nextRank = RANKS[currentIdx + 1];
  const progress = nextRank
    ? Math.min(100, ((points - RANKS[currentIdx].min) / (nextRank.min - RANKS[currentIdx].min)) * 100)
    : 100;

  return (
    <div className="bg-white/5 rounded-2xl p-5 border border-white/10">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-white/50">Your Score</span>
        {hasPangram && (
          <span className="text-xs bg-yellow-400/20 text-yellow-400 px-2 py-0.5 rounded-full">
            🌟 Pangram!
          </span>
        )}
      </div>

      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-4xl font-bold tabular-nums">{points}</span>
        <span className="text-white/40 text-sm">pts</span>
      </div>

      <p className="text-yellow-400 font-semibold text-sm mb-3">{rankTitle}</p>

      {/* Progress bar */}
      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mb-1">
        <div
          className="h-full bg-yellow-400 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {nextRank ? (
        <p className="text-xs text-white/30">
          {nextRank.min - points} more point{nextRank.min - points !== 1 ? "s" : ""} to{" "}
          <span className="text-white/50">{nextRank.label}</span>
        </p>
      ) : (
        <p className="text-xs text-yellow-400/60">Maximum rank reached 🎉</p>
      )}

      {/* Rank ladder */}
      <div className="mt-4 flex flex-wrap gap-1.5">
        {RANKS.map((r, i) => (
          <span
            key={r.label}
            className={`text-[10px] px-2 py-0.5 rounded-full border ${
              i === currentIdx
                ? "border-yellow-400 text-yellow-400 bg-yellow-400/10"
                : i < currentIdx
                ? "border-white/20 text-white/30 line-through"
                : "border-white/10 text-white/20"
            }`}
          >
            {r.label}
          </span>
        ))}
      </div>
    </div>
  );
}

// ============================================================
// FoundWords.jsx
// ============================================================
export function FoundWords({ words = [], globalWords = [] }) {
  const sorted = [...words].sort();
  const othersFound = globalWords.filter((w) => !words.includes(w));

  return (
    <div className="bg-white/5 rounded-2xl p-5 border border-white/10 flex-1">
      <h3 className="text-sm font-semibold text-white/50 mb-3">
        Your Words ({words.length})
      </h3>

      {sorted.length === 0 ? (
        <p className="text-xs text-white/25 italic">No words yet — start typing!</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {sorted.map((w) => (
            <span
              key={w}
              className="text-xs bg-white/10 px-2.5 py-1 rounded-full uppercase tracking-wide"
            >
              {w}
            </span>
          ))}
        </div>
      )}

      {othersFound.length > 0 && (
        <>
          <div className="border-t border-white/10 mt-4 pt-4">
            <h4 className="text-xs text-white/30 mb-2">
              Found by others ({othersFound.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {othersFound.slice(0, 12).map((w) => (
                <span
                  key={w}
                  className="text-xs bg-white/5 px-2.5 py-1 rounded-full uppercase tracking-wide text-white/30"
                >
                  {w}
                </span>
              ))}
              {othersFound.length > 12 && (
                <span className="text-xs text-white/20">
                  +{othersFound.length - 12} more
                </span>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ============================================================
// Leaderboard.jsx
// ============================================================
export function Leaderboard({ entries = [], currentAddress }) {
  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px] text-white/30 gap-2">
        <span className="text-4xl">🏆</span>
        <p className="text-sm">No players yet — be the first!</p>
      </div>
    );
  }

  const medals = ["🥇", "🥈", "🥉"];

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-xl font-bold mb-6">Leaderboard</h2>
      <div className="space-y-3">
        {entries.map((entry, idx) => {
          const isMe = entry.address?.toLowerCase() === currentAddress?.toLowerCase();
          return (
            <div
              key={entry.address}
              className={`flex items-center gap-4 rounded-xl p-4 border transition ${
                isMe
                  ? "border-yellow-400/40 bg-yellow-400/5"
                  : "border-white/10 bg-white/5"
              }`}
            >
              <span className="text-xl w-8 text-center">
                {medals[idx] ?? <span className="text-white/30 text-sm">#{idx + 1}</span>}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate font-mono">
                  {isMe ? (
                    <span className="text-yellow-400">You ({entry.address})</span>
                  ) : (
                    entry.address
                  )}
                </p>
                <p className="text-xs text-white/40">
                  {entry.rank_title} · {entry.words_found_count} word
                  {entry.words_found_count !== 1 ? "s" : ""}
                  {entry.has_pangram ? " · 🌟 Pangram" : ""}
                </p>
              </div>
              <span className="text-lg font-bold tabular-nums text-yellow-400">
                {entry.total_points}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ============================================================
// Toast.jsx
// ============================================================
export function Toast({ message, type = "info", definition, points, onClose }) {
  const bg = {
    success: "bg-green-500/90",
    error: "bg-red-500/80",
    warning: "bg-orange-500/80",
    info: "bg-white/10",
    pangram: "bg-yellow-400",
  }[type] ?? "bg-white/10";

  const textColor = type === "pangram" ? "text-black" : "text-white";

  return (
    <div
      className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-50 rounded-2xl shadow-2xl px-5 py-4 max-w-sm w-full mx-4 ${bg} ${textColor} backdrop-blur-sm border border-white/10`}
      onClick={onClose}
    >
      <p className="font-semibold text-sm">{message}</p>
      {points != null && (
        <p className="text-xs mt-0.5 opacity-80">+{points} points</p>
      )}
      {definition && (
        <p className="text-xs mt-1 opacity-70 italic">{definition}</p>
      )}
    </div>
  );
}
