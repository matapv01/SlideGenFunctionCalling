import { neon } from "@neondatabase/serverless";

const url = process.env.DATABASE_URL || process.env.POSTGRES_URL;
export const sql = url ? neon(url) : null;

let ready = null;
export function ensureSchema() {
  if (!sql) throw new Error("DATABASE_URL is not configured");
  ready ??= sql`
    CREATE TABLE IF NOT EXISTS ratings (
      annotator_id TEXT NOT NULL,
      pair_id      TEXT NOT NULL,
      answers      JSONB NOT NULL,
      duration_ms  INTEGER,
      client_ts    TIMESTAMPTZ,
      updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
      PRIMARY KEY (annotator_id, pair_id)
    )`;
  return ready;
}

// ANNOTATOR_CODES="secretcode1:A1,secretcode2:A2" keeps annotator identity off the client.
export function annotatorFor(code) {
  const entries = (process.env.ANNOTATOR_CODES || "").split(",").map((item) => item.trim().split(":"));
  const match = entries.find(([secret]) => secret && secret === String(code || "").trim());
  return match ? match[1] : null;
}

export function readJson(req) {
  if (req.body && typeof req.body === "object") return Promise.resolve(req.body);
  return new Promise((resolve, reject) => {
    let raw = "";
    req.on("data", (chunk) => (raw += chunk));
    req.on("end", () => {
      try { resolve(raw ? JSON.parse(raw) : {}); } catch (error) { reject(error); }
    });
  });
}
