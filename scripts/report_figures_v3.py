"""Figures for the presentation version of BAO_CAO_DAPO.md (docs/bao_cao/v3_*), generated from result files.

Usage: /home/llm/MinhPV/.venvs/plot/bin/python scripts/report_figures_v3.py
Needs slidegen_data/testset_v2/scored_5880 (with t03 PNGs), slidegen_data/pairs/baselines.json,
ViT/data/anh_slide and slidegen_data/annotation/round2/report_interim/results.json.
"""
import importlib.util
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "bao_cao"
PAGE, INK, SECOND, GRID = "#ffffff", "#1f2328", "#57606a", "#e5e7eb"
DAPO, BASE, GEMINI, BAD, GOOD = "#1B365D", "#9aa0a6", "#d08b2c", "#c0392b", "#2e7d4f"
plt.rcParams.update({"font.family": "Noto Sans", "font.size": 10.5, "axes.edgecolor": GRID, "axes.labelcolor": SECOND,
                     "xtick.color": SECOND, "ytick.color": SECOND, "text.color": INK, "figure.facecolor": PAGE,
                     "axes.facecolor": PAGE, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True})

spec = importlib.util.spec_from_file_location("table", ROOT / "scripts" / "dev_eval_table.py")
table = importlib.util.module_from_spec(spec)
spec.loader.exec_module(table)
TEST = "../testset_v2/scored_5880"


def save(fig, name: str) -> None:
    fig.savefig(OUT / name, dpi=170, bbox_inches="tight")
    plt.close(fig)


def test_row(system: str, best_of: int = 0) -> dict:
    return table.row(system, table.pick(table.load(TEST, system), best_of))


def records(system: str) -> dict:
    return {r["key"]: r for r in table.pick(table.load(TEST, system), 0)}


# 1. The RL loop: what the model sees, what it emits, how it is scored.
fig, ax = plt.subplots(figsize=(12, 3.3))
ax.set_xlim(0, 12)
ax.set_ylim(0, 3.3)
ax.axis("off")
boxes = [
    (0.1, "Nội dung slide\n+ layout được gán\n+ gợi ý sức chứa", "#eef2f7"),
    (2.5, "Qwen3.5-35B-A3B\n+ LoRA (DAPO)", "#dbe4f0"),
    (4.9, "Một lời gọi\ncông cụ XML", "#eef2f7"),
    (7.3, "Dựng slide,\nrender bằng\nChromium", "#eef2f7"),
    (9.7, "", "#f6ead8"),
]
for x, text, color in boxes:
    ax.add_patch(FancyBboxPatch((x, 1.2), 2.1, 1.9, boxstyle="round,pad=0.04,rounding_size=0.12", fc=color, ec="#b9c3d0"))
    ax.text(x + 1.05, 2.15, text, ha="center", va="center", fontsize=10.5)
for x in (2.2, 4.6, 7.0, 9.4):
    ax.add_patch(FancyArrowPatch((x + 0.02, 2.15), (x + 0.28, 2.15), arrowstyle="-|>", mutation_scale=14, color=SECOND))
ax.text(10.75, 2.82, "Reward tổng hợp", ha="center", fontsize=10.5, weight="bold")
ax.text(10.75, 1.72, "1,5·keypoint + 0,4·ngữ nghĩa\n+ 0,7·số liệu + 2,1·bố cục\n+ 1,5·ViT thẩm mỹ\n× hệ số ngôn ngữ",
        ha="center", va="center", fontsize=8.8, color=SECOND, linespacing=1.4)
ax.plot([10.75, 10.75, 3.55, 3.55], [1.15, 0.55, 0.55, 1.1], color=DAPO, lw=1.6)
ax.add_patch(FancyArrowPatch((3.55, 0.8), (3.55, 1.17), arrowstyle="-|>", mutation_scale=14, color=DAPO, lw=1.6))
ax.text(7.15, 0.2, "DAPO: sinh 4 mẫu mỗi prompt; mẫu có reward cao hơn trung bình nhóm được tăng xác suất",
        ha="center", fontsize=10, color=DAPO)
save(fig, "v3_01_vong_lap_rl.png")

# 2. Hand-made good/bad pairs: one example per defect type.
pairs_root = ROOT / "ViT" / "data" / "anh_slide" / "anh_slide"
defects = [("bo_cuc_xau", "Khối đè nhau", "hung_d23/Slide_12.png"), ("size_chu", "Cỡ chữ sai", "quang_d24/Slide_2001.png"),
           ("mau_nen_xau", "Màu nền xấu", "nam_d22/Slide_208.png"), ("mau_chu_xau", "Màu chữ xấu", "hung_d23/Slide_164.png"),
           ("tran_chu_ra_ngoai", "Tràn chữ ra ngoài", "hung_d23/Slide_59.png")]
