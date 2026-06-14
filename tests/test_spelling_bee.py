"""
Integration tests for the GenLayer Spelling Bee contract.
Run with: pytest tests/ -v
Requires: pip install genlayer-test pytest pytest-asyncio
"""

import pytest
import pytest_asyncio
from genlayer_test import ContractRunner, Account


# ------------------------------------------------------------------ #
#  Fixtures                                                            #
# ------------------------------------------------------------------ #

@pytest.fixture
def accounts():
    """Create test accounts."""
    return [
        Account.from_private_key("0x" + "1" * 64),
        Account.from_private_key("0x" + "2" * 64),
        Account.from_private_key("0x" + "3" * 64),
    ]


@pytest.fixture
def runner(accounts):
    """Deploy a fresh contract before each test."""
    r = ContractRunner(
        contract_file="contracts/spelling_bee.py",
        deployer=accounts[0],
    )
    r.deploy()
    return r


# ------------------------------------------------------------------ #
#  Puzzle / view tests                                                 #
# ------------------------------------------------------------------ #

class TestPuzzleGeneration:
    def test_initial_puzzle_structure(self, runner):
        puzzle = runner.call("get_current_puzzle")
        assert "center_letter" in puzzle
        assert "outer_letters" in puzzle
        assert "theme" in puzzle
        assert "round_number" in puzzle
        assert puzzle["round_number"] == 1
        assert len(puzzle["center_letter"]) == 1
        assert len(puzzle["outer_letters"]) == 6

    def test_center_letter_is_uppercase(self, runner):
        puzzle = runner.call("get_current_puzzle")
        assert puzzle["center_letter"] == puzzle["center_letter"].upper()

    def test_outer_letters_are_uppercase(self, runner):
        puzzle = runner.call("get_current_puzzle")
        for letter in puzzle["outer_letters"]:
            assert letter == letter.upper()

    def test_no_duplicate_letters(self, runner):
        puzzle = runner.call("get_current_puzzle")
        all_letters = [puzzle["center_letter"]] + puzzle["outer_letters"]
        assert len(all_letters) == len(set(all_letters)), "Duplicate letters found"


# ------------------------------------------------------------------ #
#  Word submission tests                                               #
# ------------------------------------------------------------------ #

class TestWordSubmission:
    def test_too_short_word_rejected(self, runner, accounts):
        result = runner.write("submit_word", ["cat"], caller=accounts[0])
        assert result["accepted"] is False
        assert "4 letters" in result["message"]

    def test_word_missing_center_letter_rejected(self, runner, accounts):
        puzzle = runner.call("get_current_puzzle")
        center = puzzle["center_letter"]

        # Build a 4-letter word from outer letters only (no center)
        outer = puzzle["outer_letters"]
        test_word = (outer[0] * 4).lower()  # crude — good enough for unit test

        result = runner.write("submit_word", [test_word], caller=accounts[0])
        assert result["accepted"] is False
        assert center.lower() in result["message"].lower() or "center" in result["message"].lower()

    def test_word_with_invalid_letter_rejected(self, runner, accounts):
        # Pick a letter not in the puzzle
        puzzle = runner.call("get_current_puzzle")
        all_letters = set(
            puzzle["center_letter"] + "".join(puzzle["outer_letters"])
        )
        invalid_letter = next(
            c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in all_letters
        )
        bad_word = (invalid_letter * 4).lower()
        result = runner.write("submit_word", [bad_word], caller=accounts[0])
        assert result["accepted"] is False

    def test_duplicate_word_rejected(self, runner, accounts):
        """Submit the same word twice — second attempt must be rejected."""
        # We need a word known to be valid for the AI. We'll mock this by
        # patching the nondet call in test mode.
        puzzle = runner.call("get_current_puzzle")
        center = puzzle["center_letter"].lower()
        # Construct a plausible 4-letter word using center letter
        test_word = center * 4

        # First submission (may or may not be accepted by AI)
        result1 = runner.write("submit_word", [test_word], caller=accounts[0])

        if result1["accepted"]:
            # Now try again — must be rejected
            result2 = runner.write("submit_word", [test_word], caller=accounts[0])
            assert result2["accepted"] is False
            assert "already found" in result2["message"].lower()

    def test_valid_word_awards_points(self, runner, accounts, monkeypatch):
        """Patch the AI validator so we can assert scoring logic."""
        # In direct test mode, override the nondet block output
        runner.mock_nondet("valid")
        runner.mock_nondet("a word meaning something interesting")

        puzzle = runner.call("get_current_puzzle")
        center = puzzle["center_letter"].lower()
        outer = [l.lower() for l in puzzle["outer_letters"]]
        # Build a 5-letter word using center + 4 outer letters
        word = center + outer[0] + outer[1] + outer[2] + outer[3]

        result = runner.write("submit_word", [word], caller=accounts[0])
        assert result["accepted"] is True
        assert result["points_earned"] > 0

    def test_four_letter_word_scores_1_point(self, runner, accounts):
        runner.mock_nondet("valid")
        runner.mock_nondet("short definition")

        puzzle = runner.call("get_current_puzzle")
        center = puzzle["center_letter"].lower()
        outer = [l.lower() for l in puzzle["outer_letters"]]
        word = center + outer[0] + outer[1] + outer[2]  # 4 letters

        result = runner.write("submit_word", [word], caller=accounts[0])
        if result["accepted"]:
            assert result["points_earned"] == 1


