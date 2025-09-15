'use client';

import React from 'react';
import { NodeTemplate, UpsertGraphTemplateRequest } from '@/types/state-manager';
import { Plus, Trash2, Settings } from 'lucide-react';

interface GraphTemplateBuilderProps {
  graphTemplate?: UpsertGraphTemplateRequest;
  onSave?: (template: UpsertGraphTemplateRequest) => void;
  readOnly?: boolean;
}

export const GraphTemplateBuilder: React.FC<GraphTemplateBuilderProps> = ({
  graphTemplate,
  onSave,
  readOnly = false
}) => {
  const [nodes, setNodes] = React.useState<NodeTemplate[]>(
    graphTemplate?.nodes || []
  );
  const [secrets, setSecrets] = React.useState<Record<string, string>>(
    graphTemplate?.secrets || {}
  );

  const addNode = () => {
    const newNode: NodeTemplate = {
      node_name: '',
      namespace: '',
      identifier: `node_${nodes.length + 1}`,
      inputs: {},
      next_nodes: []
    };
    setNodes([...nodes, newNode]);
  };

  const updateNode = (index: number, updates: Partial<NodeTemplate>) => {
    const updatedNodes = [...nodes];
    updatedNodes[index] = { ...updatedNodes[index], ...updates };
    setNodes(updatedNodes);
  };

  const removeNode = (index: number) => {
    const updatedNodes = nodes.filter((_, i) => i !== index);
    setNodes(updatedNodes);
    
    // Update next_nodes references
    const updatedNodesWithRefs = updatedNodes.map(node => ({
      ...node,
      next_nodes: node.next_nodes.filter(ref => {
        const refIndex = nodes.findIndex(n => n.identifier === ref);
        return refIndex !== index && refIndex < updatedNodes.length;
      })
    }));
    setNodes(updatedNodesWithRefs);
  };

  const addSecret = () => {
    const key = `secret_${Object.keys(secrets).length + 1}`;
    setSecrets({ ...secrets, [key]: '' });
  };

  const updateSecret = (key: string, value: string) => {
    setSecrets({ ...secrets, [key]: value });
  };

  const removeSecret = (key: string) => {
    const newSecrets = Object.fromEntries(
      Object.entries(secrets).filter(([k]) => k !== key)
    );
    setSecrets(newSecrets);
  };

  const handleSave = () => {
    if (onSave) {
      onSave({ nodes, secrets });
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Graph Template Builder</h2>
        {!readOnly && (
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-[#031035] text-white rounded-lg hover:bg-[#0a1a4a] transition-colors"
          >
            Save Template
          </button>
        )}
      </div>

      {/* Nodes Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-700">Workflow Nodes</h3>
          {!readOnly && (
            <button
              onClick={addNode}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Node</span>
            </button>
          )}
        </div>

        <div className="space-y-4">
          {nodes.map((node, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-md font-medium text-gray-800">Node {index + 1}</h4>
                {!readOnly && (
                  <button
                    onClick={() => removeNode(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Node Name
                  </label>
                  <input
                    type="text"
                    value={node.node_name}
                    onChange={(e) => updateNode(index, { node_name: e.target.value })}
                    disabled={readOnly}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                    placeholder="Enter node name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Namespace
                  </label>
                  <input
                    type="text"
                    value={node.namespace}
                    onChange={(e) => updateNode(index, { namespace: e.target.value })}
                    disabled={readOnly}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                    placeholder="Enter namespace"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Identifier
                  </label>
                  <input
                    type="text"
                    value={node.identifier}
                    onChange={(e) => updateNode(index, { identifier: e.target.value })}
                    disabled={readOnly}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                    placeholder="Enter unique identifier"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Next Nodes (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={node.next_nodes.join(', ')}
                    onChange={(e) => updateNode(index, { 
                      next_nodes: e.target.value.split(',').map(s => s.trim()).filter(Boolean) 
                    })}
                    disabled={readOnly}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                    placeholder="node2, node3"
                  />
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Node Inputs (JSON)
                </label>
                <textarea
                  value={JSON.stringify(node.inputs, null, 2)}
                  onChange={(e) => {
                    try {
                      const inputs = JSON.parse(e.target.value);
                      updateNode(index, { inputs });
                    } catch (error) {
                      console.warn('Invalid JSON:', error);
                      // Keep the text as is for user to fix
                    }
                  }}
                  disabled={readOnly}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm disabled:bg-gray-100"
                  rows={4}
                  placeholder='{"key": "value"}'
                />
              </div>
            </div>
          ))}

          {nodes.length === 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <Settings className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No nodes yet</h3>
              <p className="text-gray-600 mb-4">Get started by adding your first workflow node.</p>
              {!readOnly && (
                <button
                  onClick={addNode}
                  className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add First Node</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Secrets Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-700">Template Secrets</h3>
          {!readOnly && (
            <button
              onClick={addSecret}
              className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Secret</span>
            </button>
          )}
        </div>

        <div className="space-y-3">
          {Object.entries(secrets).map(([key, value]) => (
            <div key={key} className="flex items-center space-x-3 bg-white border border-gray-200 rounded-lg p-3">
              <input
                type="text"
                value={key}
                onChange={(e) => {
                  const newKey = e.target.value;
                  const { [key]: oldValue, ...rest } = secrets;
                  setSecrets({ ...rest, [newKey]: oldValue });
                }}
                disabled={readOnly}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                placeholder="Secret key"
              />
              <input
                type="password"
                value={value}
                onChange={(e) => updateSecret(key, e.target.value)}
                disabled={readOnly}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                placeholder="Secret value"
              />
              {!readOnly && (
                <button
                  onClick={() => removeSecret(key)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}

          {Object.keys(secrets).length === 0 && (
            <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <p className="text-gray-600">No secrets configured for this template.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
