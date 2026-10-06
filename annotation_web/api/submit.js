import { annotatorFor, ensureSchema, readJson, sql } from "./_db.js";

const CHOICES = new Set(["A", "B", "tie"]);
const CRITERIA = ["faithful", "coverage", "language", "layout", "aesthetic", "overall"];
const FLAGS = ["fabricated", "broken", "wrong_language"];

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  const body = await readJson(req);
  const annotatorId = annotatorFor(body.code);
  if (!annotatorId) return res.status(401).json({ error: "Mã người chấm không hợp lệ" });
  const answers = body.answers || {};
  const valid =
    typeof body.pair_id === "string" && body.pair_id.length < 64 &&
    CRITERIA.every((key) => CHOICES.has(answers[key])) &&
    ["A", "B"].every((side) => FLAGS.every((flag) => typeof answers.flags?.[side]?.[flag] === "boolean"));
  if (!valid) return res.status(400).json({ error: "Thiếu câu trả lời" });
  const clean = {
    ...Object.fromEntries(CRITERIA.map((key) => [key, answers[key]])),
    flags: Object.fromEntries(["A", "B"].map((side) => [side, Object.fromEntries(FLAGS.map((f) => [f, answers.flags[side][f]]))])),
    comment: String(answers.comment || "").slice(0, 1000),
  };
  await ensureSchema();
  await sql`
    INSERT INTO ratings (annotator_id, pair_id, answers, duration_ms, client_ts)
    VALUES (${annotatorId}, ${body.pair_id}, ${JSON.stringify(clean)}::jsonb,
            ${Number.isFinite(body.duration_ms) ? Math.round(body.duration_ms) : null},
            ${body.client_ts || null})
    ON CONFLICT (annotator_id, pair_id)
    DO UPDATE SET answers = EXCLUDED.answers, duration_ms = EXCLUDED.duration_ms,
                  client_ts = EXCLUDED.client_ts, updated_at = now()`;
  return res.status(200).json({ ok: true });
}
