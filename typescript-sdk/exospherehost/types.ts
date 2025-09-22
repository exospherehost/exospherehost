export interface TriggerState {
  identifier: string;
  inputs: Record<string, string>;
}

export interface GraphNode {
  node_name: string;
  identifier: string;
  inputs: Record<string, unknown>;
  next_nodes?: string[];
  namespace?: string;
}

export enum GraphValidationStatus {
  VALID = 'VALID',
  INVALID = 'INVALID',
  PENDING = 'PENDING'
}
