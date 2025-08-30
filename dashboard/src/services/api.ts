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
  GraphStructureResponse
} from '@/types/state-manager';

const API_BASE_URL = process.env.NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL || 'http://localhost:8000';
const DEFAULT_API_KEY = process.env.NEXT_PUBLIC_EXOSPHERE_API_KEY || '';
class ApiService {
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers = new Headers(options.headers);
    headers.set('Content-Type', 'application/json');
    headers.set('x-api-key', process.env.NEXT_PUBLIC_EXOSPHERE_API_KEY || '');
  
    const response = await fetch(url, {
      ...options,
      headers,
    });
  
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('API Error:', {
        status: response.status,
        statusText: response.statusText,
        url,
        errorData
      });
      throw new Error(errorData.detail || `API request failed: ${response.statusText}`);
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
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
          'X-API-Key': DEFAULT_API_KEY,
        },
      }
    );
  }
}

export const apiService = new ApiService();
