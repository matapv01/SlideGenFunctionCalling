const CRITERIA = [
  ["faithful", "Trung thực với nguồn", "Ít thông tin sai/bịa hơn"],
  ["coverage", "Đầy đủ, đúng trọng tâm", "Giữ được ý chính của nguồn"],
  ["language", "Ngôn ngữ", "Chính tả, ngữ pháp, không ký tự lạ"],
  ["layout", "Bố cục, khả năng đọc", "Không tràn/cắt/đè chữ, dễ đọc"],
  ["aesthetic", "Thẩm mỹ", "Đẹp, chuyên nghiệp"],
  ["overall", "Lựa chọn tổng thể", "Slide bạn sẽ dùng thật"],
];
const FLAGS = [
  ["fabricated", "Thông tin bịa/sai"],
  ["broken", "Lỗi hiển thị nghiêm trọng"],
  ["wrong_language", "Sai ngôn ngữ"],
];
const CHOICES = ["A", "tie", "B"];
const $ = (id) => document.getElementById(id);
const store = {
  get(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* private mode */ } },
};

const state = { code: null, annotator: null, queue: [], done: new Set(), pairs: {}, imageBase: "", index: 0, active: 0, shownAt: 0 };

function show(view) {
  for (const id of ["login-view", "guide-view", "rate-view", "done-view"]) $(id).hidden = id !== view;
  $("guide-button").hidden = view === "login-view";
}

