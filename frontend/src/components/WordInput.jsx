import { useState, useCallback, useEffect, useRef } from "react";

/**
 * WordInput
 * Letter-by-letter input bar that validates each keystroke against
 * the allowed puzzle letters and shows a "shuffle" button.
 */
export default function WordInput({
  centerLetter,
  allowedLetters,
  onSubmit,
  disabled,
  isPending,
}) {
  const [word, setWord] = useState("");
  const [shake, setShake] = useState(false);
  const inputRef = useRef(null);

  const allowedSet = new Set(allowedLetters.map((l) => l.toUpperCase()));

  const handleKey = useCallback(
    (e) => {
      if (disabled) return;

      const key = e.key.toUpperCase();

      if (e.key === "Enter") {
        e.preventDefault();
        handleSubmit();
        return;
      }
      if (e.key === "Backspace") {
        setWord((w) => w.slice(0, -1));
        return;
      }
      if (key.length === 1 && /[A-Z]/.test(key)) {
        if (!allowedSet.has(key)) {
          // Illegal letter — shake
          triggerShake();
          return;
        }
        setWord((w) => w + key.toLowerCase());
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [disabled, allowedSet, word]
  );

  const handleSubmit = useCallback(async () => {
    if (!word || disabled) return;
    await onSubmit(word);
    setWord("");
  }, [word, disabled, onSubmit]);

  const triggerShake = () => {
    setShake(true);
    setTimeout(() => setShake(false), 500);
  };

  useEffect(() => {
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [handleKey]);

  const displayWord = word || "";

  return (
    <div className="flex flex-col items-center gap-4 w-full max-w-sm">
      {/* Word display */}
      <div
        className={`relative w-full border-b-2 border-white/20 pb-2 text-center transition-all ${
          shake ? "animate-[shake_0.4s_ease-in-out]" : ""
        }`}
        style={shake ? { animation: "shake 0.4s ease-in-out" } : {}}
      >
        <span className="text-3xl font-bold tracking-widest uppercase">
          {displayWord.split("").map((ch, i) => (
            <span
              key={i}
              className={
                ch === centerLetter.toLowerCase()
                  ? "text-yellow-400"
                  : "text-white"
              }
            >
              {ch}
            </span>
          ))}
          {!displayWord && (
            <span className="text-white/20 text-2xl">Type a word…</span>
          )}
        </span>
        {/* Blinking cursor */}
        <span className="inline-block w-0.5 h-7 bg-yellow-400 ml-1 align-middle animate-pulse" />
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setWord("")}
          disabled={!word || disabled}
          className="px-4 py-2 rounded-full border border-white/20 text-sm text-white/60 hover:border-white/40 hover:text-white disabled:opacity-30 transition"
        >
          Delete
        </button>

        <button
          onClick={handleSubmit}
          disabled={!word || disabled || isPending}
          className="px-6 py-2 rounded-full bg-yellow-400 text-black font-semibold text-sm hover:bg-yellow-300 disabled:opacity-30 disabled:cursor-not-allowed transition flex items-center gap-2"
        >
          {isPending ? (
            <>
              <span className="w-3 h-3 border border-black border-t-transparent rounded-full animate-spin" />
              Validating…
            </>
          ) : (
            "Enter"
          )}
        </button>
      </div>

      {/* Keyboard shortcut hint */}
      <p className="text-xs text-white/25">
        Type on keyboard · Backspace to delete · Enter to submit
      </p>

      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          20% { transform: translateX(-6px); }
          40% { transform: translateX(6px); }
          60% { transform: translateX(-4px); }
          80% { transform: translateX(4px); }
        }
      `}</style>
    </div>
  );
}
