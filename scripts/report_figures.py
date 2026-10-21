"""Figures for docs/bao_cao (round-1 results). Usage: PYTHONPATH=/data/venvs/plot python scripts/report_figures.py"""
import collections
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "bao_cao"
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
COLOR = {"dapo": "#2a78d6", "base": "#eb6834", "gemini": "#1baf7a", "best8": "#eda100"}
NAME = {"dapo": "DAPO", "base": "Model gốc", "gemini": "Gemini 3.6 Flash", "best8": "Best-of-8 (gốc)"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True})


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


# 1. Environment-induced hallucination
fig, ax = plt.subplots(figsize=(6.4, 3.4))
labels = ["Môi trường ban đầu", "Sửa công cụ\n(liên hệ, biểu đồ)", "Sửa prompt + schema"]
values = [11.7, 5.2, 1.5]
bars = ax.bar(labels, values, width=0.5, color=COLOR["dapo"])
for bar, value in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, value + 0.25, f"{value}%", ha="center", color=INK)
ax.set_ylabel("Slide có số liệu bịa (%)")
ax.set_title("Model gốc, chưa train: lỗi bịa số liệu giảm chỉ nhờ sửa môi trường", loc="left", fontsize=11)
ax.grid(axis="x", visible=False)
save(fig, "1_bia_so_lieu_do_moi_truong.png")

# 2. Automatic test-set reward + best-of-N
summary = json.loads((ROOT / "rl/runs/final_v3_20261005/testset/summary.json").read_text())
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"width_ratios": [1, 1.1]})
ax = axes[0]
order = ["base", "gemini", "dapo", "best8"]
for i, system in enumerate(order):
    row = summary[system]
    ax.errorbar(row["reward"], i, xerr=[[row["reward"] - row["ci"][0]], [row["ci"][1] - row["reward"]]],
                fmt="o", color=COLOR[system], ms=9, lw=2, capsize=4)
    ax.text(row["ci"][1] + 0.04, i, f"{row['reward']:.2f}", va="center", color=INK)
ax.set_yticks(range(len(order)), [NAME[s] for s in order])
ax.set_xlabel("Reward tổng hợp (trung bình, 95% CI theo bộ slide)")
ax.set_title("Điểm tự động trên tập test (291 slide)", loc="left", fontsize=11)
ax.set_xlim(2.3, 4.3)
ax.grid(axis="y", visible=False)
ax = axes[1]
best = {"base": {1: 2.719, 2: 3.257, 4: 3.673, 8: 3.92}, "dapo": {1: 3.494, 2: 3.821, 4: 3.992},
        "gemini": {1: 3.423, 2: 3.642, 4: 3.818}}
for system, points in best.items():
    xs, ys = list(points), list(points.values())
    ax.plot(xs, ys, "-o", color=COLOR[system], lw=2, ms=7)
    ax.text(xs[-1] * 1.07, ys[-1], NAME[system], va="center", color=INK)
ax.set_xscale("log", base=2)
ax.set_xticks([1, 2, 4, 8], ["1", "2", "4", "8"])
ax.set_xlim(0.9, 16)
ax.set_xlabel("Số mẫu sinh rồi chọn bằng reward")
ax.set_ylabel("Reward của mẫu được chọn")
ax.set_title("DAPO lấy 4 mẫu ≈ model gốc lấy 8 mẫu", loc="left", fontsize=11)
save(fig, "2_diem_tu_dong_tap_test.png")

# 3. Human win rates
results = json.loads((ROOT / "slidegen_data/annotation/report/results.json").read_text())["win_rates"]
criteria = ["overall", "aesthetic", "layout", "language", "coverage", "faithful"]
vi = {"overall": "Tổng thể", "aesthetic": "Thẩm mỹ", "layout": "Bố cục", "language": "Ngôn ngữ",
      "coverage": "Đầy đủ", "faithful": "Trung thực"}
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
for ax, (comparison, rival) in zip(axes, [("dapo_vs_base", "base"), ("dapo_vs_gemini", "gemini"), ("dapo_vs_best8", "best8")]):
    for i, criterion in enumerate(criteria[::-1]):
        row = results[f"{comparison}/{criterion}"]
        ax.errorbar(row["rate"], i, xerr=[[row["rate"] - row["ci"][0]], [row["ci"][1] - row["rate"]]],
                    fmt="o", color=COLOR["dapo"], ms=8, lw=2, capsize=4)
        ax.text(0.672, i, f"{row['rate']:.3f}", va="center", ha="right", color=INK, fontsize=10)
    ax.axvline(0.5, color=MUTED, lw=1, ls="--")
    ax.set_xlim(0.38, 0.68)
    ax.set_yticks(range(len(criteria)), [vi[c] for c in criteria[::-1]])
    ax.set_title(f"DAPO so với {NAME[rival]}", loc="left", fontsize=11)
    ax.set_xlabel("Tỉ lệ thắng của DAPO (hòa = ½)")
    ax.grid(axis="y", visible=False)
fig.suptitle("Người chấm (vòng 1): bên phải vạch 0.5 là DAPO thắng; thanh ngang là 95% CI", x=0.01, ha="left", fontsize=11)
fig.tight_layout()
save(fig, "3_nguoi_cham_ti_le_thang.png")

# 4. Reward-human agreement vs reward gap
bins = [("< 0.5", 192, 0.62), ("0.5–1.0", 74, 0.70), ("1.0–1.5", 35, 0.86), ("1.5–2.0", 15, 0.87), ("≥ 2.0", 26, 1.00)]
fig, ax = plt.subplots(figsize=(6.4, 3.4))
bars = ax.bar([b[0] for b in bins], [100 * b[2] for b in bins], width=0.55, color=COLOR["dapo"])
for bar, (_, n, rate) in zip(bars, bins):
    ax.text(bar.get_x() + bar.get_width() / 2, 100 * rate + 1.5, f"{100 * rate:.0f}%\n(n={n})", ha="center", color=INK, fontsize=10)
