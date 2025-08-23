'use client';

import React, { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import { 
  ListRegisteredNodesResponse, 
  ListGraphTemplatesResponse,
  NodeRegistration,
  UpsertGraphTemplateResponse
} from '@/types/state-manager';
import { 
  Database, 
  GitBranch, 
  RefreshCw, 
  AlertCircle,
  CheckCircle,
  Clock,
  Loader2
} from 'lucide-react';

interface NamespaceOverviewProps {
  namespace: string;
  apiKey: string;
  onOpenNode?: (node: NodeRegistration) => void;
  onOpenGraphTemplate?: (graphName: string) => void;
}

export const NamespaceOverview: React.FC<NamespaceOverviewProps> = ({
  namespace,
  apiKey,
  onOpenNode,
  onOpenGraphTemplate
}) => {
  const [nodesResponse, setNodesResponse] = useState<ListRegisteredNodesResponse | null>(null);
  const [templatesResponse, setTemplatesResponse] = useState<ListGraphTemplatesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadNamespaceData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [nodesData, templatesData] = await Promise.all([
        apiService.listRegisteredNodes(namespace, apiKey),
        apiService.listGraphTemplates(namespace, apiKey)
      ]);
      
      setNodesResponse(nodesData);
      setTemplatesResponse(templatesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load namespace data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (namespace && apiKey) {
      loadNamespaceData();
    }
  }, [namespace, apiKey]);

  const getValidationStatusColor = (status: string) => {
    switch (status) {
      case 'VALID':
        return 'text-green-600 bg-green-100';
      case 'INVALID':
        return 'text-red-600 bg-red-100';
      case 'PENDING':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-[#031035]" />
        <span className="ml-2 text-gray-600">Loading namespace data...</span>
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
            <button type="button"
              onClick={loadNamespaceData}
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
        <h2 className="text-2xl font-bold text-gray-800">Namespace Overview</h2>
        <button
          onClick={loadNamespaceData}
                      className="flex items-center space-x-2 px-4 py-2 bg-[#031035] text-white rounded-lg hover:bg-[#0a1a4a] transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Registered Nodes */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Database className="w-6 h-6 text-[#031035]" />
                <h3 className="text-lg font-semibold text-gray-800">Registered Nodes</h3>
              </div>
              <span className="text-sm text-gray-500">
                {nodesResponse?.count || 0} nodes
              </span>
            </div>
          </div>
          
          <div className="p-6">
            {nodesResponse?.nodes && nodesResponse.nodes.length > 0 ? (
              <div className="space-y-4">
                {nodesResponse.nodes.map((node, index) => (
                  <div 
                    key={index} 
                    className={`border border-gray-200 rounded-lg p-4 ${onOpenNode ? 'cursor-pointer hover:bg-gray-50 transition-colors' : ''}`}
                    onClick={() => onOpenNode?.(node)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-800">{node.name}</h4>
                      <span className="text-xs bg-[#031035]/10 text-[#031035] px-2 py-1 rounded">
                        {node.secrets.length} secrets
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="font-medium">Inputs:</span> {Object.keys(node.inputs_schema.properties || {}).length}
                        </div>
                        <div>
                          <span className="font-medium">Outputs:</span> {Object.keys(node.outputs_schema.properties || {}).length}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Database className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No registered nodes found</p>
              </div>
            )}
          </div>
        </div>

        {/* Graph Templates */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <GitBranch className="w-6 h-6 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-800">Graph Templates</h3>
              </div>
              <span className="text-sm text-gray-500">
                {templatesResponse?.count || 0} templates
              </span>
            </div>
          </div>
          
          <div className="p-6">
            {templatesResponse?.templates && templatesResponse.templates.length > 0 ? (
              <div className="space-y-4">
                {templatesResponse.templates.map((template, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-800">
                        {template.name}
                      </h4>
                      <span className={`text-xs px-2 py-1 rounded ${getValidationStatusColor(template.validation_status)}`}>
                        {template.validation_status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="font-medium">Nodes:</span> {template.nodes.length}
                        </div>
                        <div>
                          <span className="font-medium">Secrets:</span> {Object.keys(template.secrets ?? {}).length}
                        </div>
                      </div>
                      <div className="mt-2">
                        <span className="font-medium">Created:</span> {new Date(template.created_at).toLocaleDateString()}
                      </div>
                      {template.validation_errors && template.validation_errors.length > 0 && (
                        <div className="mt-2">
                          <span className="font-medium text-red-600">Errors:</span>
                          <ul className="text-xs text-red-600 mt-1">
                            {template.validation_errors.map((error, i) => (
                              <li key={i}>• {error}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {onOpenGraphTemplate && (
                        <div className="mt-3">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              // For now, we'll use a generic name since we don't have the actual graph name
                              onOpenGraphTemplate(template.name);
                            }}
                            className="text-xs bg-[#031035] text-white px-2 py-1 rounded hover:bg-[#0a1a4a] transition-colors"
                          >
                            View Details
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <GitBranch className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No graph templates found</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 bg-white rounded-lg shadow-md border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Namespace Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-[#031035]">{nodesResponse?.count || 0}</div>
            <div className="text-sm text-gray-600">Registered Nodes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{templatesResponse?.count || 0}</div>
            <div className="text-sm text-gray-600">Graph Templates</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {templatesResponse?.templates?.filter(t => t.validation_status === 'VALID').length || 0}
            </div>
            <div className="text-sm text-gray-600">Valid Templates</div>
          </div>
        </div>
      </div>
    </div>
  );
};