fig, axes = plt.subplots(2, 5, figsize=(14, 3.7))
for col, (folder, label, name) in enumerate(defects):
    who, file = name.split("/")
    for row, path in enumerate([pairs_root / who / "Dep" / file, pairs_root / who / "Xau_1" / folder / file]):
        ax = axes[row][col]
        ax.imshow(Image.open(path).convert("RGB"))
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color(GOOD if row == 0 else BAD)
            spine.set_linewidth(2)
        if row == 0:
            ax.set_title(label, fontsize=11)
axes[0][0].set_ylabel("Đẹp", color=GOOD, fontsize=11)
axes[1][0].set_ylabel("Xấu", color=BAD, fontsize=11)
fig.subplots_adjust(wspace=0.04, hspace=0.06)
save(fig, "v3_02_cap_dep_xau.png")

# 3. Aesthetic judges: easy on synthetic pairs, hard on slides the model generated.
baselines = json.loads((ROOT / "slidegen_data" / "pairs" / "baselines.json").read_text())
fig, (left, right) = plt.subplots(1, 2, figsize=(11.5, 3.0), gridspec_kw={"width_ratios": [1, 1.25]})
names = ["Ngẫu nhiên", "CLIP zero-shot", "VLM 35B zero-shot", "ViT (của chúng tôi)"]
values = [50, baselines["clip"]["accuracy"] * 100, baselines["vlm"]["accuracy"] * 100, 97.9]
left.barh(names, values, color=[BASE, BASE, GEMINI, DAPO], height=0.55)
for i, v in enumerate(values):
    left.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=9.5)
left.set_xlim(0, 112)
left.set_title("Cặp đẹp–xấu nhân tạo (193 cặp kiểm thử)", fontsize=11)
left.set_xlabel("Chọn đúng slide đẹp (%)")
left.grid(axis="y", visible=False)
judges = [("ViT", "vit", DAPO), ("Reward tổng hợp", "reward", "#5b7aa6"), ("VLM 35B", "vlm", GEMINI)]
for j, (label, key, color) in enumerate(judges):
    vals = [baselines["human_aesthetic"][key] * 100, baselines["human_overall"][key] * 100]
    right.bar([i + (j - 1) * 0.26 for i in range(2)], vals, width=0.25, color=color, label=label)
    for i, v in enumerate(vals):
        right.text(i + (j - 1) * 0.26, v + 0.8, f"{v:.0f}", ha="center", fontsize=9)
right.axhline(50, color=SECOND, ls="--", lw=1)
right.set_xticks([0, 1], [f"Thẩm mỹ ({baselines['human_aesthetic']['n']} cặp)", f"Tổng thể ({baselines['human_overall']['n']} cặp)"])
right.set_ylim(40, 80)
right.set_ylabel("Chọn trùng người chấm (%)")
right.set_title("Slide do model sinh, người chấm thật", fontsize=11)
right.legend(frameon=False, fontsize=9, loc="upper left", ncol=3)
right.grid(axis="x", visible=False)
save(fig, "v3_03_bo_cham_tham_my.png")

# 4. Held-out test set overview: one sample vs best-of-4, three systems.
systems = [("Model gốc", "base_final_t03", "base_final_t10", BASE), ("DAPO", "dapo_final_t03", "dapo_final_t10", DAPO),
           ("Gemini 3.6 Flash", "gemini_final_t03", "gemini_final_t10", GEMINI)]
rows = {name: (test_row(one), test_row(four, 4)) for name, one, four, _ in systems}
fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.2))
for ax, (key, label, low) in zip(axes, [("usable", "Slide dùng được (%) — cao hơn tốt hơn", 80),
                                         ("visible", "Slide có lỗi nhìn thấy (%) — thấp hơn tốt hơn", 0)]):
    for s, (name, _, _, color) in enumerate(systems):
        for g in range(2):
            v = rows[name][g][key] * 100
            x = g * 1.0 + (s - 1) * 0.27
            ax.bar(x, v, width=0.25, color=color, label=name if g == 0 else None)
            ax.text(x, v + (0.3 if key == "usable" else 0.15), f"{v:.1f}", ha="center", fontsize=9)
    ax.set_xticks([0, 1], ["1 mẫu (T=0,3)", "Best-of-4 (T=1,0)"])
    ax.set_title(label, fontsize=11)
    ax.grid(axis="x", visible=False)
    if key == "usable":
        ax.set_ylim(low, 100)
fig.legend(*axes[0].get_legend_handles_labels(), frameon=False, fontsize=10, loc="upper center", ncol=3,
           bbox_to_anchor=(0.5, 1.08))
save(fig, "v3_04_tap_test_tong_quan.png")

