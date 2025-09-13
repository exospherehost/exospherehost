import { ExosphereClient } from "./client.js";
import type { GraphNodeModel, RetryPolicyModel, TriggerResponse } from "./types.js";

export interface UpsertGraphParams {
  graph_name: string;
  graph_nodes: GraphNodeModel[];
  secrets?: Record<string, string>;
  retry_policy?: RetryPolicyModel;
}

export class StateManager {
  private readonly client: ExosphereClient;
  private readonly namespace: string;

  constructor(client: ExosphereClient, namespace: string) {
    this.client = client;
    this.namespace = namespace;
  }

  async upsert_graph(params: UpsertGraphParams): Promise<{ graph_name: string; created?: boolean }> {
    // Follows Python naming and payload keys
    return this.client.requestJson<{ graph_name: string; created?: boolean }>("/v1/graphs/upsert", {
      method: "POST",
      body: JSON.stringify({
        namespace: this.namespace,
        graph_name: params.graph_name,
        graph_nodes: params.graph_nodes,
        secrets: params.secrets ?? {},
        retry_policy: params.retry_policy,
      }),
    });
  }

  async trigger(graph_name: string, input?: Record<string, unknown> | unknown): Promise<TriggerResponse> {
    return this.client.requestJson<TriggerResponse>("/v1/runs/trigger", {
      method: "POST",
      body: JSON.stringify({ namespace: this.namespace, graph_name, input }),
    });
  }
}

