# CS329A reasoning-core — verified measured results (REAL Qwen3-0.6B runs)

All numbers below were measured by running a REAL small reasoning model — **Qwen3-0.6B** (0.6
billion parameters) — on real benchmark questions, mostly **GSM8K** grade-school math word
problems, graded against the gold answer. Runs were done on a Colab T4/L4 GPU in the companion
"reasoning-from-scratch" lab. The model is small ON PURPOSE so its reasoning is visible and
imperfect. Cite these numbers verbatim; do NOT invent new ones.

## S1 — direct answer vs "thinking first" (5 probe questions)
- Direct answer: **3/5** correct. Let it think first (write a private train of thought before
  answering): **4/5** correct.
- Headline: the "how many r's in strawberry" question — answered **1** cold (wrong, 21 tokens),
  **3** when thinking first (correct, 336 tokens).
- Insight: same network, no retraining — just letting it work out loud rescues problems it fails cold.

## S2 — chain-of-thought over GSM8K (N=30 real problems, each run twice)
- Direct: **14/30**. Think-first (chain of thought): **18/30**.
- **Rescued 4** (direct wrong → thinking right), **broke 0** (none regressed).
- **12/30** thinking traces hit the 2048-token limit without settling. Avg length: direct 226 tokens
  → thinking 1449 tokens.
- Insight: thinking reliably helps a tiny model (14→18) but is not magic — it still misses 12/30 and
  rambles to the limit on the hardest ones.

## S3 — self-consistency / majority vote (N=14, K=8 sampled paths, temperature 0.9)
- One careful ("greedy") path: **6/14 = 43%**. One random sampled path (average): **39%**.
- Majority vote across 8 sampled paths: **8/14 = 57%**.
- Coverage curve — majority-vote accuracy as paths grow 1→8: **0.429, 0.429, 0.500, 0.500, 0.500,
  0.571, 0.571, 0.571** (rises then plateaus).
- Insight: one random path (39%) is noisier than the careful one (43%), but sampling many paths and
  voting jumps to 57% — and the gains flatten, so more paths eventually stop helping.

## S4 — self-refine (N=12, 3 rounds: answer, then critique-and-revise twice)
- Accuracy by round: **5 → 6 → 7 out of 12** (**42% → 50% → 58%**, +17 points).
- Every revision that changed the answer improved it: round 1 **fixed 1, broke 0**; round 2 **fixed 1,
  broke 0** (total **2 fixed, 0 broken**).
- Insight: letting the model critique and redo its own work was strictly positive here — it corrected
  mistakes without introducing new ones.

## S5 — verifiers: the SAME 25 traces graded four different ways
- exact string match: **0/25 = 0%**; "the right number appears somewhere": **16/25 = 64%**; "last
  number in the text": **10/25 = 40%**; "the final boxed answer, read carefully": **11/25 = 44%**.
- 14/25 traces ended in a clean boxed final answer.
- Insight: one model, four graders, four scores (0% / 64% / 40% / 44%). How you check the answer is a
  design decision — a lenient grader (64%) is easy to fool; the careful boxed grader (44%) is trusted
  and is the one used to grade the RL runs below.

## S6 — GRPO / naive reinforcement learning (N=20, checkpoints at steps 0/500/3000/9000)
- Accuracy (careful grader, /20): **1, 10, 3, 3** → **base 5% → peak 50% at step 500 → collapse to 15%**
  by step 3000 and stays there.
- Avg answer length (tokens): **21 → 236 → 8 → 7** (a bare guess → a worked solution → shrivelled to a
  boxed number). By step 9000 a typical answer is literally just "\boxed{540}" — right form, no reasoning.
- Insight: a plain right/wrong reward first grew real reasoning (5%→50%, 236-token solutions), then got
  reward-hacked back down to 15% — the model learned to emit a lone boxed guess that sometimes hits.

## S7 — distillation (N=20, Qwen3-0.6B student imitating DeepSeek-R1 traces, epochs 1/2/3)
- Accuracy (careful grader, /20): **2, 7, 13, 10** → **base 10% → 35% → peak 65% → 50%** (slight over-fit).
- Avg length: **1536 → 934 → 673 → 840** tokens — it never collapses; still writes ~840-token full
  solutions at the end.
- Insight: copying a strong teacher's worked solutions climbed to 65% and stayed stable — no collapse —
  unlike RL's fragile 50%-then-15%. This is why most small reasoning models are distilled.

## S8 — KL-stabilized RL: token-length collapse (N=20, naive vs regularized recipe)
- Naive (no leash): step 500 = **50%**, avg **377** tokens; step 9000 = **15%**, avg **7** tokens
  (collapsed — a whole answer is just "\boxed{48}").
- Regularized (KL leash + format reward): step 500 = **5%**, avg **1237** tokens, still writing real
  solutions (12/20 even ran past the 2048-token limit).
- Insight: same reward — the KL "leash" preserves the one thing collapse destroys. Naive shrivels to
  7-token cheats; the leashed model keeps writing 1237-token solutions. It doesn't win on accuracy yet,
  but it never degenerates. (Honest caveat: only the 500-step regularized checkpoint is released.)
