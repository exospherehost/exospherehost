export interface NodeRegistration {
  name: string;
  inputs_schema: Record<string, unknown>;
  outputs_schema: Record<string, unknown>;
  secrets: string[];
}

export interface RegisterNodesRequest {
  runtime_name: string;
  nodes: NodeRegistration[];
}

export interface RegisterNodesResponse {
  runtime_name: string;
  registered_nodes: NodeRegistration[];
}

export interface NodeTemplate {
  node_name: string;
  namespace: string;
  identifier: string;
  inputs: Record<string, unknown>;
  next_nodes: string[];
}

export interface UpsertGraphTemplateRequest {
  secrets: Record<string, string>;
  nodes: NodeTemplate[];
}

export interface UpsertGraphTemplateResponse {
  name: string;
  namespace: string;
  nodes: NodeTemplate[];
  secrets: Record<string, boolean>;
  created_at: string;
  updated_at: string;
  validation_status: GraphTemplateValidationStatus;
  validation_errors?: string[];
}

export enum GraphTemplateValidationStatus {
  VALID = 'VALID',
  INVALID = 'INVALID',
  PENDING = 'PENDING'
}

export interface RequestState {
  identifier: string;
  inputs: Record<string, unknown>;
}

export interface ResponseState {
  state_id: string;
  node_name: string;
  identifier: string;
  graph_name: string;
  run_id: string;
  inputs: Record<string, unknown>;
  created_at: string;
}

export interface CreateRequest {
  run_id: string;
  states: RequestState[];
}

export interface CreateResponse {
  status: StateStatus;
  states: ResponseState[];
}

export enum StateStatus {
  CREATED = 'CREATED',
  QUEUED = 'QUEUED',
  EXECUTED = 'EXECUTED',
  NEXT_CREATED = 'NEXT_CREATED',
  RETRY_CREATED = 'RETRY_CREATED',
  TIMEDOUT = 'TIMEDOUT',
  ERRORED = 'ERRORED',
  CANCELLED = 'CANCELLED',
  SUCCESS = 'SUCCESS'
}

export interface EnqueueRequest {
  nodes: string[];
  batch_size: number;
}

export interface EnqueueResponse {
  status: string;
  namespace: string;
  count: number;
  states: Array<{
    state_id: string;
    node_name: string;
    identifier: string;
    inputs: Record<string, unknown>;
  }>;
}

export interface ExecutedRequest {
  outputs: Record<string, unknown>[];
}

export interface ExecutedResponse {
  status: StateStatus;
}

export interface SecretsResponse {
  secrets: Record<string, string>;
}

export interface ListRegisteredNodesResponse {
  namespace: string;
  count: number;
  nodes: NodeRegistration[];
}

export interface ListGraphTemplatesResponse {
  namespace: string;
  count: number;
  templates: UpsertGraphTemplateResponse[];
}

export interface StateListItem {
  id: string;
  node_name: string;
  namespace_name: string;
  identifier: string;
  graph_name: string;
  run_id: string;
  status: StateStatus;
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  error?: string;
  parents: Record<string, string>;
  created_at: string;
  updated_at: string;
}



export interface WorkflowStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  data?: unknown;
}

export interface WorkflowState {
  namespace: string;
  apiKey: string;
  runtimeName: string;
  graphName: string;
  steps: WorkflowStep[];
  currentStep: number;
}

// Graph Structure Types
export interface GraphNode {
  id: string;
  node_name: string;
  identifier: string;
  status: StateStatus;
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  error?: string;
  created_at: string;
  updated_at: string;
  position?: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  source_output?: string;
  target_input?: string;
}

export interface GraphStructureResponse {
  namespace: string;
  run_id: string;
  graph_name: string;
  root_nodes: GraphNode[];
  nodes: GraphNode[];
  edges: GraphEdge[];
  node_count: number;
  edge_count: number;
  execution_summary: Record<string, number>;
}

// Runs Types
export enum RunStatusEnum {
  SUCCESS = "SUCCESS",
  PENDING = "PENDING",
  FAILED = "FAILED"
}

export interface RunListItem {
  run_id: string;
  graph_name: string;
  success_count: number;
  pending_count: number;
  errored_count: number;
  retried_count: number;
  total_count: number;
  status: RunStatusEnum;
  created_at: string;
}

export interface RunsResponse {
  namespace: string;
  total: number;
  page: number;
  size: number;
  runs: RunListItem[];
}
