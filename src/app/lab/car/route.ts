import { readFile } from "node:fs/promises";
import path from "node:path";

// Dev-only: serves traced car definitions straight from disk so the lab can
// preview a stop the moment its trace script writes the JSON.
export async function GET(request: Request) {
  if (process.env.NODE_ENV === "production")
    return new Response("Not found", { status: 404 });
  const id = new URL(request.url).searchParams.get("id") ?? "";
  if (!/^[\w.-]+$/.test(id)) return new Response("Bad id", { status: 400 });
  try {
    const file = path.join(process.cwd(), "src", "data", "cars", `${id}.json`);
    return new Response(await readFile(file, "utf8"), {
      headers: {
        "content-type": "application/json",
        "cache-control": "no-store",
      },
    });
  } catch {
    return new Response("Not found", { status: 404 });
  }
}
