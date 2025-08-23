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
  const [editingNode, setEditingNode] = React.useState<number | null>(null);

  const addNode = () => {
    const newNode: NodeTemplate = {
      node_name: '',
      namespace: '',
      identifier: `node_${nodes.length + 1}`,
      inputs: {},
      next_nodes: []
    };
    setNodes([...nodes, newNode]);
    setEditingNode(nodes.length);
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
    const { [key]: removed, ...remaining } = secrets;
    setSecrets(remaining);
  };

  const handleSave = () => {
    if (onSave) {
      onSave({ nodes, secrets });
    }
  };

  const getNodeConnections = (nodeIndex: number) => {
    const node = nodes[nodeIndex];
    if (!node) return [];
    
    return node.next_nodes.map(nextNodeId => {
      const nextNodeIndex = nodes.findIndex(n => n.identifier === nextNodeId);
      return { from: nodeIndex, to: nextNodeIndex, label: nextNodeId };
    });
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Nodes Section */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Nodes</h3>
              {!readOnly && (
                <button
                  onClick={addNode}
                  className="flex items-center space-x-2 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Node</span>
                </button>
              )}
            </div>

            <div className="space-y-4">
              {nodes.map((node, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-800">
                      Node {index + 1}: {node.identifier}
                    </h4>
                    {!readOnly && (
                      <button
                        onClick={() => removeNode(index)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#031035]"
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#031035]"
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Next Nodes
                      </label>
                      <input
                        type="text"
                        value={node.next_nodes.join(', ')}
                        onChange={(e) => updateNode(index, { 
                          next_nodes: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                        })}
                        disabled={readOnly}
                        placeholder="node1, node2, node3"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#031035]"
                      />
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Inputs (JSON)
                    </label>
                    <textarea
                      value={JSON.stringify(node.inputs, null, 2)}
                      onChange={(e) => {
                        try {
                          const inputs = JSON.parse(e.target.value);
                          updateNode(index, { inputs });
                        } catch (error) {
                          // Invalid JSON, ignore
                        }
                      }}
                      disabled={readOnly}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#031035] font-mono text-sm"
                    />
                  </div>
                </div>
              ))}
            </div>

            {nodes.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Settings className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No nodes added yet. Click &quot;Add Node&quot; to get started.</p>
              </div>
            )}
          </div>
        </div>

        {/* Secrets Section */}
        <div>
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Secrets</h3>
              {!readOnly && (
                <button
                  onClick={addSecret}
                  className="flex items-center space-x-2 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Secret</span>
                </button>
              )}
            </div>

            <div className="space-y-3">
              {Object.entries(secrets).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={key}
                    onChange={(e) => {
                      const newSecrets = { ...secrets };
                      delete newSecrets[key];
                      newSecrets[e.target.value] = value;
                      setSecrets(newSecrets);
                    }}
                    disabled={readOnly}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#031035] text-sm"
                  />
                  <span className="text-gray-500">:</span>
                  <input
                    type="password"
                    value={value}
                    onChange={(e) => updateSecret(key, e.target.value)}
                    disabled={readOnly}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#031035] text-sm"
                  />
                  {!readOnly && (
                    <button
                      onClick={() => removeSecret(key)}
                      className="p-1 text-red-600 hover:bg-red-50 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {Object.keys(secrets).length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <p>No secrets configured.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
