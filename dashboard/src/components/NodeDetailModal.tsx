'use client';

import React from 'react';
import { NodeRegistration } from '@/types/state-manager';
import { X, Code, Eye, EyeOff, Key } from 'lucide-react';

interface NodeDetailModalProps {
  node: NodeRegistration | null;
  isOpen: boolean;
  onClose: () => void;
}

const SchemaRenderer: React.FC<{ schema: any; title: string }> = ({ schema, title }) => {
  const [isExpanded, setIsExpanded] = React.useState(true);

  const renderSchemaProperties = (properties: any, required: string[] = []) => {
    return Object.entries(properties).map(([key, value]: [string, any]) => (
      <div key={key} className="border-l-2 border-gray-200 pl-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-sm font-medium text-gray-800">
              {key}
            </span>
            {required.includes(key) && (
              <span className="text-xs bg-red-100 text-red-800 px-1 py-0.5 rounded">
                required
              </span>
            )}
          </div>
          <span className="text-xs text-gray-500 font-mono">
            {value.type}
          </span>
        </div>
        {value.description && (
          <p className="text-xs text-gray-600 mt-1">{value.description}</p>
        )}
        {value.enum && (
          <div className="mt-1">
            <span className="text-xs text-gray-500">Values: </span>
            <span className="text-xs font-mono text-[#031035]">
              {value.enum.join(', ')}
            </span>
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h4 className="text-sm font-semibold text-gray-700 flex items-center">
          <Code className="w-4 h-4 mr-2" />
          {title}
        </h4>
        {isExpanded ? (
          <EyeOff className="w-4 h-4 text-gray-500" />
        ) : (
          <Eye className="w-4 h-4 text-gray-500" />
        )}
      </div>
      
      {isExpanded && (
        <div className="mt-3 space-y-2">
          {schema.properties && (
            <div>
              <h5 className="text-xs font-medium text-gray-600 mb-2">Properties:</h5>
              {renderSchemaProperties(schema.properties, schema.required || [])}
            </div>
          )}
          
          {schema.type && (
            <div className="text-xs text-gray-500">
              <span className="font-medium">Type:</span> {schema.type}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const NodeDetailModal: React.FC<NodeDetailModalProps> = ({
  node,
  isOpen,
  onClose
}) => {
  if (!isOpen || !node) return null;

  return (
    <div className="fixed inset-0 bg-white/30 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#031035] to-purple-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">{node.name}</h2>
              <p className="text-[#031035]/80 text-sm mt-1">
                Node Schema Details
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
          {/* Secrets Section */}
          {node.secrets.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                <Key className="w-5 h-5 mr-2 text-yellow-600" />
                Required Secrets
              </h3>
              <div className="flex flex-wrap gap-2">
                {node.secrets.map((secret, index) => (
                  <span
                    key={index}
                    className="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full font-medium"
                  >
                    {secret}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Input Schema */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Input Schema</h3>
            <SchemaRenderer 
              schema={node.inputs_schema} 
              title="Input Schema" 
            />
          </div>

          {/* Output Schema */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Output Schema</h3>
            <SchemaRenderer 
              schema={node.outputs_schema} 
              title="Output Schema" 
            />
          </div>

          {/* Summary */}
          <div className="bg-[#031035]/5 border border-[#031035]/20 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-[#031035] mb-2">Node Summary</h4>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-[#031035] font-medium">Secrets:</span>
                <span className="ml-2 text-[#031035]">{node.secrets.length}</span>
              </div>
              <div>
                <span className="text-[#031035] font-medium">Inputs:</span>
                <span className="ml-2 text-[#031035]">
                  {Object.keys(node.inputs_schema.properties || {}).length}
                </span>
              </div>
              <div>
                <span className="text-[#031035] font-medium">Outputs:</span>
                <span className="ml-2 text-[#031035]">
                  {Object.keys(node.outputs_schema.properties || {}).length}
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