ax.axhline(50, color=MUTED, lw=1, ls="--")
ax.text(4.45, 51, "ngẫu nhiên", color=MUTED, ha="right", fontsize=9)
ax.set_ylim(0, 115)
ax.set_xlabel("Chênh lệch reward giữa hai slide")
ax.set_ylabel("Reward chọn trùng người chấm (%)")
ax.set_title("Reward càng chênh lớn càng khớp với lựa chọn của người", loc="left", fontsize=11)
ax.grid(axis="x", visible=False)
save(fig, "4_reward_khop_nguoi_cham.png")

# 5. DAPO vs Gemini by layout (rating-level wins minus losses)
ratings = json.loads((ROOT / "slidegen_data/annotation/ratings.json").read_text())["ratings"]
mapping = json.loads((ROOT / "slidegen_data/annotation/secret_mapping.json").read_text())["pairs"]
rows = {r["key"]: r for r in json.loads((ROOT / "slidegen_data/testset/eval_rows.json").read_text())}
value = {"A": 1, "tie": 0, "B": -1}
by_tool = collections.defaultdict(list)
for rating in ratings:
    entry = mapping[rating["pair_id"]]
    if entry["comparison"] != "dapo_vs_gemini" or entry["attention_check_of"]:
        continue
    sign = 1 if entry["a"]["system"] == "dapo" else -1
    tool = rows[entry["key"]]["assigned_tool_name"].replace("generate_", "").replace("_slide_xml", "")
    by_tool[tool].append(sign * value[rating["answers"]["overall"]])
items = sorted(((tool, sum(v > 0 for v in vals), sum(v < 0 for v in vals)) for tool, vals in by_tool.items() if len(vals) >= 8),
               key=lambda item: item[1] - item[2])
fig, ax = plt.subplots(figsize=(8.4, 5.2))
for i, (tool, wins, losses) in enumerate(items):
    ax.barh(i, wins, height=0.6, color=COLOR["dapo"])
    ax.barh(i, -losses, height=0.6, color=COLOR["gemini"])
    ax.text(wins + 0.5, i, str(wins), va="center", color=INK, fontsize=9)
    ax.text(-losses - 0.5, i, str(losses), va="center", ha="right", color=INK, fontsize=9)
ax.set_yticks(range(len(items)), [item[0][:34] for item in items], fontsize=9)
ax.axvline(0, color=INK, lw=1)
ax.set_xlim(-32, 32)
ax.set_xticks([-30, -20, -10, 0, 10, 20, 30], ["30", "20", "10", "0", "10", "20", "30"])
ax.set_xlabel("← Gemini thắng (số lượt chấm)        DAPO thắng (số lượt chấm) →")
ax.set_title("DAPO thắng rõ ở layout 2–3 ý; thua ở layout bìa và layout nhiều khối chữ", loc="left", fontsize=11)
ax.grid(axis="y", visible=False)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=COLOR["dapo"]), plt.Rectangle((0, 0), 1, 1, color=COLOR["gemini"])],
          labels=["DAPO thắng", "Gemini thắng"], frameon=False, loc="lower right")
save(fig, "5_dapo_vs_gemini_theo_layout.png")
print(sorted(p.name for p in OUT.glob("*.png")))

# 0. Reward-model dataset: pairs per defect type and held-out pairwise accuracy
import csv  # noqa: E402

pairs = [row for name in ("train_data.csv", "val_data.csv") for row in csv.DictReader(open(ROOT / "slidegen_data/pairs" / name))]
defects = {"cac_khoi_de_nhau": "Các khối đè nhau", "size_chu": "Cỡ chữ sai", "mau_nen_xau": "Màu nền xấu",
           "mau_chu_xau": "Màu chữ xấu", "tran_chu": "Tràn chữ ra ngoài"}
accuracy = {"cac_khoi_de_nhau": 97.7, "size_chu": 97.6, "mau_nen_xau": 100.0, "mau_chu_xau": 100.0, "tran_chu": 96.1}
counts = {key: sum(key in row["bad_path"].split("/")[-2] for row in pairs) for key in defects}
order = sorted(defects, key=lambda key: counts[key])
fig, axes = plt.subplots(1, 2, figsize=(11, 3.2), sharey=True)
bars = axes[0].barh([defects[k] for k in order], [counts[k] for k in order], height=0.55, color=COLOR["dapo"])
for bar, key in zip(bars, order):
    axes[0].text(counts[key] + 12, bar.get_y() + bar.get_height() / 2, str(counts[key]), va="center", color=INK)
axes[0].set_xlabel("Số cặp đẹp–xấu có lỗi này (một cặp có thể có 2 lỗi)")
axes[0].set_title("Dữ liệu gán tay: 1.929 cặp, 5 loại lỗi", loc="left", fontsize=11)
axes[0].set_xlim(0, max(counts.values()) * 1.15)
axes[0].grid(axis="y", visible=False)
axes[1].plot([accuracy[k] for k in order], [defects[k] for k in order], "o", color=COLOR["dapo"], ms=9)
for index, key in enumerate(order):
    axes[1].text(accuracy[key] + 0.25, index, f"{accuracy[key]:.1f}%", va="center", color=INK)
axes[1].set_xlim(90, 101.5)
axes[1].set_xlabel("Độ chính xác chọn đúng slide đẹp trên tập kiểm thử (%)")
axes[1].set_title("ViT pairwise: 97,9% trên 193 cặp chưa thấy", loc="left", fontsize=11)
axes[1].grid(axis="y", visible=False)
save(fig, "0_reward_model.png")
print(counts)
