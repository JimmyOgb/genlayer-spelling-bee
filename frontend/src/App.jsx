import { useState, useEffect, useCallback } from "react";
import { createWalletClient, custom } from "viem";
import HoneycombGrid from "./components/HoneycombGrid";
import WordInput from "./components/WordInput";
import { ScorePanel, FoundWords, Leaderboard, Toast } from "./components/index";
import { useSpellingBeeContract } from "./hooks/useSpellingBeeContract";
import { formatAddress } from "./lib/utils";

const CONTRACT_ADDRESS = "0x63Bfa1201F0b4e95bc9f7f1473c8cB57d2afa0Ac";

export default function App() {
  const [account, setAccount] = useState(null);
  const [activeTab, setActiveTab] = useState("game");
  const [toast, setToast] = useState(null);

  const {
    puzzle,
    playerScore,
    leaderboard,
    gameStats,
    foundWordsGlobal,
    isLoading,
    isTxPending,
    submitWord,
    getHint,
    refreshAll,
  } = useSpellingBeeContract({ contractAddress: CONTRACT_ADDRESS, account });

  const connectWallet = useCallback(async () => {
    if (!window.ethereum) {
      showToast("Please install MetaMask or a compatible wallet.", "error");
      return;
    }
    try {
      const [addr] = await window.ethereum.request({
        method: "eth_requestAccounts",
      });
      setAccount({ address: addr });
    } catch (err) {
      showToast("Wallet connection failed.", "error");
    }
  }, []);

  const showToast = useCallback((message, type = "info", extra = {}) => {
    setToast({ message, type, ...extra });
    setTimeout(() => setToast(null), 4500);
  }, []);

  const handleWordSubmit = useCallback(
    async (word) => {
      if (!account) {
        showToast("Connect your wallet to play!", "warning");
        return;
      }
      const result = await submitWord(word);
      if (!result) return;
      if (result.accepted) {
        showToast(result.message, result.is_pangram ? "pangram" : "success", {
          definition: result.definition,
          points: result.points_earned,
        });
      } else {
        showToast(result.message, "error");
      }
    },
    [account, submitWord, showToast]
  );

  const handleHint = useCallback(
    async (letter) => {
      const hint = await getHint(letter);
      if (hint) showToast(hint, "info");
    },
    [getHint, showToast]
  );

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 30000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  return (
    <div className="min-h-screen bg-[#0f0f13] text-white font-sans">
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🐝</span>
          <div>
            <h1 className="text-lg font-bold tracking-tight">GenLayer Spelling Bee</h1>
            {puzzle && (
              <p className="text-xs text-white/40">
                Round #{puzzle.round_number} · {puzzle.theme}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4">
          {gameStats && (
            <span className="text-xs text-white/40 hidden sm:block">
              {gameStats.total_players} players · {gameStats.total_words_discovered} words found
            </span>
          )}
          {account ? (
            <div className="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-full text-sm">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              {formatAddress(account.address)}
            </div>
          ) : (
            <button
              onClick={connectWallet}
              className="bg-yellow-400 text-black font-semibold text-sm px-4 py-2 rounded-full hover:bg-yellow-300 transition"
            >
              Connect Wallet
            </button>
          )}
        </div>
      </header>

      <nav className="flex border-b border-white/10 px-6">
        {["game", "leaderboard"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`py-3 px-4 text-sm font-medium capitalize transition border-b-2 -mb-px ${
              activeTab === tab
                ? "border-yellow-400 text-yellow-400"
                : "border-transparent text-white/40 hover:text-white/70"
            }`}
          >
            {tab}
          </button>
        ))}
      </nav>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {isLoading && !puzzle ? (
          <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
            <div className="w-10 h-10 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-white/40 text-sm">GenLayer AI is generating your puzzle…</p>
          </div>
        ) : activeTab === "game" ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 flex flex-col items-center gap-6">
              {puzzle && (
                <>
                  <HoneycombGrid
                    centerLetter={puzzle.center_letter}
                    outerLetters={puzzle.outer_letters}
                    onHint={handleHint}
                  />
                  <WordInput
                    centerLetter={puzzle.center_letter}
                    allowedLetters={[puzzle.center_letter, ...puzzle.outer_letters]}
                    onSubmit={handleWordSubmit}
                    disabled={isTxPending || !account}
                    isPending={isTxPending}
                  />
                  {!account && (
                    <p className="text-sm text-white/30">Connect wallet to submit words</p>
                  )}
                </>
              )}
            </div>
            <div className="flex flex-col gap-4">
              <ScorePanel score={playerScore} />
              <FoundWords
                words={playerScore?.words_found ?? []}
                globalWords={foundWordsGlobal}
              />
            </div>
          </div>
        ) : (
          <Leaderboard entries={leaderboard} currentAddress={account?.address} />
        )}
      </main>

      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
    </div>
  );
}