async function api(path, body) {
  const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Lỗi ${response.status}`);
  return data;
}

async function login(code) {
  const session = await api("/api/session", { code });
  const [pairs, assignments] = await Promise.all([
    fetch("/data/pairs.json").then((r) => r.json()),
    fetch("/data/assignments.json").then((r) => r.json()),
  ]);
  state.code = code;
  state.annotator = session.annotator_id;
  state.done = new Set(session.done);
  state.imageBase = pairs.image_base;
  state.pairs = Object.fromEntries(pairs.pairs.map((pair) => [pair.id, pair]));
  state.queue = assignments[state.annotator] || [];
  const firstOpen = state.queue.findIndex((id) => !state.done.has(id));
  state.index = firstOpen === -1 ? state.queue.length : firstOpen;
  store.set("slidegen-code", code);
  if (!store.get(`guide-seen-${state.annotator}`, false)) show("guide-view");
  else renderPair();
}

function updateProgress() {
  const total = state.queue.length || 1;
  $("progress-label").textContent = `${state.annotator} · đã chấm ${state.done.size}/${state.queue.length}`;
  $("progress-bar").style.width = `${(100 * state.done.size) / total}%`;
}

function draftKey(pairId) { return `draft-${state.annotator}-${pairId}`; }

function renderPair() {
  updateProgress();
  if (state.index >= state.queue.length) return show("done-view");
  show("rate-view");
  const pair = state.pairs[state.queue[state.index]];
  const draft = store.get(draftKey(pair.id), { flags: { A: {}, B: {} } });
  $("pair-label").textContent = `${pair.kind ? pair.kind + " · " : ""}Cặp ${state.index + 1}/${state.queue.length}`;
  $("source-title").textContent = pair.title;
  $("source-text").textContent = pair.text;
  for (const side of ["A", "B"]) {
    const img = $(`img-${side}`);
    img.src = state.imageBase + pair[side.toLowerCase()];
  }
  $("criteria-body").innerHTML = CRITERIA.map(([key, label, hint], row) => `
    <tr data-row="${row}">
      <td>${label}<small>${hint}</small></td>
      ${CHOICES.map((choice) => `<td><input type="radio" name="${key}" value="${choice}" ${draft[key] === choice ? "checked" : ""} aria-label="${label}: ${choice}"></td>`).join("")}
    </tr>`).join("");
  for (const side of ["A", "B"]) {
    $(`flags-${side}`).innerHTML = FLAGS.map(([flag, label]) =>
      `<label><input type="checkbox" data-side="${side}" data-flag="${flag}" ${draft.flags?.[side]?.[flag] ? "checked" : ""}> ${label}</label>`).join("");
  }
  $("comment").value = draft.comment || "";
  $("prev-button").disabled = state.index === 0;
  $("save-status").textContent = state.done.has(pair.id) ? "Đã lưu trước đó (có thể sửa)" : "";
  state.active = Math.max(0, CRITERIA.findIndex(([key]) => !draft[key]));
  highlightRow();
  state.shownAt = performance.now();
  window.scrollTo({ top: 0 });
}

function collect() {
  const answers = { flags: { A: {}, B: {} }, comment: $("comment").value.trim() };
  for (const [key] of CRITERIA) answers[key] = document.querySelector(`input[name="${key}"]:checked`)?.value;
  for (const box of document.querySelectorAll("#rating-form input[type=checkbox]")) {
    answers.flags[box.dataset.side][box.dataset.flag] = box.checked;
  }
  return answers;
}

function saveDraft() {
  const pair = state.queue[state.index];
  if (pair) store.set(draftKey(pair), collect());
}

function highlightRow() {
  document.querySelectorAll("#criteria-body tr").forEach((row, index) => row.classList.toggle("active", index === state.active));
}

async function submit() {
  const answers = collect();
  const missing = CRITERIA.filter(([key]) => !answers[key]).map(([, label]) => label);
  if (missing.length) {
    $("save-status").textContent = `Còn thiếu: ${missing.join(", ")}`;
    return;
  }
  const pairId = state.queue[state.index];
  $("next-button").disabled = true;
  $("save-status").textContent = "Đang lưu…";
  try {
    await api("/api/submit", {
      code: state.code, pair_id: pairId, answers,
      duration_ms: performance.now() - state.shownAt, client_ts: new Date().toISOString(),
    });
    store.set(draftKey(pairId), answers);
    state.done.add(pairId);
    state.index += 1;
    renderPair();
  } catch (error) {
    $("save-status").textContent = `Không lưu được: ${error.message}. Bấm lại để thử.`;
  } finally {
    $("next-button").disabled = false;
  }
}

$("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("login-error").hidden = true;
  try { await login($("code-input").value.trim()); }
  catch (error) { $("login-error").textContent = error.message; $("login-error").hidden = false; }
});
$("start-button").addEventListener("click", () => { store.set(`guide-seen-${state.annotator}`, true); renderPair(); });
$("guide-button").addEventListener("click", () => { saveDraft(); show("guide-view"); });
$("rating-form").addEventListener("submit", (event) => { event.preventDefault(); submit(); });
$("rating-form").addEventListener("change", (event) => {
  saveDraft();
  const row = event.target.closest("tr")?.dataset.row;
  if (row !== undefined) { state.active = Math.min(CRITERIA.length - 1, Number(row) + 1); highlightRow(); }
});
$("prev-button").addEventListener("click", () => { saveDraft(); state.index = Math.max(0, state.index - 1); renderPair(); });
for (const side of ["A", "B"]) {
  $(`img-${side}`).addEventListener("click", () => { $("zoom-img").src = $(`img-${side}`).src; $("zoom").showModal(); });
}
$("zoom-close").addEventListener("click", () => $("zoom").close());
document.addEventListener("keydown", (event) => {
  if ($("rate-view").hidden || event.target.matches("textarea, input[type=text]") || $("zoom").open) return;
  if (["1", "2", "3"].includes(event.key)) {
    const [key] = CRITERIA[state.active];
    const input = document.querySelector(`input[name="${key}"][value="${CHOICES[Number(event.key) - 1]}"]`);
    input.checked = true;
    input.dispatchEvent(new Event("change", { bubbles: true }));
  } else if (event.key === "Enter") {
    event.preventDefault();
    submit();
  }
});

const saved = store.get("slidegen-code", null);
if (saved) login(saved).catch(() => show("login-view"));
else show("login-view");
