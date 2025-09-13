import type { Run, RunEvent } from "./types.js";
import { ExosphereClient } from "./client.js";

export interface AwaitRunOptions {
  pollIntervalMs?: number;
  maxWaitMs?: number;
  onUpdate?: (run: Run) => void;
}

export async function awaitRun(
  client: ExosphereClient,
  runId: string,
  options?: AwaitRunOptions
): Promise<Run> {
  const start = Date.now();
  const poll = Math.max(250, options?.pollIntervalMs ?? 1000);
  const maxWait = options?.maxWaitMs ?? 60 * 60 * 1000; // 1 hour default
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const run = await client.getRun(runId);
    options?.onUpdate?.(run);
    if (isTerminal(run.status)) return run;
    if (Date.now() - start > maxWait) {
      throw new Error(`Timed out waiting for run ${runId} to complete`);
    }
    await sleep(poll);
  }
}

export interface StreamRunEventsOptions<T = unknown> {
  signal?: AbortSignal;
  onError?: (error: unknown) => void;
  parser?: (raw: string) => T;
}

export async function streamRunEvents<T = unknown>(
  client: ExosphereClient,
  runId: string,
  onEvent: (event: RunEvent<T>) => void,
  options?: StreamRunEventsOptions<T>
): Promise<void> {
  const controller = new AbortController();
  const signals: AbortSignal[] = [];
  if (options?.signal) signals.push(options.signal);
  signals.push(controller.signal);
  const signal = anySignal(signals);

  const resp = await client.requestRaw(`/v1/runs/${encodeURIComponent(runId)}/events?stream=1`, {
    method: "GET",
    headers: {
      Accept: "text/event-stream",
    },
    signal,
  });
  if (!resp.ok || !resp.body) {
    const text = await safeReadText(resp);
    throw new Error(`Failed to stream events: HTTP ${resp.status} ${resp.statusText} ${text}`);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  try {
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let idx: number;
      while ((idx = buffer.indexOf("\n\n")) !== -1) {
        const rawEvent = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        const parsed = parseSseEvent(rawEvent);
        if (parsed) {
          const data = parsed.data ? (options?.parser ? options.parser(parsed.data) : tryJson(parsed.data)) : undefined;
          onEvent({ type: parsed.event ?? "message", data: data as T, ts: parsed.ts });
        }
      }
    }
  } catch (err) {
    if (options?.onError) options.onError(err);
    else throw err;
  } finally {
    controller.abort();
    try { reader.releaseLock(); } catch {}
  }
}

function isTerminal(status: RunStatusLike): boolean {
  return status === "succeeded" || status === "failed" || status === "cancelled";
}

type RunStatusLike = "queued" | "running" | "succeeded" | "failed" | "cancelled" | string;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseSseEvent(raw: string): { event?: string; data?: string; ts?: string } | null {
  const lines = raw.split(/\r?\n/);
  let event: string | undefined;
  let dataLines: string[] = [];
  let ts: string | undefined;
  for (const line of lines) {
    if (!line || line.startsWith(":")) continue;
    const idx = line.indexOf(":");
    const field = idx === -1 ? line : line.slice(0, idx);
    const value = idx === -1 ? "" : line.slice(idx + 1).trimStart();
    if (field === "event") event = value;
    else if (field === "data") dataLines.push(value);
    else if (field === "ts") ts = value;
  }
  const data = dataLines.length ? dataLines.join("\n") : undefined;
  if (!event && !data) return null;
  return { event, data, ts };
}

function tryJson<T = unknown>(raw: string): T | string {
  try {
    return JSON.parse(raw) as T;
  } catch {
    return raw;
  }
}

function anySignal(signals: AbortSignal[]): AbortSignal {
  const controller = new AbortController();
  const onAbort = () => controller.abort();
  for (const s of signals) {
    if (s.aborted) {
      controller.abort();
      break;
    }
    s.addEventListener("abort", onAbort);
  }
  return controller.signal;
}

async function safeReadText(resp: Response): Promise<string> {
  try {
    return await resp.text();
  } catch {
    return "";
  }
}

