# { "Depends": "py-genlayer:test" }
"""
GenLayer Spelling Bee — Intelligent Contract
=============================================
An on-chain Spelling Bee game powered by GenLayer's AI consensus.
Words, definitions, and scoring are all validated through the
Optimistic Democracy consensus mechanism using LLMs.

Contract Address (Testnet): 0x63Bfa1201F0b4e95bc9f7f1473c8cB57d2afa0Ac
"""

import json
try:
    from genlayer import *
except ImportError:
    pass


@gl.dataclass
class GameRound:
    center_letter: str
    outer_letters: list[str]
    pangrams: list[str]
    theme: str
    date_generated: str


@gl.dataclass
class PlayerScore:
    address: str
    total_points: int
    words_found: list[str]
    has_pangram: bool
    rank_title: str


RANK_THRESHOLDS = [
    (0, "Beginner"),
    (2, "Good Start"),
    (5, "Moving Up"),
    (8, "Good"),
    (15, "Solid"),
    (25, "Nice"),
    (40, "Great"),
    (50, "Amazing"),
    (70, "Genius"),
]


class SpellingBee(gl.Contract):
    # --- State ---
    current_round: GameRound
    player_scores: TreeMap[str, PlayerScore]
    all_found_words: TreeMap[str, list[str]]   # word -> list of finder addresses
    round_number: int
    total_players: int
    leaderboard: list[str]                     # sorted list of addresses by score

    def __init__(self) -> None:
        self.round_number = 0
        self.total_players = 0
        self.leaderboard = []
        self.player_scores = TreeMap()
        self.all_found_words = TreeMap()

        # Bootstrap the first round via AI
        self._generate_new_round()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _generate_new_round(self) -> None:
        """Use the LLM to generate a new Spelling Bee puzzle."""

        def _nondet_generate():
            prompt = """Generate a Spelling Bee puzzle in JSON.

Rules:
- Choose 7 unique letters (A-Z, no duplicates).
- One letter is the "center" and must appear in every valid word.
- Words must be at least 4 letters, use only the 7 chosen letters, and contain the center letter.
- Include 3-5 pangrams (words that use all 7 letters at least once).
- Choose a light thematic hint (e.g. "Nature & Animals", "Food & Cooking").

Respond ONLY with this JSON, no extra text:
{
  "center_letter": "A",
  "outer_letters": ["B", "C", "D", "E", "F", "G"],
  "pangrams": ["example1", "example2"],
  "theme": "Nature & Animals"
}"""
            result = gl.exec_prompt(prompt)
            raw = result.strip()
            # Strip possible markdown fences
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:])
            if raw.endswith("```"):
                raw = "\n".join(raw.split("\n")[:-1])
            data = json.loads(raw)
            return json.dumps(data, sort_keys=True)

        raw = gl.eq_principle_prompt_comparative(_nondet_generate)
        data = json.loads(raw)

        import datetime
        today = datetime.date.today().isoformat()

        self.current_round = GameRound(
            center_letter=data["center_letter"].upper(),
            outer_letters=[l.upper() for l in data["outer_letters"]],
            pangrams=[w.lower() for w in data["pangrams"]],
            theme=data.get("theme", "General"),
            date_generated=today,
        )
        self.round_number += 1

    def _calculate_word_points(self, word: str, letters: list[str]) -> int:
        """Standard Spelling Bee scoring rules."""
        length = len(word)
        if length < 4:
            return 0
        if length == 4:
            return 1
        # pangram bonus
        all_letters = set(letters)
        is_pangram = all(l in word.upper() for l in all_letters)
        base = length
        return base + (7 if is_pangram else 0)

    def _get_rank(self, points: int) -> str:
        rank = "Beginner"
        for threshold, title in RANK_THRESHOLDS:
            if points >= threshold:
                rank = title
        return rank

    def _update_leaderboard(self, player_address: str) -> None:
        """Keep leaderboard sorted (simple insertion sort for small sets)."""
        if player_address not in self.leaderboard:
            self.leaderboard.append(player_address)

        self.leaderboard.sort(
            key=lambda addr: self.player_scores[addr].total_points
            if addr in self.player_scores
            else 0,
            reverse=True,
        )

    # ------------------------------------------------------------------ #
    #  Validation helpers (non-deterministic / LLM)                       #
    # ------------------------------------------------------------------ #

    def _validate_word_with_ai(
        self, word: str, center: str, letters: list[str]
    ) -> bool:
        """Ask the LLM whether a word is a real English word."""

        all_letters = [center] + letters

        def _nondet_validate():
            prompt = f"""You are a Spelling Bee judge.

Puzzle letters: {", ".join(all_letters)}
Center letter (required): {center}
Submitted word: "{word}"

Rules:
1. The word must be a real, common English dictionary word.
2. It must contain the center letter "{center}".
3. It must use only the puzzle letters.
4. It must be at least 4 letters long.
5. Proper nouns, obscene words, and abbreviations are NOT allowed.

Reply with ONLY "valid" or "invalid" — no other text."""
            result = gl.exec_prompt(prompt)
            verdict = result.strip().lower()
            if "valid" in verdict:
                return "valid"
            return "invalid"

        verdict = gl.eq_principle_prompt_comparative(_nondet_validate)
        return verdict.strip().lower() == "valid"

    def _get_word_definition(self, word: str) -> str:
        """Fetch a short definition of a word using the LLM."""

        def _nondet_define():
            prompt = f'Give a single, concise dictionary definition for the word "{word}". Reply with ONLY the definition, no punctuation at the start, no word echo.'
            return gl.exec_prompt(prompt)

        return gl.eq_principle_prompt_comparative(_nondet_define).strip()

    # ------------------------------------------------------------------ #
    #  Public VIEW methods                                                 #
    # ------------------------------------------------------------------ #

    @gl.public.view
    def get_current_puzzle(self) -> dict:
        """Return the current puzzle state."""
        return {
            "round_number": self.round_number,
            "center_letter": self.current_round.center_letter,
            "outer_letters": self.current_round.outer_letters,
            "theme": self.current_round.theme,
            "date_generated": self.current_round.date_generated,
        }

    @gl.public.view
    def get_player_score(self, player_address: str) -> dict:
        """Return a player's current score and found words."""
        if player_address not in self.player_scores:
            return {
                "address": player_address,
                "total_points": 0,
                "words_found": [],
                "has_pangram": False,
                "rank_title": "Beginner",
            }
        score = self.player_scores[player_address]
        return {
            "address": score.address,
            "total_points": score.total_points,
            "words_found": score.words_found,
            "has_pangram": score.has_pangram,
            "rank_title": score.rank_title,
        }

    @gl.public.view
    def get_leaderboard(self, top_n: int = 10) -> list:
        """Return top N players by score."""
        result = []
        for addr in self.leaderboard[:top_n]:
            if addr in self.player_scores:
                s = self.player_scores[addr]
                result.append({
                    "address": addr,
                    "total_points": s.total_points,
                    "rank_title": s.rank_title,
                    "words_found_count": len(s.words_found),
                    "has_pangram": s.has_pangram,
                })
        return result

    @gl.public.view
    def get_game_stats(self) -> dict:
        """Return overall game statistics."""
        return {
            "round_number": self.round_number,
            "total_players": self.total_players,
            "total_words_discovered": len(list(self.all_found_words.keys())),
        }

    @gl.public.view
    def get_found_words_global(self) -> list:
        """Return all words discovered by any player this round."""
        return list(self.all_found_words.keys())

    # ------------------------------------------------------------------ #
    #  Public WRITE methods                                                #
    # ------------------------------------------------------------------ #

    @gl.public.write
    def submit_word(self, word: str) -> dict:
        """
        Submit a word guess. The LLM validates whether it's a real word
        that follows the puzzle rules.

        Returns a dict with:
          - accepted (bool)
          - points_earned (int)
          - definition (str)
          - is_pangram (bool)
          - message (str)
        """
        player = gl.message.sender_address
        word = word.strip().lower()

        if len(word) < 4:
            return {"accepted": False, "points_earned": 0, "definition": "",
                    "is_pangram": False, "message": "Words must be at least 4 letters."}

        center = self.current_round.center_letter.lower()
        if center not in word:
            return {"accepted": False, "points_earned": 0, "definition": "",
                    "is_pangram": False,
                    "message": f'Word must contain the center letter "{center.upper()}".'}

        all_letters = set(
            [self.current_round.center_letter.lower()]
            + [l.lower() for l in self.current_round.outer_letters]
        )
        for ch in word:
            if ch not in all_letters:
                return {"accepted": False, "points_earned": 0, "definition": "",
                        "is_pangram": False,
                        "message": f'Letter "{ch.upper()}" is not in the puzzle.'}

        # Initialise player record if new
        if player not in self.player_scores:
            self.player_scores[player] = PlayerScore(
                address=player,
                total_points=0,
                words_found=[],
                has_pangram=False,
                rank_title="Beginner",
            )
            self.total_players += 1

        player_score = self.player_scores[player]

        if word in player_score.words_found:
            return {"accepted": False, "points_earned": 0, "definition": "",
                    "is_pangram": False, "message": "You already found that word!"}

        # AI validation
        is_valid = self._validate_word_with_ai(
            word,
            self.current_round.center_letter,
            self.current_round.outer_letters,
        )

        if not is_valid:
            return {"accepted": False, "points_earned": 0, "definition": "",
                    "is_pangram": False, "message": f'"{word}" is not a valid word.'}

        # Score the word
        all_letters_list = (
            [self.current_round.center_letter]
            + self.current_round.outer_letters
        )
        points = self._calculate_word_points(word, all_letters_list)
        is_pangram = word.lower() in [p.lower() for p in self.current_round.pangrams]
        definition = self._get_word_definition(word)

        # Update state
        player_score.words_found.append(word)
        player_score.total_points += points
        if is_pangram:
            player_score.has_pangram = True
        player_score.rank_title = self._get_rank(player_score.total_points)
        self.player_scores[player] = player_score

        # Track globally
        if word not in self.all_found_words:
            self.all_found_words[word] = []
        finders = self.all_found_words[word]
        finders.append(player)
        self.all_found_words[word] = finders

        self._update_leaderboard(player)

        return {
            "accepted": True,
            "points_earned": points,
            "definition": definition,
            "is_pangram": is_pangram,
            "message": "🎉 Pangram!" if is_pangram else f"+{points} points!",
        }

    @gl.public.write
    def advance_round(self) -> dict:
        """
        Generate a new puzzle round. Resets all player word lists
        but preserves cumulative scores across rounds.
        """
        self.all_found_words = TreeMap()

        # Preserve cumulative scores, reset per-round words
        for addr in list(self.player_scores.keys()):
            score = self.player_scores[addr]
            score.words_found = []
            score.has_pangram = False
            self.player_scores[addr] = score

        self.leaderboard = []
        self._generate_new_round()

        return {
            "round_number": self.round_number,
            "center_letter": self.current_round.center_letter,
            "outer_letters": self.current_round.outer_letters,
            "theme": self.current_round.theme,
        }

    @gl.public.write
    def get_hint(self, letter_start: str) -> str:
        """
        Ask the AI for a hint: how many valid words start with `letter_start`.
        Non-deterministic — uses LLM.
        """
        letter_start = letter_start.strip().upper()
        all_letters = (
            [self.current_round.center_letter]
            + self.current_round.outer_letters
        )

        def _nondet_hint():
            prompt = f"""Spelling Bee puzzle.
Letters available: {", ".join(all_letters)}
Center letter (required in every word): {self.current_round.center_letter}

How many common English words of 4+ letters:
- start with "{letter_start}"
- contain the center letter
- use only the available letters

Reply with ONLY a number."""
            return gl.exec_prompt(prompt)

        count = gl.eq_principle_prompt_comparative(_nondet_hint).strip()
        return f"There are approximately {count} words starting with {letter_start}."
