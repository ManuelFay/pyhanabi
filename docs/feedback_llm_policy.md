# Feedback LLM Hanabi Policy

HANABI STRATEGY POLICY

You must choose moves using only legally available information. Do not assume the hidden identity of your own cards unless it follows from clues and public information.

Before selecting a move, compute:
1. Board next-needed ranks:
   - A card is playable only if its rank is exactly board[color] + 1.
   - A rank-1 card is NOT playable in a color whose 1 is already played.
   - A rank-2 card is NOT playable in a color already at 2 or higher.

2. For each own card, classify it:
   - CERTAIN PLAY: every possible identity is currently playable.
   - POSSIBLE PLAY: at least one possible identity is playable, but not all.
   - SAFE DISCARD: every possible identity is already played, duplicate, or not needed.
   - DANGEROUS DISCARD: any possible identity could be needed for progression, is a 5, or is the last/critical copy.
   - CRITICAL: any known or possible 5, any last copy, or any card needed for a lagging color.

3. For each possible clue, classify its intent:
   - PLAY clue: clearly identifies one or more immediately playable cards.
   - SAVE clue: protects a 5 or last critical copy.
   - DISCARD clue: identifies cards safely discardable.
   - SETUP clue: connects to a near-future play.
   - LOW-VALUE clue: gives information but does not change partner’s next action.

Decision priority:
1. Play a CERTAIN PLAY.
2. Give a PLAY clue that lets partner make an immediate safe play.
3. Give a SAVE clue for an unprotected 5 or last critical copy.
4. Give a high-quality SETUP clue only if it clearly enables a near-future play.
5. Discard a SAFE DISCARD to regain a hint.
6. Give a DISCARD clue if no safe discard is known.
7. Only make a probabilistic play when there is no safe discard/clue and the expected value clearly outweighs the bomb risk.

Hard rules:
- Never discard a known 5 unless it is provably dead.
- Never discard a card that could be a needed 5 or last copy.
- Never treat “rank 1” as playable without checking the color stack.
- Never treat “rank 2” as playable without checking whether that color is exactly at 1.
- Do not repeat a clue unless it adds new actionable information.
- Do not spend the last hint on redundant or speculative information.
- Do not give color clues that touch both playable and unplayable cards unless the intended interpretation is unambiguous.
- After receiving a clear play clue, prefer playing the clued card before giving unrelated clues.
- With 0 hints, default to safe discard. Do not blind-play a POSSIBLE PLAY unless the card is effectively certain or the game state demands risk.
- With 1 life remaining, only play cards that are certain.

Before finalizing the move, run this self-check:
- Is my chosen play guaranteed playable?
- Is my chosen discard guaranteed safe?
- Does my clue create a specific action for partner?
- Am I repeating information partner already had?
- Could this clue accidentally imply the wrong card is playable?
- Am I preserving 5s, last copies, and lagging-color progression?

Compact rules:
- A play is legal-strategic only when the card is certain playable, not merely plausible.
- A discard is safe only when every possible identity is disposable.
- A clue is good only when it changes partner’s next action.
- Repeated clues are bad unless they disambiguate a new action.
- Lagging colors make unknown low cards dangerous, not discardable.
- Known 5s are protected cards, never discard candidates.

Structured explanation output (embed in `strategy_feedback`):

```json
{
  "move": "...",
  "intent": "PLAY | SAVE | DISCARD | SETUP | SAFE_DISCARD | RISK_PLAY",
  "target_cards": [0, 2],
  "why_not_play": "...",
  "why_not_discard": "...",
  "risk_level": "none | low | medium | high",
  "is_redundant_clue": false,
  "is_card_certain_playable": true,
  "is_card_certain_discardable": false
}
```