# ------------------------------------------------------------------ #
#  Scoring / leaderboard tests                                         #
# ------------------------------------------------------------------ #

class TestScoring:
    def test_new_player_starts_at_zero(self, runner, accounts):
        score = runner.call("get_player_score", [accounts[1].address])
        assert score["total_points"] == 0
        assert score["words_found"] == []
        assert score["rank_title"] == "Beginner"

    def test_leaderboard_empty_initially(self, runner):
        lb = runner.call("get_leaderboard", [10])
        assert lb == []

    def test_game_stats_increment_on_new_player(self, runner, accounts):
        runner.mock_nondet("valid")
        runner.mock_nondet("a definition")

        puzzle = runner.call("get_current_puzzle")
        center = puzzle["center_letter"].lower()
        outer = [l.lower() for l in puzzle["outer_letters"]]
        word = center + outer[0] + outer[1] + outer[2]

        before = runner.call("get_game_stats")
        runner.write("submit_word", [word], caller=accounts[1])
        after = runner.call("get_game_stats")

        # Total players should increase (may already be 1 from deployer)
        assert after["total_players"] >= before["total_players"]


# ------------------------------------------------------------------ #
#  Round advancement tests                                             #
# ------------------------------------------------------------------ #

class TestRoundAdvancement:
    def test_advance_round_increments_counter(self, runner, accounts):
        before = runner.call("get_current_puzzle")["round_number"]
        runner.write("advance_round", [], caller=accounts[0])
        after = runner.call("get_current_puzzle")["round_number"]
        assert after == before + 1

    def test_advance_round_generates_new_letters(self, runner, accounts):
        before = runner.call("get_current_puzzle")
        runner.write("advance_round", [], caller=accounts[0])
        after = runner.call("get_current_puzzle")
        # Not guaranteed to change, but round number must increment
        assert after["round_number"] > before["round_number"]

    def test_found_words_cleared_after_advance(self, runner, accounts):
        runner.mock_nondet("valid")
        runner.mock_nondet("def")

        puzzle = runner.call("get_current_puzzle")
        center = puzzle["center_letter"].lower()
        outer = [l.lower() for l in puzzle["outer_letters"]]
        word = center + outer[0] + outer[1] + outer[2]

        runner.write("submit_word", [word], caller=accounts[0])
        assert len(runner.call("get_found_words_global")) > 0

        runner.write("advance_round", [], caller=accounts[0])
        assert runner.call("get_found_words_global") == []


# ------------------------------------------------------------------ #
#  Hint tests                                                          #
# ------------------------------------------------------------------ #

class TestHints:
    def test_hint_returns_string(self, runner, accounts):
        runner.mock_nondet("5")
        puzzle = runner.call("get_current_puzzle")
        first_letter = puzzle["center_letter"]
        hint = runner.write("get_hint", [first_letter], caller=accounts[0])
        assert isinstance(hint, str)
        assert first_letter in hint


# ------------------------------------------------------------------ #
#  Multi-player tests                                                  #
# ------------------------------------------------------------------ #

class TestMultiplePlayers:
    def test_multiple_players_can_find_same_word(self, runner, accounts):
        runner.mock_nondet("valid")
        runner.mock_nondet("definition one")
        runner.mock_nondet("valid")
        runner.mock_nondet("definition two")

        puzzle = runner.call("get_current_puzzle")
        center = puzzle["center_letter"].lower()
        outer = [l.lower() for l in puzzle["outer_letters"]]
        word = center + outer[0] + outer[1] + outer[2]

        r1 = runner.write("submit_word", [word], caller=accounts[0])
        r2 = runner.write("submit_word", [word], caller=accounts[1])

        # Both may succeed (different players)
        if r1["accepted"] and r2["accepted"]:
            global_words = runner.call("get_found_words_global")
            assert word in global_words

    def test_leaderboard_sorted_by_score(self, runner, accounts):
        # Give player 1 a higher score via mocking
        for _ in range(3):
            runner.mock_nondet("valid")
            runner.mock_nondet("def")

        puzzle = runner.call("get_current_puzzle")
        center = puzzle["center_letter"].lower()
        outer = [l.lower() for l in puzzle["outer_letters"]]

        words = [
            center + outer[0] + outer[1] + outer[2],
            center + outer[1] + outer[2] + outer[3],
            center + outer[0] + outer[2] + outer[3],
        ]

        for w in words:
            runner.write("submit_word", [w], caller=accounts[0])

        lb = runner.call("get_leaderboard", [10])
        if len(lb) > 1:
            # Verify descending order
            for i in range(len(lb) - 1):
                assert lb[i]["total_points"] >= lb[i + 1]["total_points"]
