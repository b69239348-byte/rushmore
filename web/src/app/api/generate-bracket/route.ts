import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? "";
const INTERNAL_KEY = process.env.INTERNAL_API_KEY ?? "";

export async function POST(req: NextRequest) {
  const body = await req.arrayBuffer();
  const res = await fetch(`${BACKEND}/api/generate-bracket`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Internal-Key": INTERNAL_KEY,
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