# 5. Which defects each system makes on the test set (one sample, T=0.3).
kinds = [("cutoff", "Chữ bị cắt"), ("spill", "Tràn khỏi nền/panel"), ("collision", "Khối đè nhau"),
         ("invalid", "Lời gọi không hợp lệ")]
fig, ax = plt.subplots(figsize=(11.5, 2.9))
for s, (name, one, _, color) in enumerate(systems):
    row = dict(rows[name][0], invalid=1 - rows[name][0]["valid"])
    vals = [row[k] * 100 for k, _ in kinds]
    xs = [i + (s - 1) * 0.27 for i in range(len(kinds))]
    ax.bar(xs, vals, width=0.25, color=color, label=name)
    for x, v in zip(xs, vals):
        ax.text(x, v + 0.12, f"{v:.1f}", ha="center", fontsize=8.5)
ax.set_xticks(range(len(kinds)), [label for _, label in kinds])
ax.set_ylabel("% trong 337 slide")
ax.legend(frameon=False, fontsize=9)
ax.grid(axis="x", visible=False)
save(fig, "v3_05_loai_loi_tap_test.png")

# 6. Trade-off: fewer defects vs key-point coverage.
fig, ax = plt.subplots(figsize=(7.5, 3.6))
for name, _, _, color in systems:
    for g, marker in ((0, "o"), (1, "s")):
        row = rows[name][g]
        ax.scatter(row["keypoint"], row["usable"] * 100, s=90, color=color, marker=marker, zorder=3)
        ax.annotate(f"{name}{' best-of-4' if g else ''}", (row["keypoint"], row["usable"] * 100),
                    xytext=(6, -12 if (g and name == "Model gốc") else 5), textcoords="offset points", fontsize=8.8)
ax.set_xlabel("Độ phủ ý chính (keypoint) — phải hơn tốt hơn")
ax.set_ylabel("Slide dùng được (%)")
ax.set_title("Tròn: 1 mẫu; vuông: best-of-4", fontsize=10, color=SECOND)
save(fig, "v3_06_danh_doi_noi_dung.png")

# 7. Human evaluation round 2 (interim): win rate of DAPO with deck-bootstrap CIs.
interim = ROOT / "slidegen_data" / "annotation" / "round2" / "report_interim" / "results.json"
if interim.exists():
    win = json.loads(interim.read_text())["win_rates"]
    comparisons = [("dapo_vs_base", "so với model gốc"), ("dapo_vs_best4", "so với model gốc best-of-4"),
                   ("dapo_vs_gemini", "so với Gemini 3.6 Flash")]
    criteria = [("overall", "Tổng thể"), ("aesthetic", "Thẩm mỹ"), ("layout", "Bố cục"), ("coverage", "Đầy đủ"),
                ("language", "Ngôn ngữ"), ("faithful", "Trung thực")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.0), sharey=True)
    for ax, (comparison, title) in zip(axes, comparisons):
        for i, (key, _) in enumerate(criteria):
            item = win[f"{comparison}/{key}"]
            ax.errorbar(item["rate"], i, xerr=[[item["rate"] - item["ci"][0]], [item["ci"][1] - item["rate"]]],
                        fmt="o", color=DAPO, capsize=3, ms=6)
            ax.text(0.585, i, f"{item['rate']:.3f}", va="center", fontsize=8.8)
        ax.axvline(0.5, color=SECOND, ls="--", lw=1)
        ax.set_xlim(0.42, 0.6)
        ax.set_title(f"DAPO {title}\n({win[f'{comparison}/overall']['n']} cặp)", fontsize=10.5)
        ax.set_xlabel("Tỉ lệ thắng của DAPO (hòa = ½)")
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(range(len(criteria)), [label for _, label in criteria])
    axes[0].invert_yaxis()
    save(fig, "v3_07_nguoi_cham_dot2_tam.png")


# 11. Development set (291 slides, T=0.3): base vs DAPO rounds, round 4 as mean ± std over three seeds.
import statistics  # noqa: E402

dev = {name: table.row(name, table.pick(table.load("scored_r4", system), 0)) for name, system in
       [("Model gốc", "base_r4_t03"), ("DAPO-2d", "dapo_r2d_t03"), ("DAPO-3", "dapo_r3_t03"),
        ("s42", "dapo_r4s175_t03"), ("s7", "dapo_r4seed7_t03"), ("s2026", "dapo_r4seed2026_t03")]}
