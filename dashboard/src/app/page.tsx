'use client';

import React, { useState, useEffect } from 'react';
import { GraphTemplateBuilder } from '@/components/GraphTemplateBuilder';
import { NamespaceOverview } from '@/components/NamespaceOverview';
import { StatesByRunId } from '@/components/StatesByRunId';
import { NodeDetailModal } from '@/components/NodeDetailModal';
import { GraphTemplateDetailModal } from '@/components/GraphTemplateDetailModal';
import { apiService } from '@/services/api';
import {
  NodeRegistration, 
  ResponseState, 
  UpsertGraphTemplateRequest,
  UpsertGraphTemplateResponse,
} from '@/types/state-manager';
import { 
  GitBranch, 
  BarChart3,
  AlertCircle,
  Filter
} from 'lucide-react';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState< 'overview' | 'graph' |'run-states'>('overview');
  const [namespace, setNamespace] = useState('testnamespace');
  const [apiKey, setApiKey] = useState('');
  const [runtimeName, setRuntimeName] = useState('test-runtime');
  const [graphName, setGraphName] = useState('test-graph');
  
  
  const [currentStep, setCurrentStep] = useState(0);
  const [registeredNodes, setRegisteredNodes] = useState<NodeRegistration[]>([]);
  const [graphTemplate, setGraphTemplate] = useState<UpsertGraphTemplateRequest | null>(null);
  const [states, setStates] = useState<ResponseState[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [selectedNode, setSelectedNode] = useState<NodeRegistration | null>(null);
  const [isNodeModalOpen, setIsNodeModalOpen] = useState(false);
  const [selectedGraphTemplate, setSelectedGraphTemplate] = useState<UpsertGraphTemplateResponse | null>(null);
  const [isGraphModalOpen, setIsGraphModalOpen] = useState(false);

  const handleSaveGraphTemplate = async (template: UpsertGraphTemplateRequest) => {
    try {
      await apiService.upsertGraphTemplate(namespace, graphName, template, apiKey);
      setGraphTemplate(template);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save graph template');
    }
  };

  // Modal handlers
  const handleOpenNodeModal = (node: NodeRegistration) => {
    setSelectedNode(node);
    setIsNodeModalOpen(true);
  };

  const handleCloseNodeModal = () => {
    setIsNodeModalOpen(false);
    setSelectedNode(null);
  };

  const handleOpenGraphModal = async (graphName: string) => {
    try {
      setIsLoading(true);
      const graphTemplate = await apiService.getGraphTemplate(namespace, graphName, apiKey);
      setSelectedGraphTemplate(graphTemplate);
      setIsGraphModalOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load graph template');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseGraphModal = () => {
    setIsGraphModalOpen(false);
    setSelectedGraphTemplate(null);
  };

  const tabs = [    
    { id: 'overview', label: 'Overview', icon: BarChart3 },    
    { id: 'graph', label: 'Graph Template', icon: GitBranch },    
    { id: 'run-states', label: 'Run States', icon: Filter }
  ] as const;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-[#031035] shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <img src="/exospheresmall.png" alt="Exosphere Logo" className="w-8 h-8" />
                <h1 className="text-xl font-bold text-white">Exosphere Dashboard</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-white">Namespace:</span>
                <input
                  type="text"
                  value={namespace}
                  onChange={(e) => setNamespace(e.target.value)}
                  className="px-2 py-1 text-sm text-white border border-gray-300 rounded"
                />
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-white">API Key:</span>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="px-2 py-1 text-sm text-white border border-gray-300 rounded"
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-[#031035] text-[#031035]'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="mb-6 bg-[#031035]/10 border border-[#031035]/20 rounded-md p-4">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#031035]"></div>
              <span className="ml-2 text-sm text-[#031035]">Processing...</span>
            </div>
          </div>
        )}


        {activeTab === 'graph' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Graph Template Builder</h2>
              {graphTemplate && (
                <button
                  onClick={() => handleOpenGraphModal(graphName)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  View Graph Template
                </button>
              )}
            </div>
            <GraphTemplateBuilder
              graphTemplate={graphTemplate || undefined}
              onSave={handleSaveGraphTemplate}
              readOnly={false}
            />
          </div>
        )}

        {activeTab === 'overview' && (
          <NamespaceOverview
            namespace={namespace}
            apiKey={apiKey}
            onOpenNode={handleOpenNodeModal}
            onOpenGraphTemplate={handleOpenGraphModal}
          />
        )}

        {activeTab === 'run-states' && (
          <StatesByRunId
            namespace={namespace}
            apiKey={apiKey}
          />
        )}
      </main>

      {/* Modals */}
      <NodeDetailModal
        node={selectedNode}
        isOpen={isNodeModalOpen}
        onClose={handleCloseNodeModal}
      />
      
      <GraphTemplateDetailModal
        graphTemplate={selectedGraphTemplate}
        isOpen={isGraphModalOpen}
        onClose={handleCloseGraphModal}
      />
    </div>
  );
}
