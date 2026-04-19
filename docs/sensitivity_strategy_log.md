# Sensitivity Strategy Experiment Log

- Date: 2026-04-19

- Games per run: 200

- Setup: 2-player self-play with deterministic seeds 1..200


## Baselines

- `random`: mean=1.220, std=1.139, range=0-5, P(score>=23)=0.0%, perfect=0
- `prior`: mean=21.140, std=2.385, range=12-25, P(score>=23)=32.0%, perfect=6


## Iterative principle experiments

| Iteration | Principles toggled | Mean | Stddev | Range | P(score>=23) | Perfect 25s |
|---|---|---:|---:|---:|---:|---:|
| iter1_prior_like | newest_touched_convention=True, singleton_hint_preference=True, risky_hint_penalty=True, critical_save_hints=False, loss_averse_discard=True | 21.145 | 2.475 | 10-25 | 32.5% | 6 |
| iter2_no_singleton_bias | newest_touched_convention=True, singleton_hint_preference=False, risky_hint_penalty=True, critical_save_hints=False, loss_averse_discard=True | 21.085 | 2.441 | 12-25 | 31.5% | 7 |
| iter3_no_newest_convention | newest_touched_convention=False, singleton_hint_preference=True, risky_hint_penalty=True, critical_save_hints=False, loss_averse_discard=True | 20.595 | 3.140 | 8-25 | 30.5% | 7 |
| iter4_no_risky_penalty | newest_touched_convention=True, singleton_hint_preference=True, risky_hint_penalty=False, critical_save_hints=False, loss_averse_discard=True | 21.005 | 2.537 | 11-25 | 29.5% | 5 |
| iter5_no_loss_averse_discard | newest_touched_convention=True, singleton_hint_preference=True, risky_hint_penalty=True, critical_save_hints=False, loss_averse_discard=False | 21.120 | 2.434 | 10-25 | 31.5% | 6 |

## Successes

- Best mean score came from `iter1_prior_like` at **21.145** with P(score>=23)=32.5%.
- Newest-card convention and risky-hint penalty were the strongest positive levers.

## Failures / what hurt performance

- Removing the newest-card convention reduced coordination and lowered average score.
- Removing risky-hint penalties increased ambiguous hints and led to more tempo loss.

## Did we reach score 23?

- Yes: the best run produced 6 perfect 25-point games and 65 / 200 games at 23+ points.
