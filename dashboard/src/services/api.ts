import {
  RegisterNodesRequest,
  RegisterNodesResponse,
  UpsertGraphTemplateRequest,
  UpsertGraphTemplateResponse,
  CreateRequest,
  CreateResponse,
  EnqueueRequest,
  EnqueueResponse,
  ExecutedRequest,
  ExecutedResponse,
  SecretsResponse,
  ListRegisteredNodesResponse,
  ListGraphTemplatesResponse,
  CurrentStatesResponse,
  StatesByRunIdResponse,
  GraphStructureResponse,
  RunsResponse
} from '@/types/state-manager';

const API_BASE_URL = process.env.NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL || 'http://localhost:8000';

class ApiService {
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Node Registration
  async registerNodes(
    namespace: string,
    request: RegisterNodesRequest,
    apiKey: string
  ): Promise<RegisterNodesResponse> {
    return this.makeRequest<RegisterNodesResponse>(
      `/v0/namespace/${namespace}/nodes/`,
      {
        method: 'PUT',
        headers: {
          'X-API-Key': apiKey,
        },
        body: JSON.stringify(request),
      }
    );
  }

  // Graph Template Management
  async upsertGraphTemplate(
    namespace: string,
    graphName: string,
    request: UpsertGraphTemplateRequest,
    apiKey: string
  ): Promise<UpsertGraphTemplateResponse> {
    return this.makeRequest<UpsertGraphTemplateResponse>(
      `/v0/namespace/${namespace}/graph/${graphName}`,
      {
        method: 'PUT',
        headers: {
          'X-API-Key': apiKey,
        },
        body: JSON.stringify(request),
      }
    );
  }

  async getGraphTemplate(
    namespace: string,
    graphName: string,
    apiKey: string
  ): Promise<UpsertGraphTemplateResponse> {
    return this.makeRequest<UpsertGraphTemplateResponse>(
      `/v0/namespace/${namespace}/graph/${graphName}`,
      {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      }
    );
  }

  // State Management
  async createStates(
    namespace: string,
    graphName: string,
    request: CreateRequest,
    apiKey: string
  ): Promise<CreateResponse> {
    return this.makeRequest<CreateResponse>(
      `/v0/namespace/${namespace}/graph/${graphName}/states/create`,
      {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey,
        },
        body: JSON.stringify(request),
      }
    );
  }

  async enqueueStates(
    namespace: string,
    request: EnqueueRequest,
    apiKey: string
  ): Promise<EnqueueResponse> {
    return this.makeRequest<EnqueueResponse>(
      `/v0/namespace/${namespace}/states/enqueue`,
      {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey,
        },
        body: JSON.stringify(request),
      }
    );
  }

  async executeState(
    namespace: string,
    stateId: string,
    request: ExecutedRequest,
    apiKey: string
  ): Promise<ExecutedResponse> {
    return this.makeRequest<ExecutedResponse>(
      `/v0/namespace/${namespace}/states/${stateId}/executed`,
      {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey,
        },
        body: JSON.stringify(request),
      }
    );
  }

  async getSecrets(
    namespace: string,
    stateId: string,
    apiKey: string
  ): Promise<SecretsResponse> {
    return this.makeRequest<SecretsResponse>(
      `/v0/namespace/${namespace}/state/${stateId}/secrets`,
      {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      }
    );
  }

  // List Operations
  async listRegisteredNodes(
    namespace: string,
    apiKey: string
  ): Promise<ListRegisteredNodesResponse> {
    return this.makeRequest<ListRegisteredNodesResponse>(
      `/v0/namespace/${namespace}/nodes/`,
      {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      }
    );
  }

  async listGraphTemplates(
    namespace: string,
    apiKey: string
  ): Promise<ListGraphTemplatesResponse> {
    return this.makeRequest<ListGraphTemplatesResponse>(
      `/v0/namespace/${namespace}/graphs/`,
      {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      }
    );
  }

  // State Operations
  async getCurrentStates(
    namespace: string,
    apiKey: string
  ): Promise<CurrentStatesResponse> {
    return this.makeRequest<CurrentStatesResponse>(
      `/v0/namespace/${namespace}/states/`,
      {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      }
    );
  }

  async getStatesByRunId(
    namespace: string,
    runId: string,
    apiKey: string
  ): Promise<StatesByRunIdResponse> {
    return this.makeRequest<StatesByRunIdResponse>(
      `/v0/namespace/${namespace}/states/run/${runId}`,
      {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      }
    );
  }

  async getGraphStructure(
    namespace: string,
    runId: string,
    apiKey: string
  ): Promise<GraphStructureResponse> {
    return this.makeRequest<GraphStructureResponse>(
      `/v0/namespace/${namespace}/states/run/${runId}/graph`,
      {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      }
    );
  }

  // Runs endpoint
  async getRuns(
    namespace: string,
    apiKey: string,
    page: number = 1,
    size: number = 20
  ): Promise<RunsResponse> {
    return this.makeRequest<RunsResponse>(
      `/v0/namespace/${namespace}/runs/${page}/${size}`,
      {
        method: 'GET',
        headers: {
          'X-API-Key': apiKey,
        },
      }
    );
  }
}

export const apiService = new ApiService();
