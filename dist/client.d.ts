import type { ExosphereClientOptions, GraphDefinition, NodeModelDefinition, Run, TriggerRequest, TriggerResponse, UpsertGraphResponse, UpsertNodeModelResponse } from "./types.js";
export declare class ExosphereClient {
    private readonly baseUrl;
    private readonly apiKey;
    private readonly timeoutMs;
    private readonly fetchImpl;
    constructor(options: ExosphereClientOptions);
    getBaseUrl(): string;
    getAuthHeaders(): Record<string, string>;
    private mergeHeaders;
    private withTimeout;
    private anySignal;
    requestRaw(path: string, init?: RequestInit): Promise<Response>;
    requestJson<T>(path: string, init?: RequestInit): Promise<T>;
    upsertGraph(graph: GraphDefinition): Promise<UpsertGraphResponse>;
    upsertNodeModel(graphId: string, node: NodeModelDefinition): Promise<UpsertNodeModelResponse>;
    trigger(request: TriggerRequest): Promise<TriggerResponse>;
    getRun(runId: string): Promise<Run>;
    cancelRun(runId: string): Promise<{
        cancelled: boolean;
    } | Run>;
}
