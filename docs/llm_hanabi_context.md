# Hanabi LLM Context Pack (v1)

This document is the canonical context for LLM-based Hanabi strategies in this repository.
It explains:

1. Standard Hanabi rules (the game model used by this engine)
2. How this engine encodes game state for an LLM
3. How this engine encodes legal actions and expected model output

---

## 1) Hanabi Rules (standard/cooperative)

Hanabi is a **cooperative**, imperfect-information card game.

### Goal
Build 5 color stacks in ascending order from 1 to 5 for maximum score **25**.

### Deck
- Colors: 5 (green, yellow, white, blue, red)
- Ranks per color:
  - three 1s
  - two 2s
  - two 3s
  - two 4s
  - one 5

### Visibility and information
- You can see **other players' cards**, but not your own.
- Players share information by giving hints.

### Tokens / resources
- **Hint tokens**: start at 8 (max 8).
  - Giving a hint spends 1 token.
  - Discarding a card restores 1 token (up to max).
  - Successfully playing a 5 also restores 1 token (up to max).
- **Fuse tokens / strikes**: start at 3.
  - Misplaying a card loses 1 strike.
  - Game ends immediately at 0 strikes.

### Turn actions
On your turn choose exactly one:
1. **Play** one of your own cards.
2. **Discard** one of your own cards.
3. **Hint color** to another player (all cards of that color in their hand).
4. **Hint number** to another player (all cards of that rank in their hand).

### Play outcomes
- If played card is exactly next needed rank on its color stack: success and card is added to board.
- Otherwise: misplay, card goes to trash/discard pile, lose one strike.

### End of game
- Immediate end on 0 strikes.
- Also ends after deck empties and each player receives final turns (engine handles this internally).
- Score is sum of top ranks on all 5 color stacks.

---

## 2) Engine State Encoding Given to LLM

The LLM strategy serializes a JSON payload containing a `state` object with the following fields.

### Top-level state keys
- `current_player` (`int`): index of acting player.
- `hints` (`int`): current hint tokens.
- `visible_hands` (`list`): hands as seen by acting player.
  - Acting player's own entry is typically `[]`.
  - Other players' entries are lists of cards encoded as `[color_index, rank]`.
- `knowledge` (`list`): per-player, per-card possibility tables maintained by engine.
- `trash` (`list`): discarded/misplayed cards, each as `[color_index, rank]`.
- `played` (`list`): successfully played cards, each as `[color_index, rank]`.
- `board` (`object`): map from color name to highest successfully played rank for that color.
  - Example: `{ "green": 2, "yellow": 0, "white": 1, "blue": 0, "red": 3 }`
- `legal_actions` (`list`): fully enumerated legal actions for this turn.

### Color encoding
- `0 = green`
- `1 = yellow`
- `2 = white`
- `3 = blue`
- `4 = red`

### Card encoding
Cards are represented as `[color_index, rank]`, where rank is `1..5`.

### Knowledge encoding (high level)
For each unknown card, `knowledge` contains counts over possible identities by color and rank.
A zero means impossible; positive means still possible.

---

## 3) Legal Action Encoding + Required Output Protocol

The strategy computes legal actions from engine state and sends them explicitly.

Each `legal_actions[i]` object has:
- `action_id` (`int`): index in `legal_actions` list.
- `type` (`str`): one of:
  - `"hint_color"`
  - `"hint_number"`
  - `"play"`
  - `"discard"`
- `pnr` (`int|null`): target player index for hint actions, otherwise `null`.
- `col` (`int|null`): hinted color for `hint_color`, otherwise `null`.
- `num` (`int|null`): hinted rank for `hint_number`, otherwise `null`.
- `cnr` (`int|null`): acting player's card index for `play`/`discard`, otherwise `null`.
- `canonical` (`str`): human-readable normalized action string.

### Required model response shape
The model must return strict JSON with this exact shape:

```json
{
  "selected_action_id": 3,
  "selected_action": {
    "type": "play",
    "pnr": null,
    "col": null,
    "num": null,
    "cnr": 1,
    "canonical": "play(card_index=1)"
  },
  "reasoning": "short explanation"
}
```

### Safety checks performed by strategy
The engine strategy rejects outputs unless all are true:
1. `selected_action_id` is an integer.
2. `selected_action_id` indexes an existing element of `legal_actions`.
3. `selected_action` includes all required keys.
4. Every key in `selected_action` exactly matches the corresponding chosen legal action object.

If any check fails, strategy raises a protocol error.

---

## 4) Guidance for future prompt optimization

To iterate on prompts safely:
- Keep this file as canonical game/protocol context.
- Adjust style or reasoning instructions separately from protocol requirements.
- Prefer changing prompt framing without changing JSON schema.
- If schema changes are needed, version the protocol name and update tests.
