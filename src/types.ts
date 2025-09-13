export interface ExosphereClientOptions {
  apiKey: string;
  baseUrl?: string;
  timeoutMs?: number;
  fetchImpl?: typeof fetch;
}

export interface EdgeDefinition {
  from: string;
  to: string;
  conditionExpression?: string;
  metadata?: Record<string, unknown>;
}

export interface NodeModelDefinition {
  key: string;
  type: string;
  model?: string;
  prompt?: string;
  config?: Record<string, unknown>;
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface GraphDefinition {
  id?: string;
  name?: string;
  description?: string;
  nodes: NodeModelDefinition[];
  edges?: EdgeDefinition[];
  metadata?: Record<string, unknown>;
}

export interface UpsertGraphResponse {
  graphId: string;
  version?: number;
  created?: boolean;
}

export interface UpsertNodeModelResponse {
  graphId: string;
  nodeKey: string;
  created?: boolean;
}

export type RunStatus = "queued" | "running" | "succeeded" | "failed" | "cancelled";

export interface TriggerRequest {
  graphId: string;
  input?: Record<string, unknown> | unknown;
  runIdempotencyKey?: string;
  startNodeKey?: string;
  metadata?: Record<string, unknown>;
}

export interface TriggerResponse {
  runId: string;
  status: RunStatus;
}

export interface Run {
  id: string;
  graphId?: string;
  status: RunStatus;
  output?: unknown;
  error?: unknown;
  createdAt?: string;
  updatedAt?: string;
  metadata?: Record<string, unknown>;
}

export interface RunEvent<T = unknown> {
  type: string;
  data: T;
  ts?: string;
}

