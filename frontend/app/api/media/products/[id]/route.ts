import { NextResponse } from "next/server";
import { readFile, stat } from "fs/promises";
import path from "path";

const DATA_DIR = path.resolve(
  process.env.DATA_DIR || path.join(process.cwd(), "..", "data")
);

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const filePath = path.join(DATA_DIR, "products", `${id}.jpg`);

  try {
    const fileStat = await stat(filePath);
    const buffer = await readFile(filePath);

    return new Response(buffer, {
      status: 200,
      headers: {
        "Content-Type": "image/jpeg",
        "Content-Length": String(fileStat.size),
        "Cache-Control": "public, max-age=86400",
      },
    });
  } catch {
    return NextResponse.json(
      { error: "Product image not found" },
      { status: 404 }
    );
  }
}
