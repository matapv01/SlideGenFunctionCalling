import { annotatorFor, ensureSchema, readJson, sql } from "./_db.js";

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  const { code } = await readJson(req);
  const annotatorId = annotatorFor(code);
  if (!annotatorId) return res.status(401).json({ error: "Mã người chấm không hợp lệ" });
  await ensureSchema();
  const rows = await sql`SELECT pair_id FROM ratings WHERE annotator_id = ${annotatorId}`;
  return res.status(200).json({ annotator_id: annotatorId, done: rows.map((row) => row.pair_id) });
}
