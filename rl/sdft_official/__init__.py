# Self-Distillation Fine-Tuning (SDFT)
# =======================================
# Official implementation from:
#   https://github.com/idanshen/Self-Distillation
#   Paper: "Self-Distillation Enables Continual Learning" (arXiv 2601.19897)
#
# Contents:
#   distil_config.py    — DistilConfig (extends TrainingArguments)
#   distil_trainer.py   — DistilTrainer (on-policy self-distillation)
#   main.py             — Example entry point (tooluse / science datasets)
#   eval_tooluse.py     — Evaluation script for tooluse
#   data/               — Original tooluse & science datasets
#
# Custom entry point for slidegen:
#   train_slidegen.py   — Adapted training for slide function calling
