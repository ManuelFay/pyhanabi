# Strategy Rationales (Natural Language Overview)

This document explains the built-in Hanabi strategies in plain language: what each one optimizes for, what information it considers, and how it tends to decide actions.

## Shared context (applies to all strategies)

Every strategy receives:
- visible hands (`hands`),
- belief/knowledge tensors (`knowledge`),
- discard pile (`trash`),
- played cards (`played`),
- current fireworks board (`board`),
- currently legal moves (`valid_actions`),
- remaining hint tokens (`hints`).

Most strategies balance three core goals:
1. **Play safely** when confidence is high.
2. **Discard safely** when likely harmless and hints are needed.
3. **Use hints intentionally** to shape partner behavior.

---

## `random` (`Player`)

**Rationale:** Baseline behavior for benchmarking.

**What it considers:** Only legal actions (no deeper reasoning).

**Decision style:** Uniform random choice among valid actions.

**Tradeoff:** Very simple and cheap; weak score quality.

---

## `inner` (`InnerStatePlayer`)

**Rationale:** Use only own local uncertainty structure and direct play/discard checks.

**What it considers:**
- set of cards each own card could be (`get_possible` over own knowledge),
- immediate playability/discardability of those possibilities,
- partner visible hand for opportunistic hints.

**Decision style (roughly):**
1. Play a card if all possibilities are currently playable.
2. Else discard a card if all possibilities are safely discardable.
3. Else hint partner about a currently playable partner card (if hints exist).
4. Else pick other simple hints; fallback to discard.

**Tradeoff:** Fast and pragmatic, but less socially strategic.

---

## `outer` (`OuterStatePlayer`)

**Rationale:** Build explicit state about previously encoded hints and use partner-facing structure.

**What it considers:**
- own/partner possibilities,
- board progression,
- tracked hint metadata to preserve/shift conventions,
- available hint tokens.

**Decision style:** Similar safety-first flow (safe play, safe discard, then hinting) but with stronger partner-modeling and hint bookkeeping than `inner`.

**Tradeoff:** Better coordination than simple heuristics; still approximate.

---

## `self` (`SelfRecognitionPlayer`)

**Rationale:** Recursive reasoning (“what would I do if I were my partner?”) to decode hint intent.

**What it considers:**
- partner model class (`other`) used for self-recognition,
- generated candidate hidden hands consistent with beliefs,
- inferred hint semantics from simulated partner decisions,
- timing/convention helpers and board urgency.

**Decision style:**
- Simulate partner policy under plausible hidden states,
- infer which hints/actions best explain observed behavior,
- choose actions that align with inferred intent while preserving safety.

**Tradeoff:** Much heavier compute cost; can be slow but often more coordinated.

---

## `timed` (`TimedPlayer`)

**Rationale:** Encode intent through coarse timing channels / delay buckets.

**What it considers:**
- elapsed time since prior event,
- bucketized delay interpreted as play/discard index,
- partner hand priorities.

**Decision style:**
- derive index/intent from timing slice,
- map timing to play/discard action,
- optionally hint if careful mode requires preserving tempo semantics.

**Tradeoff:** Experimental signaling mechanism; brittle but interesting for protocol experiments.

---

## `intentional` (`IntentionalPlayer`)

**Rationale:** Evaluate hints by predicted downstream partner actions.

**What it considers:**
- explicit intention labels (play/discard/keep),
- hypothetical post-hint knowledge states,
- whether a hint is valid and informative,
- expected utility of future partner actions.

**Decision style:**
1. Compute intended actions for partner cards.
2. Score candidate color/number hints via forward simulation (`pretend`).
3. Choose high-value valid hints when possible.
4. Otherwise choose safe play/discard according to confidence.

**Tradeoff:** Better communicative quality than pure heuristics; more computation.

---

## `full` (`SelfIntentionalPlayer`)

**Rationale:** Combine self-recognition and intentional hint planning into one richer policy.

**What it considers:**
- both explicit intention planning and recursive interpretation,
- own uncertainty and partner uncertainty,
- board urgency, discard risk, hint economy.

**Decision style:**
- run intention-aware evaluations,
- integrate with self-model assumptions,
- prefer moves that maximize coordinated expected value.

**Tradeoff:** Stronger coordination potential, higher runtime cost and complexity.

---

## `sample` (`SamplingRecognitionPlayer`)

**Rationale:** Approximate expensive recursive reasoning by sampling plausible hands.

**What it considers:**
- sampled hidden-hand hypotheses (`sample_hand`),
- partner model behavior across samples,
- aggregate action quality under uncertainty.

**Decision style:**
- repeatedly sample consistent hidden states,
- evaluate candidate actions/hints under samples,
- pick robust action under sampled posterior.

**Tradeoff:** More scalable than exhaustive self-recognition; still stochastic and potentially noisy.

---

## `fully_intentional` (`FullyIntentionalPlayer`)

**Rationale:** Variant of strong intentional planning with broader internal scoring logic.

**What it considers:**
- intention consistency,
- knowledge transitions after hints,
- risk/reward over play/discard/hint trajectories.

**Decision style:**
- score candidate communicative actions with richer internal logic,
- choose action maximizing expected collaborative progress.

**Tradeoff:** High sophistication and high complexity; mainly useful for advanced experiments.

---


## `prior` (`PrioritizedIntentionalPlayer`)

**Rationale:** Fast, rule-compliant deterministic priors with explicit hint-following conventions.

**What it considers:**
- own per-card possibility sets from public knowledge,
- whether a just-received hint touched cards that are certainly/potentially playable,
- partner playable cards plus hint quality (narrowness, newest-touched alignment, ambiguity risk),
- discard criticality from board + trash counts (protect last copies, especially 5s).

**Decision style:**
1. **Fresh-hint resolution:** if a received hint touched cards, play the newest touched card that is certainly playable; otherwise the newest touched card that is potentially playable.
2. **Guaranteed self-play:** if any own card is certainly playable, play one (prefers highest implied rank).
3. **Tempo-hint prior:** if no play exists, hint partner about currently playable cards using scoring that favors narrow, singleton, newest-aligned, low-ambiguity hints.
4. **Safe/low-risk discard:** if still blocked, prefer guaranteed-safe discard (when hints are not full), else use risk-ranked discard fallback.

**Tradeoff:** Extremely fast and deterministic, with strong mirror coordination when partner follows newest-touched hint conventions; less robust with mismatched partner conventions.

---

## Practical guidance

- For **fast baselines**: use `random`, `inner`, `outer`, `prior`.
- For **communication-heavy experiments**: use `intentional`, `full`, `sample`.
- For **protocol/timing experiments**: use `timed`.
- For **deep recursive behavior**: use `self` (expect longer runtimes).
