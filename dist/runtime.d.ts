import type { Run, RunEvent } from "./types.js";
import { ExosphereClient } from "./client.js";
export interface AwaitRunOptions {
    pollIntervalMs?: number;
    maxWaitMs?: number;
    onUpdate?: (run: Run) => void;
}
export declare function awaitRun(client: ExosphereClient, runId: string, options?: AwaitRunOptions): Promise<Run>;
export interface StreamRunEventsOptions<T = unknown> {
    signal?: AbortSignal;
    onError?: (error: unknown) => void;
    parser?: (raw: string) => T;
}
export declare function streamRunEvents<T = unknown>(client: ExosphereClient, runId: string, onEvent: (event: RunEvent<T>) => void, options?: StreamRunEventsOptions<T>): Promise<void>;
