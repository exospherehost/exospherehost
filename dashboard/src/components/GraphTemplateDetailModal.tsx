'use client';

import React from 'react';
import { UpsertGraphTemplateResponse, NodeTemplate } from '@/types/state-manager';
import { X, GitBranch, Settings, ArrowRight, Key } from 'lucide-react';

interface GraphTemplateDetailModalProps {
  graphTemplate: UpsertGraphTemplateResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

const GraphVisualizer: React.FC<{ nodes: NodeTemplate[] }> = ({ nodes }) => {
  const renderNode = (node: NodeTemplate, index: number) => {
    const connections = node.next_nodes.map(nextNodeId => {
      const nextNodeIndex = nodes.findIndex(n => n.identifier === nextNodeId);
      return { from: index, to: nextNodeIndex, label: nextNodeId };
    });

    return (
      <div key={index} className="relative">
        <div className="bg-white border-2 border-[#031035]/30 rounded-lg p-4 shadow-md">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-gray-800 text-sm">
              {node.identifier}
            </h4>
            <span className="text-xs bg-[#031035]/10 text-[#031035] px-2 py-1 rounded">
              {index + 1}
            </span>
          </div>
          <div className="text-xs text-gray-600 space-y-1">
            <div><span className="font-medium">Node:</span> {node.node_name}</div>
            <div><span className="font-medium">Namespace:</span> {node.namespace}</div>
            <div><span className="font-medium">Inputs:</span> {Object.keys(node.inputs).length}</div>
          </div>
        </div>
        
        {/* Connection lines */}
        {connections.map((connection, connIndex) => (
          <div key={connIndex} className="absolute top-1/2 left-full w-8 h-0.5 bg-[#031035]/30 transform -translate-y-1/2">
            <ArrowRight className="absolute right-0 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#031035]/30" />
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
        <GitBranch className="w-4 h-4 mr-2" />
        Graph Structure
      </h4>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {nodes.map((node, index) => renderNode(node, index))}
      </div>
      
      {nodes.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Settings className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No nodes in this graph template.</p>
        </div>
      )}
    </div>
  );
};

const NodeDetailView: React.FC<{ node: NodeTemplate; index: number }> = ({ node, index }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-medium text-gray-800">
          Node {index + 1}: {node.identifier}
        </h4>
                    <span className="text-xs bg-[#031035]/10 text-[#031035] px-2 py-1 rounded">
          {index + 1}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Node Name
          </label>
          <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md font-mono">
            {node.node_name}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Namespace
          </label>
          <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md font-mono">
            {node.namespace}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Identifier
          </label>
          <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md font-mono">
            {node.identifier}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Next Nodes
          </label>
          <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md font-mono">
            {node.next_nodes.length > 0 ? node.next_nodes.join(', ') : 'None'}
          </div>
        </div>
      </div>

      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Inputs (JSON)
        </label>
        <pre className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md text-xs overflow-x-auto">
          {JSON.stringify(node.inputs, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export const GraphTemplateDetailModal: React.FC<GraphTemplateDetailModalProps> = ({
  graphTemplate,
  isOpen,
  onClose
}) => {
  if (!isOpen || !graphTemplate) return null;

  return (
    <div className="fixed inset-0 bg-white/30 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-500 to-[#031035] p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Graph Template</h2>
              <p className="text-green-100 text-sm mt-1">
                Created: {new Date(graphTemplate.created_at).toLocaleString()}
              </p>
              <p className="text-green-100 text-sm">
                Updated: {new Date(graphTemplate.updated_at).toLocaleString()}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Validation Status */}
          <div className={`p-4 rounded-lg border ${
            graphTemplate.validation_status === 'VALID' 
              ? 'bg-green-50 border-green-200' 
              : graphTemplate.validation_status === 'INVALID'
              ? 'bg-red-50 border-red-200'
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-3 ${
                graphTemplate.validation_status === 'VALID' 
                  ? 'bg-green-500' 
                  : graphTemplate.validation_status === 'INVALID'
                  ? 'bg-red-500'
                  : 'bg-yellow-500'
              }`} />
              <div>
                <h3 className="font-semibold text-gray-800">
                  Validation Status: {graphTemplate.validation_status}
                </h3>
                {graphTemplate.validation_errors && graphTemplate.validation_errors.length > 0 && (
                  <div className="mt-2">
                    <p className="text-sm font-medium text-red-800 mb-1">Validation Errors:</p>
                    <ul className="text-sm text-red-700 space-y-1">
                      {graphTemplate.validation_errors.map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Graph Visualization */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Graph Structure</h3>
            <GraphVisualizer nodes={graphTemplate.nodes} />
          </div>

          {/* Secrets */}
          {Object.keys(graphTemplate.secrets).length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                <Key className="w-5 h-5 mr-2 text-yellow-600" />
                Secrets Configuration
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(graphTemplate.secrets).map(([key, isConfigured]) => (
                  <div key={key} className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                    <span className="font-mono text-sm">{key}</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      isConfigured 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {isConfigured ? 'Configured' : 'Missing'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Node Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Node Details</h3>
            <div className="space-y-4">
              {graphTemplate.nodes.map((node, index) => (
                <NodeDetailView key={index} node={node} index={index} />
              ))}
            </div>
          </div>

          {/* Summary */}
          <div className="bg-[#031035]/5 border border-[#031035]/20 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-[#031035] mb-2">Graph Summary</h4>
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-[#031035] font-medium">Nodes:</span>
                <span className="ml-2 text-[#031035]">{graphTemplate.nodes.length}</span>
              </div>
              <div>
                <span className="text-[#031035] font-medium">Secrets:</span>
                <span className="ml-2 text-[#031035]">{Object.keys(graphTemplate.secrets).length}</span>
              </div>
              <div>
                <span className="text-[#031035] font-medium">Status:</span>
                <span className="ml-2 text-[#031035]">{graphTemplate.validation_status}</span>
              </div>
              <div>
                <span className="text-[#031035] font-medium">Connections:</span>
                <span className="ml-2 text-[#031035]">
                  {graphTemplate.nodes.reduce((total, node) => total + node.next_nodes.length, 0)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 rounded-b-lg">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
