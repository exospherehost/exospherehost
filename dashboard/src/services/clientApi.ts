// Client-side API service that calls our server-side routes
// This keeps sensitive information like API keys on the server side
import { UpsertGraphTemplateRequest } from '@/types/state-manager';

export class ClientApiService {
  // Runs
  async getRuns(namespace: string, page: number = 1, size: number = 20) {
    const response = await fetch(`/api/runs?namespace=${encodeURIComponent(namespace)}&page=${page}&size=${size}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch runs: ${response.statusText}`);
    }
    return response.json();
  }

  // Graph Structure
  async getGraphStructure(namespace: string, runId: string) {
    const response = await fetch(`/api/graph-structure?namespace=${encodeURIComponent(namespace)}&runId=${encodeURIComponent(runId)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch graph structure: ${response.statusText}`);
    }
    return response.json();
  }

  // Namespace Overview
  async getNamespaceOverview(namespace: string) {
    const response = await fetch(`/api/namespace-overview?namespace=${encodeURIComponent(namespace)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch namespace overview: ${response.statusText}`);
    }
    return response.json();
  }

  // Graph Template
  async getGraphTemplate(namespace: string, graphName: string) {
    const response = await fetch(`/api/graph-template?namespace=${encodeURIComponent(namespace)}&graphName=${encodeURIComponent(graphName)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch graph template: ${response.statusText}`);
    }
    return response.json();
  }

  async upsertGraphTemplate(namespace: string, graphName: string, template: UpsertGraphTemplateRequest) {
    const response = await fetch(`/api/graph-template?namespace=${encodeURIComponent(namespace)}&graphName=${encodeURIComponent(graphName)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(template),
    });
    if (!response.ok) {
      throw new Error(`Failed to update graph template: ${response.statusText}`);
    }
    return response.json();
  }
}

export const clientApiService = new ClientApiService(); 