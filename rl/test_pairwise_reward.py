"""Pairwise reward invariants: direction, batching, invalid model outputs."""
from types import SimpleNamespace

import pytest
import torch
from PIL import Image

from rl.rewards.aesthetic_reward import (
    PairwiseRewardModel, _evaluate_batch, reward_model_settings,
)


class PixelUtility(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.batch_sizes = []

    def forward(self, pixel_values):
        assert not torch.is_grad_enabled()
        self.batch_sizes.append(len(pixel_values))
        return SimpleNamespace(logits=pixel_values[:, 0, 0, 0].reshape(-1, 1))


def test_pairwise_scores_preserve_order_and_do_not_depend_on_batch_composition(tmp_path):
    paths = []
    for i, value in enumerate([0, 64, 128, 192, 255]):
        path = tmp_path / f"{i}.png"
        Image.new("RGB", (8, 8), (value, value, value)).save(path)
        paths.append(path)
    model = PixelUtility()
    scorer = PairwiseRewardModel(
        model=model, device=torch.device("cpu"), batch_size=2,
        transform=lambda im: torch.full((3, 2, 2), im.getpixel((0, 0))[0] / 64 - 2),
    )
    scores = _evaluate_batch(scorer, paths)
    assert model.batch_sizes == [2, 2, 1]
    assert scores == sorted(scores)
    assert all(0 < s < 1 for s in scores)
    assert scores[2] == pytest.approx(0.5)
    scorer.batch_size = 4
    assert _evaluate_batch(scorer, paths) == pytest.approx(scores)
    assert _evaluate_batch(scorer, [paths[2]]) == pytest.approx([scores[2]])
    scorer.center = 1
    assert _evaluate_batch(scorer, [paths[2]])[0] < scores[2]
    scorer.center = 0
    scorer.temperature = 2
    softer = _evaluate_batch(scorer, paths)
    assert softer[0] > scores[0] and softer[-1] < scores[-1]
    assert _evaluate_batch(scorer, []) == []
    assert scorer.last_metrics == {}


@pytest.mark.parametrize("logits,match", [
    (torch.tensor([[float("nan")]]), "non-finite raw"),
    (torch.tensor([[float("inf")]]), "non-finite raw"),
    (torch.tensor([[-float("inf")]]), "non-finite raw"),
    (torch.zeros(1, 5), "exactly one logit"),
])
def test_pairwise_rejects_invalid_outputs_before_sigmoid(tmp_path, logits, match):
    class Fixed(torch.nn.Module):
        def forward(self, pixel_values):
            return SimpleNamespace(logits=logits)
    path = tmp_path / "slide.png"
    Image.new("RGB", (8, 8)).save(path)
    scorer = PairwiseRewardModel(
        model=Fixed(), device=torch.device("cpu"),
        transform=lambda im: torch.zeros(3, 2, 2),
    )
    with pytest.raises(RuntimeError, match=match):
        _evaluate_batch(scorer, [path])


@pytest.mark.parametrize("key,value", [
    ("RL_PAIRWISE_CENTER", "nan"),
    ("RL_PAIRWISE_TEMPERATURE", "0"),
    ("RL_PAIRWISE_TEMPERATURE", "-1"),
    ("RL_PAIRWISE_TEMPERATURE", "inf"),
    ("RL_VIT_BATCH_SIZE", "0"),
])
def test_pairwise_rejects_invalid_settings(monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(ValueError, match=key):
        reward_model_settings()
