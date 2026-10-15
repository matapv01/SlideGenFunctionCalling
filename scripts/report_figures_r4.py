"""Round-4 figures for docs/bao_cao, generated from the scored result files (Kami palette).

Usage: PYTHONPATH=/data/venvs/plot python scripts/report_figures_r4.py
"""
import importlib.util
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "bao_cao"
PAGE, INK, SECOND, GRID = "#f5f4ed", "#141413", "#3d3d3a", "#e8e6dc"
OURS, BASE, OTHERS = "#1B365D", "#6b6a64", ["#504e49", "#b8b7b0"]
plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 10.5, "axes.edgecolor": GRID, "axes.labelcolor": SECOND,
                     "xtick.color": SECOND, "ytick.color": SECOND, "text.color": INK, "figure.facecolor": PAGE,
                     "axes.facecolor": PAGE, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True})

spec = importlib.util.spec_from_file_location("table", ROOT / "scripts" / "dev_eval_table.py")
table = importlib.util.module_from_spec(spec)
spec.loader.exec_module(table)


def dev_row(system: str) -> dict:
    return table.row(system, table.pick(table.load("scored_r4", system), 0))


def save(fig, name: str) -> None:
    fig.savefig(OUT / name, dpi=160, bbox_inches="tight")
    plt.close(fig)


# 6. Development set: base model vs DAPO rounds; round 4 as mean ± std over three seeds.
base = dev_row("base_r4_t03")
others = {"DAPO-2d": dev_row("dapo_r2d_t03"), "DAPO-3": dev_row("dapo_r3_t03")}
seeds = [dev_row(s) for s in ("dapo_r4s175_t03", "dapo_r4seed7_t03", "dapo_r4seed2026_t03")]
panels = [("usable", "Slide dùng được (%)\ncao hơn = tốt hơn", 100), ("visible", "Slide có lỗi nhìn thấy (%)\nthấp hơn = tốt hơn", 100),
          ("keypoint", "Độ phủ ý chính (keypoint)\ncao hơn = tốt hơn", 1)]
fig, axes = plt.subplots(1, 3, figsize=(11.5, 2.6))
names = list(others) + ["DAPO-4 (3 seed)"]
for ax, (key, label, scale) in zip(axes, panels):
    values = [others[n][key] * scale for n in others]
    mean = statistics.mean(s[key] for s in seeds) * scale
    std = statistics.stdev(s[key] for s in seeds) * scale
    ax.barh(range(len(values)), values, height=0.5, color=OTHERS[0])
    ax.barh(len(values), mean, height=0.5, color=OURS, xerr=std, error_kw={"ecolor": INK, "capsize": 3, "lw": 1})
    ax.axvline(base[key] * scale, color=BASE, lw=1.4, ls="--")
    for i, v in enumerate(values + [mean]):
        ax.text(v, i + 0.33, f"{v:.1f}" if scale == 100 else f"{v:.3f}", ha="center", fontsize=9, color=INK)
    ax.set_yticks(range(len(names)), names if key == "usable" else [""] * len(names))
    ax.set_xlabel(label)
    ax.grid(axis="y", visible=False)
    low = min(values + [mean, base[key] * scale])
    high = max(values + [mean, base[key] * scale])
    ax.set_xlim(low - (high - low) * 0.8, high + (high - low) * 0.6)
fig.legend(handles=[plt.Line2D([], [], color=BASE, lw=1.4, ls="--")], labels=["model gốc, cùng prompt"],
           frameon=False, loc="center left", bbox_to_anchor=(1.0, 0.55))
fig.suptitle("Tập phát triển, 291 slide, T=0.3: DAPO-4 giảm lỗi nhìn thấy gần một nửa, đổi lại độ phủ ý chính giảm 0,02",
             x=0.01, y=1.0, ha="left", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.93))
save(fig, "6_tap_phat_trien_vong4.png")

# 7. Round-4 training curves: internal eval reward of the original run and both replicates.
runs = {"seed 42 (bản chốt)": "qwen3_5_35b_dapo_r4_20261014", "seed 7": "qwen3_5_35b_dapo_r4_seed7_20261014",
        "seed 2026": "qwen3_5_35b_dapo_r4_seed2026_20261014"}
fig, ax = plt.subplots(figsize=(8.2, 3.2))
for (name, run), color in zip(runs.items(), [OURS] + OTHERS):
    states = sorted((ROOT / run).glob("checkpoint-*/trainer_state.json"), key=lambda p: int(p.parent.name.split("-")[1]))
    history = max((json.loads(p.read_text())["log_history"] for p in states), key=len)
    points = sorted({r["step"]: r["eval_reward"] for r in history if "eval_reward" in r}.items())
    xs, ys = zip(*points)
    ax.plot(xs, ys, "-o", color=color, lw=1.6, ms=4, label=name)
    ax.axhline(ys[0], color=color, lw=0.8, ls=":")
ax.set_xlabel("Bước train")
ax.set_ylabel("Reward eval nội bộ\ncao hơn = tốt hơn")
ax.legend(frameon=False, loc="center left", bbox_to_anchor=(1.01, 0.5))
ax.set_title("Cả ba seed đều vượt mức bước 0 (đường chấm), nhưng đỉnh rơi vào bước rất khác nhau: 50, 175, 175",
             loc="left", fontsize=10.5)
save(fig, "7_duong_cong_vong4.png")
print(sorted(p.name for p in OUT.glob("[67]_*.png")))
