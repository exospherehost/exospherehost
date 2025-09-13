import type {
  ExosphereClientOptions,
  GraphDefinition,
  NodeModelDefinition,
  Run,
  TriggerRequest,
  TriggerResponse,
  UpsertGraphResponse,
  UpsertNodeModelResponse,
} from "./types.js";

function trimTrailingSlash(url: string): string {
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

export class ExosphereClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly timeoutMs: number;
  private readonly fetchImpl: typeof fetch;

  constructor(options: ExosphereClientOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = trimTrailingSlash(options.baseUrl ?? "https://api.exosphere.host");
    this.timeoutMs = options.timeoutMs ?? 300_000; // 5 minutes default
    this.fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
    if (typeof this.fetchImpl !== "function") {
      throw new Error("No fetch implementation available. Provide options.fetchImpl on Node <18.");
    }
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }

  getAuthHeaders(): Record<string, string> {
    return {
      Authorization: `Bearer ${this.apiKey}`,
    };
  }

  private mergeHeaders(extra?: HeadersInit): HeadersInit {
    return {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...this.getAuthHeaders(),
      ...(extra as Record<string, string>),
    };
  }

  private withTimeout(init?: RequestInit, timeoutMs?: number): { init: RequestInit; controller: AbortController } {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs ?? this.timeoutMs);
    const combined = {
      ...init,
      signal: init?.signal ? this.anySignal([init.signal, controller.signal]) : controller.signal,
    } as RequestInit;
    // clear timeout on settled
    const cleanup = () => clearTimeout(timeout);
    // Attach then/catch cleanup where used
    (combined as any).__cleanupTimeout = cleanup;
    return { init: combined, controller };
  }

  private anySignal(signals: AbortSignal[]): AbortSignal {
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

  async requestRaw(path: string, init?: RequestInit): Promise<Response> {
    const url = `${this.baseUrl}${path.startsWith("/") ? "" : "/"}${path}`;
    const { init: withSig } = this.withTimeout({
      ...init,
      headers: this.mergeHeaders(init?.headers),
    });
    const resp = await this.fetchImpl(url, withSig);
    return resp;
  }

  async requestJson<T>(path: string, init?: RequestInit): Promise<T> {
    const resp = await this.requestRaw(path, init);
    if (!resp.ok) {
      const text = await safeReadText(resp);
      throw new Error(`HTTP ${resp.status} ${resp.statusText}: ${text}`);
    }
    const contentType = resp.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      return (await resp.json()) as T;
    }
    const text = await resp.text();
    try {
      return JSON.parse(text) as T;
    } catch {
      throw new Error(`Expected JSON response but got: ${contentType || "unknown"}`);
    }
  }

  async upsertGraph(graph: GraphDefinition): Promise<UpsertGraphResponse> {
    return this.requestJson<UpsertGraphResponse>("/v1/graphs/upsert", {
      method: "POST",
      body: JSON.stringify({ graph }),
    });
  }

  async upsertNodeModel(graphId: string, node: NodeModelDefinition): Promise<UpsertNodeModelResponse> {
    return this.requestJson<UpsertNodeModelResponse>(`/v1/graphs/${encodeURIComponent(graphId)}/nodes/upsert`, {
      method: "POST",
      body: JSON.stringify({ node }),
    });
  }

  async trigger(request: TriggerRequest): Promise<TriggerResponse> {
    return this.requestJson<TriggerResponse>("/v1/runs/trigger", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getRun(runId: string): Promise<Run> {
    return this.requestJson<Run>(`/v1/runs/${encodeURIComponent(runId)}`);
  }

  async cancelRun(runId: string): Promise<{ cancelled: boolean } | Run> {
    return this.requestJson(`/v1/runs/${encodeURIComponent(runId)}/cancel`, {
      method: "POST",
    });
  }
}

async function safeReadText(resp: Response): Promise<string> {
  try {
    return await resp.text();
  } catch {
    return "";
  }
}

