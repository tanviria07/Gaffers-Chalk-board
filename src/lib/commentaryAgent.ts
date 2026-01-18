export interface LiveCommentaryInput {
  videoId: string;
  timestamp: number;
  windowSize?: number;
}

export interface LiveCommentaryResponse {
  commentary: string | null;
  rawAction: string | null;
  timestamp: number;
  skipped: boolean;
  error?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE?.trim() || "/api";

function asString(v: unknown): string | null {
  if (typeof v !== "string") return null;
  const t = v.trim();
  return t.length ? t : null;
}

function asNumber(v: unknown, fallback: number): number {
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : fallback;
}

export async function getLiveCommentary(
  input: LiveCommentaryInput
): Promise<LiveCommentaryResponse> {
  try {
    const res = await fetch(`${API_BASE}/live-commentary`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        videoId: input.videoId,
        timestamp: input.timestamp,
        windowSize: input.windowSize ?? 5.0,
      }),
    });

    const text = await res.text();
    let data: any = null;

    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = null;
    }

    if (!res.ok) {
      const msg =
        asString(data?.error) ||
        asString(data?.message) ||
        (text ? text.slice(0, 300) : `HTTP ${res.status}`);
      return {
        commentary: null,
        rawAction: null,
        timestamp: input.timestamp,
        skipped: true,
        error: msg,
      };
    }

    return {
      commentary: asString(data?.commentary),
      rawAction: asString(data?.rawAction),
      timestamp: asNumber(data?.timestamp, input.timestamp),
      skipped: Boolean(data?.skipped),
      error: asString(data?.error) ?? undefined,
    };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    return {
      commentary: null,
      rawAction: null,
      timestamp: input.timestamp,
      skipped: true,
      error: msg,
    };
  }
}