fig, axes = plt.subplots(1, 3, figsize=(12, 2.9))
labels = ["Model gốc", "DAPO-2d", "DAPO-3", "DAPO-4\n(3 seed)"]
for ax, (key, title, scale, fmt) in zip(axes, [("usable", "Slide dùng được (%), cao hơn tốt hơn", 100, "{:.1f}"),
                                               ("visible", "Lỗi nhìn thấy (%), thấp hơn tốt hơn", 100, "{:.1f}"),
                                               ("keypoint", "Độ phủ ý chính, cao hơn tốt hơn", 1, "{:.3f}")]):
    seeds = [dev[k][key] * scale for k in ("s42", "s7", "s2026")]
    vals = [dev[n][key] * scale for n in labels[:3]] + [statistics.mean(seeds)]
    err = [0, 0, 0, statistics.stdev(seeds)]
    ax.bar(range(4), vals, color=[BASE, "#8da2c0", "#8da2c0", DAPO], width=0.6)
    ax.errorbar(3, vals[3], yerr=err[3], color=INK, capsize=4)
    for i, v in enumerate(vals):
        ax.text(i, v + err[i] + (0.001 if scale == 1 else 0.15), fmt.format(v), ha="center", va="bottom", fontsize=9)
    ax.set_xticks(range(4), labels, fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.grid(axis="x", visible=False)
    if key == "usable":
        ax.set_ylim(85, 98)
    if key == "keypoint":
        ax.set_ylim(0.76, 0.83)
    if key == "visible":
        ax.set_ylim(0, 10.5)
save(fig, "v3_11_tap_phat_trien.png")


# 8-10. Real slides from the test set, each with the measured defects.
ISSUE = {"text_cutoff": "chữ bị cắt", "plate_spill": "tràn khỏi nền", "panel_spill": "tràn khỏi panel",
         "bbox_collision": "khối đè nhau", "low_contrast": "chữ khó đọc", "markup_leak": "lộ ký hiệu",
         "tiny_text": "chữ quá nhỏ", "slide_boundary": "vượt mép slide"}


def verdict(record: dict) -> str:
    if not record["valid"]:
        return "không hợp lệ"
    found = [ISSUE[i] for i in record["dom_issues"] or [] if i in ISSUE]
    if (record["components"] or {}).get("language", 1) < 1:
        found.append("lẫn chữ tiếng Anh")
    return ", ".join(dict.fromkeys(found)) if found else "không lỗi nhìn thấy"


def gallery(name: str, rows_spec: list[tuple[str, list[tuple[str, str]], str]]) -> None:
    """rows_spec: (key, [(system, label)], note) — one row per source slide."""
    cols = max(len(systems_) for _, systems_, _ in rows_spec)
    fig, axes = plt.subplots(len(rows_spec), cols, figsize=(5.6 * cols, 3.55 * len(rows_spec)), squeeze=False)
    for r, (key, systems_, note) in enumerate(rows_spec):
        for c, (system, label) in enumerate(systems_):
            ax = axes[r][c]
            record = records(system)[key]
            ax.imshow(Image.open(ROOT / record["png"]).convert("RGB").resize((960, 540)))
            ax.set_xticks([])
            ax.set_yticks([])
            bad = verdict(record) != "không lỗi nhìn thấy"
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color(BAD if bad else GOOD)
                spine.set_linewidth(2.2)
            ax.set_title(f"{label}: {verdict(record)}", fontsize=10.5, color=BAD if bad else GOOD)
        axes[r][0].set_ylabel(note, fontsize=9.5, color=SECOND)
    fig.subplots_adjust(wspace=0.04, hspace=0.22)
    save(fig, name)


gallery("v3_08_dapo_sua_loi_base.png", [
    ("2001_06", [("base_final_t03", "Model gốc"), ("dapo_final_t03", "DAPO")], "2001_06"),
    ("2034_03", [("base_final_t03", "Model gốc"), ("dapo_final_t03", "DAPO")], "2034_03"),
    ("2048_03", [("base_final_t03", "Model gốc"), ("dapo_final_t03", "DAPO")], "2048_03"),
])
gallery("v3_09_loi_gemini.png", [
    ("2000_00", [("gemini_final_t03", "Gemini"), ("dapo_final_t03", "DAPO")], "2000_00"),
    ("2003_00", [("gemini_final_t03", "Gemini"), ("dapo_final_t03", "DAPO")], "2003_00"),
    ("2001_06", [("gemini_final_t03", "Gemini"), ("dapo_final_t03", "DAPO")], "2001_06"),
])
gallery("v3_10_loi_dapo_con_lai.png", [
    ("2048_06", [("dapo_final_t03", "DAPO"), ("base_final_t03", "Model gốc")], "2048_06"),
    ("2018_07", [("dapo_final_t03", "DAPO"), ("base_final_t03", "Model gốc")], "2018_07"),
    ("2001_00", [("dapo_final_t03", "DAPO"), ("base_final_t03", "Model gốc")], "2001_00"),
])
print("figures written to", OUT)
