# 🐝 GenLayer Spelling Bee

An on-chain Spelling Bee game powered by **GenLayer Intelligent Contracts**.  
Words, definitions, and scoring are validated through GenLayer's **Optimistic Democracy** AI consensus — no centralized backend required.

[![CI](https://github.com/YOUR_ORG/genlayer-spelling-bee/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_ORG/genlayer-spelling-bee/actions/workflows/ci.yml)

---

## 🎮 Live Demo

| Resource | URL |
|---|---|
| Frontend | https://genspellingbee.lovable.app/ |
| Contract (Testnet) | `0x63Bfa1201F0b4e95bc9f7f1473c8cB57d2afa0Ac` |
| GenLayer Studio | https://studio.genlayer.com/?import-contract=0x63Bfa1201F0b4e95bc9f7f1473c8cB57d2afa0Ac |

---

## ✨ Features

- **AI-generated puzzles** — each round's 7-letter honeycomb is produced by an LLM and validated through consensus
- **AI word validation** — the LLM judges whether a submitted word is real and follows the puzzle rules
- **AI definitions** — every accepted word comes with a fresh definition
- **On-chain scoring** — points and leaderboard are stored in the contract state
- **Rank progression** — Beginner → Genius, mirroring the classic game
- **Pangram bonuses** — extra points for words that use all 7 letters
- **Hints** — ask the contract how many words start with a given letter

---

## 📁 Repository Structure

```
genlayer-spelling-bee/
├── contracts/
│   └── spelling_bee.py          # GenLayer Intelligent Contract (Python)
├── tests/
│   └── test_spelling_bee.py     # pytest integration tests
├── scripts/
│   ├── deploy.py                # Deployment script (genlayer-py)
│   └── interact.py              # CLI interaction script
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── components/
│       │   ├── HoneycombGrid.jsx
│       │   ├── WordInput.jsx
│       │   └── index.jsx        # ScorePanel, FoundWords, Leaderboard, Toast
│       ├── hooks/
│       │   └── useSpellingBeeContract.js
│       └── lib/
│           └── utils.js
├── .github/workflows/
│   └── ci.yml                   # Lint + test + build
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

---

### 1 · Run the Frontend Locally

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

The frontend points to the live testnet contract by default. You only need a MetaMask wallet with some testnet GLY to submit words.

---

### 2 · Run Contract Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Tests use `genlayer-test` in **direct / simulation mode** so they run without a live node. LLM calls can be mocked via `runner.mock_nondet(...)`.

---

### 3 · Lint the Contract

```bash
pip install genlayer-cli
genlayer lint contracts/spelling_bee.py
```

---

### 4 · Deploy Your Own Contract

```bash
# Set environment variables
export PRIVATE_KEY=0xYOUR_PRIVATE_KEY
export NETWORK=testnet   # or localnet

pip install genlayer-py
python scripts/deploy.py
```

After deployment, update `CONTRACT_ADDRESS` in `frontend/src/App.jsx`.

---

### 5 · Interact via CLI

```bash
export PRIVATE_KEY=0xYOUR_PRIVATE_KEY
export CONTRACT_ADDRESS=0xYOUR_CONTRACT

# View current puzzle
python scripts/interact.py --action get_puzzle

# Submit a word
python scripts/interact.py --action submit_word --word "crane"

# Check leaderboard
python scripts/interact.py --action leaderboard

# View game stats
python scripts/interact.py --action stats
```

---

## 🧠 How It Works

### GenLayer Intelligent Contract

The contract (`contracts/spelling_bee.py`) is written in Python and deployed to the GenLayer network. It uses two GenLayer-specific primitives:

#### `gl.exec_prompt(prompt)` — LLM call
Calls an LLM inside a **non-deterministic block**. Multiple validators each run the LLM independently.

#### `gl.eq_principle_prompt_comparative(fn)` — Consensus
Validators compare their LLM outputs and reach consensus if results are *equivalent enough* — even if not byte-identical. This is GenLayer's **Equivalence Principle**.

```python
def _validate_word_with_ai(self, word, center, letters):
    def _nondet():
        prompt = f'Is "{word}" a valid Spelling Bee word? Reply "valid" or "invalid".'
        return gl.exec_prompt(prompt)

    verdict = gl.eq_principle_prompt_comparative(_nondet)
    return verdict.strip().lower() == "valid"
```

### Scoring

| Word length | Points |
|---|---|
| 4 letters | 1 |
| 5+ letters | = length |
| Pangram bonus | +7 |

### Rank Ladder

Beginner → Good Start → Moving Up → Good → Solid → Nice → Great → Amazing → **Genius**

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Intelligent Contract | Python · GenLayer SDK (`py-genlayer`) |
| Blockchain | GenLayer Testnet (Bradbury) |
| Frontend | React 18 · Vite · Tailwind CSS |
| Web3 SDK | genlayer-js · viem |
| Testing | pytest · genlayer-test |
| CI | GitHub Actions |

---

## 🔧 Environment Variables

| Variable | Description |
|---|---|
| `PRIVATE_KEY` | Deployer / caller private key |
| `CONTRACT_ADDRESS` | Deployed contract address |
| `NETWORK` | `testnet` or `localnet` |

---

## 📖 GenLayer Resources

- [GenLayer Documentation](https://docs.genlayer.com)
- [Intelligent Contracts Guide](https://docs.genlayer.com/developers/intelligent-contracts/introduction)
- [GenLayer JS SDK](https://docs.genlayer.com/developers/decentralized-applications/genlayer-js)
- [GenLayer Studio](https://studio.genlayer.com)
- [Boilerplate Repo](https://github.com/genlayerlabs/genlayer-boilerplate)

---

## 📄 License

MIT
