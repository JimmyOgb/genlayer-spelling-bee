import { useState, useCallback, useRef } from "react";
import { createClient } from "genlayer-js";

const GENLAYER_RPC = "https://studio.genlayer.com/api";

export function useSpellingBeeContract({ contractAddress, account }) {
  const clientRef = useRef(null);

  const getClient = useCallback(() => {
    if (!clientRef.current) {
      clientRef.current = createClient({ endpoint: GENLAYER_RPC });
    }
    return clientRef.current;
  }, []);

  const [puzzle, setPuzzle] = useState(null);
  const [playerScore, setPlayerScore] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [gameStats, setGameStats] = useState(null);
  const [foundWordsGlobal, setFoundWordsGlobal] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTxPending, setIsTxPending] = useState(false);

  const readContract = useCallback(
    async (method, args = []) => {
      try {
        const client = getClient();
        const result = await client.readContract({
          address: contractAddress,
          functionName: method,
          args,
        });
        return result;
      } catch (err) {
        console.error(`readContract(${method}) error:`, err);
        return null;
      }
    },
    [contractAddress, getClient]
  );

  const refreshPuzzle = useCallback(async () => {
    const data = await readContract("get_current_puzzle");
    if (data) setPuzzle(data);
  }, [readContract]);

  const refreshPlayerScore = useCallback(async () => {
    if (!account?.address) return;
    const data = await readContract("get_player_score", [account.address]);
    if (data) setPlayerScore(data);
  }, [account, readContract]);

  const refreshLeaderboard = useCallback(async () => {
    const data = await readContract("get_leaderboard", [10]);
    if (data) setLeaderboard(data);
  }, [readContract]);

  const refreshGameStats = useCallback(async () => {
    const data = await readContract("get_game_stats");
    if (data) setGameStats(data);
  }, [readContract]);

  const refreshFoundWords = useCallback(async () => {
    const data = await readContract("get_found_words_global");
    if (data) setFoundWordsGlobal(data);
  }, [readContract]);

  const refreshAll = useCallback(async () => {
    setIsLoading(true);
    await Promise.allSettled([
      refreshPuzzle(),
      refreshPlayerScore(),
      refreshLeaderboard(),
      refreshGameStats(),
      refreshFoundWords(),
    ]);
    setIsLoading(false);
  }, [
    refreshPuzzle,
    refreshPlayerScore,
    refreshLeaderboard,
    refreshGameStats,
    refreshFoundWords,
  ]);

  const writeContract = useCallback(
    async (method, args = []) => {
      if (!account) throw new Error("No wallet connected");
      const client = getClient();
      setIsTxPending(true);
      try {
        const txHash = await client.writeContract({
          address: contractAddress,
          functionName: method,
          args,
          account: account.address,
        });
        let receipt = null;
        for (let i = 0; i < 60; i++) {
          await new Promise((r) => setTimeout(r, 2000));
          try {
            receipt = await client.getTransactionReceipt({ hash: txHash });
            if (receipt?.status === "finalized") break;
          } catch (_) {}
        }
        return receipt?.result ?? null;
      } finally {
        setIsTxPending(false);
      }
    },
    [account, contractAddress, getClient]
  );

  const submitWord = useCallback(
    async (word) => {
      try {
        const result = await writeContract("submit_word", [word]);
        await Promise.allSettled([
          refreshPlayerScore(),
          refreshLeaderboard(),
          refreshFoundWords(),
          refreshGameStats(),
        ]);
        return result;
      } catch (err) {
        console.error("submitWord error:", err);
        return null;
      }
    },
    [writeContract, refreshPlayerScore, refreshLeaderboard, refreshFoundWords, refreshGameStats]
  );

  const getHint = useCallback(
    async (letter) => {
      try {
        return await writeContract("get_hint", [letter]);
      } catch (err) {
        console.error("getHint error:", err);
        return null;
      }
    },
    [writeContract]
  );

  return {
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
  };
}
