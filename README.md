# UniG2U: human ratings of generated intermediate images

This package contains the human study used in the rebuttal and revision. Three annotators independently rated the intermediate images that unified models generate in the Generate-then-Answer (GtA) protocol. Everything needed to reproduce the reported statistics is included.

## Contents

| Path | Description |
|---|---|
| `items.csv` | One row per item: model, task, document id, question, image files, and the model's GtA and Direct scores on that item. `role` marks the 207 rated items and the 3 calibration examples shown to annotators. |
| `ratings.csv` | One row per (item, annotator): fidelity and helpfulness on a 1–5 scale. 621 ratings in total (207 items × 3 annotators). |
| `raw_logs/` | The append-only logs written by the rating tool, one per annotator. When an item was rated more than once, the last entry counts. |
| `images/` | `<item>_orig.jpg` is the input image the model saw. `<item>_mid.jpg` is the intermediate image it generated; multi-step items show up to four steps tiled into one image. |
| `analysis/analyze.py` | Recomputes inter-annotator agreement and the per-model results below (`python analysis/analyze.py` from this directory; needs numpy, pandas and scipy). |

## Sample

- Models: BAGEL-7B-MoT, Ovis-U1-3B and Janus-Pro-7B, run with the benchmark's GtA protocol.
- Items: 210 were drawn with a fixed random seed (`numpy.random.default_rng(20261116)`), stratified over task groups (multi-image spatial reasoning, RealUnify, VisualPuzzles, visual spatial planning, IllusionBench, ChartQA, and the multi-step maze and sliding-puzzle tasks). The draw was made before any rating or score was inspected, and no item was filtered by correctness.
- Three of the 210 items were used as calibration examples on the instruction page and were not rated, leaving 207 rated items.

## Protocol

- Annotators saw the question, the input image and the intermediate image. Model names, the model's answer and its correctness were hidden.
- Each annotator rated all items in an independently shuffled order. Annotators did not discuss items with each other.
- Two scales:
  - **Fidelity (状态保真度):** does the intermediate preserve the scene and objects of the input and depict the state the question needs? 1 = unrelated or garbage, 3 = partly right with clear errors, 5 = fully faithful.
  - **Helpfulness (对答题的帮助):** would looking at the intermediate make answering easier or more reliable? 1 = misleading, 3 = no effect, 5 = clearly helpful.
- Calibration examples, shown on the instruction page:
  - R138 (fidelity 1, helpfulness 1)
  - R088 (fidelity 3, helpfulness 3)
  - R058 (fidelity 5, helpfulness 4)

## Results (output of `analysis/analyze.py`)

**Inter-annotator agreement**

| Scale | Krippendorff's α (ordinal) [95% CI] | Pairwise Spearman (A-B / A-C / B-C) |
|---|---|---|
| Fidelity | 0.613 [0.528, 0.685] | 0.553 / 0.615 / 0.712 |
| Helpfulness | 0.523 [0.430, 0.612] | 0.436 / 0.587 / 0.572 |

**Per model**

Mean ratings are over all rated items. Accuracies are over the items that have GtA results.

| Model | Fidelity | Helpfulness | Items with GtA results | GtA acc. | Direct acc. | GtA − Direct |
|---|---|---|---|---|---|---|
| BAGEL-7B-MoT | 3.08 | 2.70 | 67 | 0.347 | 0.313 | +0.034 |
| Ovis-U1-3B | 1.87 | 1.62 | 69 | 0.196 | 0.361 | −0.166 |
| Janus-Pro-7B | 1.40 | 1.31 | 70 | 0.193 | 0.300 | −0.107 |

The model whose intermediates are rated highest (BAGEL) is the only one that gains from GtA on these items.

One BAGEL item has no GtA score and is excluded from the accuracy columns.

## Notes

- For maze and sliding puzzle, scores are frame accuracy, the benchmark's metric for these tasks. All other tasks are scored 0/1 or with the task's own metric (see `metric` in `items.csv`).
- Annotator identities are withheld; annotators are labelled A, B and C.

## Automatic RA / AL scores

`ra_al.csv` gives the paper's RA (reasoning-to-visual alignment) and AL (answer-to-visual alignment) scores for the same items. They were produced with the paper's judge prompts (Appendix M) and GPT-5.6 as the judge; the model was asked to output only the integer score. Against the mean human fidelity rating, RA has Spearman ρ = 0.64 (95% CI [0.54, 0.72]) and quadratic-weighted κ = 0.63, comparable to the agreement among the three annotators (α = 0.61).
