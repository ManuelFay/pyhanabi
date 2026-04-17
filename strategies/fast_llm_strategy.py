"""Fast LLM strategy with compact state payload for cheaper/faster reasoning."""

from .llm_strategy import LLMStrategy
from hanabi import COLORNAMES


class FastLLMStrategy(LLMStrategy):
    """Compact-state variant of LLMStrategy.

    Sends only essential state slices (plus short history) to reduce token usage.
    """

    def _serialize_state(self, nr, hands, knowledge, trash, played, board, hints, legal_actions):
        board_state = {COLORNAMES[col]: rank for (col, rank) in board}
        next_playable = {color_name: rank + 1 for color_name, rank in board_state.items()}

        visible_hands = []
        for pnr, hand in enumerate(hands):
            if pnr == nr:
                visible_hands.append({"player": pnr, "cards": "hidden_to_current_player"})
                continue
            visible_hands.append(
                {
                    "player": pnr,
                    "cards": [
                        {
                            "card_index": idx,
                            "color": COLORNAMES[col],
                            "rank": rank,
                        }
                        for idx, (col, rank) in enumerate(hand)
                    ],
                }
            )

        own_knowledge_summary = []
        for card_idx, card_knowledge in enumerate(knowledge[nr]):
            candidates = []
            total = sum([sum(col_counts) for col_counts in card_knowledge]) or 1
            for col in range(len(card_knowledge)):
                for rank_idx, count in enumerate(card_knowledge[col]):
                    if count > 0:
                        candidates.append(
                            {
                                "color": COLORNAMES[col],
                                "rank": rank_idx + 1,
                                "p": round(count / float(total), 4),
                            }
                        )
            candidates.sort(key=lambda x: (-x["p"], x["color"], x["rank"]))
            own_knowledge_summary.append(
                {
                    "card_index": card_idx,
                    "top_candidates": candidates[:3],
                }
            )

        compact_legal_actions = []
        for action in legal_actions:
            compact_legal_actions.append(
                {
                    "action_id": action["action_id"],
                    "type": action["type"],
                    "pnr": action["pnr"],
                    "col": action["col"],
                    "num": action["num"],
                    "cnr": action["cnr"],
                    "canonical": action["canonical"],
                }
            )

        return {
            "current_player": nr,
            "hints": hints,
            "board": board_state,
            "next_playable_rank_by_color": next_playable,
            "visible_hands": visible_hands,
            "own_knowledge_summary": own_knowledge_summary,
            "recent_discarded_cards": trash[-8:],
            "recent_played_cards": played[-8:],
            "legal_actions": compact_legal_actions,
        }
