import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const backend = process.env.NEXT_PUBLIC_API_URL ?? "";
  const internalKey = process.env.INTERNAL_API_KEY ?? "";
  const body = await req.arrayBuffer();
  const res = await fetch(`${backend}/api/generate-bracket`, {
    method: "POST",
    signal: AbortSignal.timeout(25_000),
    headers: {
      "Content-Type": "application/json",
      "X-Internal-Key": internalKey,
    },
    body,
  });
  const data = await res.arrayBuffer();
  return new NextResponse(data, {
    status: res.status,
    headers: {
      "Content-Type": res.headers.get("Content-Type") ?? "image/png",
    },
  });
}
