'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { apiService } from '@/services/api';
import { 
  CurrentStatesResponse, 
  StatesByRunIdResponse,
  StateListItem 
} from '@/types/state-manager';
import { GraphVisualization } from './GraphVisualization';
import { 
  Database, 
  RefreshCw, 
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Play,
  Filter,
  Network
} from 'lucide-react';

interface StatesByRunIdProps {
  namespace: string;
  apiKey: string;
}

export const StatesByRunId: React.FC<StatesByRunIdProps> = ({
  namespace,
  apiKey
}) => {
  const [currentStates, setCurrentStates] = useState<CurrentStatesResponse | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string>('');
  const [runStates, setRunStates] = useState<StatesByRunIdResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showGraph, setShowGraph] = useState(false);

  const countsByRunId = useMemo(() => {  
  const m = new Map<string, number>();  
  currentStates?.states.forEach((s) => m.set(s.run_id, (m.get(s.run_id) ?? 0) + 1));  
  return m;  
}, [currentStates]);  

  const loadCurrentStates = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getCurrentStates(namespace, apiKey);
      setCurrentStates(data);
      
      // Auto-select the first run ID if available
      if (data.run_ids.length > 0 && !selectedRunId) {
        setSelectedRunId(data.run_ids[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load current states');
    } finally {
      setIsLoading(false);
    }
  };

  const loadStatesByRunId = async (runId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getStatesByRunId(namespace, runId, apiKey);
      setRunStates(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load states for run ID');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (namespace && apiKey) {
      loadCurrentStates();
    }
  }, [namespace, apiKey]);

  useEffect(() => {
    if (selectedRunId) {
      loadStatesByRunId(selectedRunId);
    }
  }, [selectedRunId]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CREATED':
        return <Clock className="w-4 h-4 text-[#031035]" />;
      case 'QUEUED':
        return <Loader2 className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'EXECUTED':
      case 'SUCCESS':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'ERRORED':
      case 'TIMEDOUT':
      case 'CANCELLED':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-black" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CREATED':
        return 'bg-[#031035]/10 text-[#031035]';
      case 'QUEUED':
        return 'bg-yellow-100 text-yellow-800';
      case 'EXECUTED':
      case 'SUCCESS':
        return 'bg-green-100 text-green-800';
      case 'ERRORED':
      case 'TIMEDOUT':
      case 'CANCELLED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading && !currentStates) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-[#031035]" />
        <span className="ml-2 text-gray-600">Loading states...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
            <button
              onClick={loadCurrentStates}
              className="mt-3 inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200"
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">States by Run ID</h2>
        <div className="flex items-center space-x-2">
          {selectedRunId && (
            <button
              onClick={() => setShowGraph(!showGraph)}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Network className="w-4 h-4" />
              <span>{showGraph ? 'Hide' : 'Show'} Graph</span>
            </button>
          )}
          <button
            onClick={loadCurrentStates}
            className="flex items-center space-x-2 px-4 py-2 bg-[#031035] text-white rounded-lg hover:bg-[#0a1a4a] transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Run ID Selector */}
      {currentStates && currentStates.run_ids.length > 0 && (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 mb-6">
          <div className="flex items-center space-x-2 mb-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-800">Select Run ID</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {currentStates.run_ids.map((runId) => (
              <button
                key={runId}
                onClick={() => setSelectedRunId(runId)}
                className={`p-4 rounded-lg border-2 transition-colors ${
                  selectedRunId === runId
                    ? 'border-[#031035] bg-[#031035]/5'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-sm font-medium text-gray-900 truncate">
                  {runId}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {countsByRunId.get(runId) ?? 0} states
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Graph Visualization */}
      {showGraph && selectedRunId && (
        <div className="mb-6">
                      <GraphVisualization
              namespace={namespace}
              runId={selectedRunId}
            />
        </div>
      )}

      {/* States for Selected Run ID */}
      {selectedRunId && runStates && (
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Database className="w-6 h-6 text-[#031035]" />
                <h3 className="text-lg font-semibold text-gray-800">
                  States for Run ID: {selectedRunId}
                </h3>
              </div>
              <span className="text-sm text-gray-500">
                {runStates.count} states
              </span>
            </div>
          </div>
          
          <div className="p-6">
            {runStates.states.length > 0 ? (
              <div className="space-y-4">
                {runStates.states.map((state) => (
                  <div key={state.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(state.status)}
                        <h4 className="font-medium text-gray-800">{state.node_name}</h4>
                        <span className="text-sm text-gray-500">({state.identifier})</span>
                        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                          ID: {state.id}
                        </span>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${getStatusColor(state.status)}`}>
                        {state.status}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Inputs:</span>
                        <pre className="mt-1 text-xs text-black bg-gray-50 p-2 rounded overflow-x-auto">
                          {JSON.stringify(state.inputs, null, 2)}
                        </pre>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Outputs:</span>
                        <pre className="mt-1 text-xs text-black bg-gray-50 p-2 rounded overflow-x-auto">
                          {JSON.stringify(state.outputs, null, 2)}
                        </pre>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Parents:</span>
                        <pre className="mt-1 text-xs text-black bg-gray-50 p-2 rounded overflow-x-auto">
                          {Object.keys(state.parents).length > 0 
                            ? JSON.stringify(state.parents, null, 2)
                            : 'No parents'
                          }
                        </pre>
                      </div>
                    </div>
                    
                    {state.error && (
                      <div className="mt-3">
                        <span className="font-medium text-red-700">Error:</span>
                        <div className="mt-1 text-sm text-red-600 bg-red-50 p-2 rounded">
                          {state.error}
                        </div>
                      </div>
                    )}
                    
                    <div className="mt-3 text-xs text-gray-500">
                      Created: {new Date(state.created_at).toLocaleString()}
                      {state.updated_at !== state.created_at && (
                        <span className="ml-4">
                          Updated: {new Date(state.updated_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Database className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No states found for this run ID</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Summary */}
      {currentStates && (
        <div className="mt-6 bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-[#031035]">{currentStates.count}</div>
              <div className="text-sm text-gray-600">Total States</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{currentStates.run_ids.length}</div>
              <div className="text-sm text-gray-600">Unique Run IDs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {currentStates.states.filter(s => s.status === 'SUCCESS' || s.status === 'EXECUTED').length}
              </div>
              <div className="text-sm text-gray-600">Completed States</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
