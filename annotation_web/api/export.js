import { ensureSchema, sql } from "./_db.js";

export default async function handler(req, res) {
  const token = req.headers["x-admin-token"];
  if (!process.env.ADMIN_TOKEN || token !== process.env.ADMIN_TOKEN) {
    return res.status(401).json({ error: "unauthorized" });
  }
  await ensureSchema();
  const rows = await sql`SELECT * FROM ratings ORDER BY annotator_id, updated_at`;
  return res.status(200).json({ count: rows.length, ratings: rows });
}
