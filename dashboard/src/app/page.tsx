'use client';

import React, { useState, useEffect } from 'react';
import { GraphTemplateBuilder } from '@/components/GraphTemplateBuilder';
import { NamespaceOverview } from '@/components/NamespaceOverview';
import { RunsTable } from '@/components/RunsTable';
import { NodeDetailModal } from '@/components/NodeDetailModal';
import { GraphTemplateDetailModal } from '@/components/GraphTemplateDetailModal';
import { clientApiService } from '@/services/clientApi';
import {
  NodeRegistration, 
  UpsertGraphTemplateRequest,
  UpsertGraphTemplateResponse,
  ListNamespacesResponse,
} from '@/types/state-manager';
import { 
  GitBranch, 
  BarChart3,
  AlertCircle,
  Filter
} from 'lucide-react';

// Shadcn components
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState< 'overview' | 'graph' |'runs'>('overview');
  const [namespace, setNamespace] = useState('default');
  const [availableNamespaces, setAvailableNamespaces] = useState<string[]>([]);
  const [graphName, setGraphName] = useState('test-graph');
  const [graphTemplate, setGraphTemplate] = useState<UpsertGraphTemplateRequest | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [selectedNode, setSelectedNode] = useState<NodeRegistration | null>(null);
  const [isNodeModalOpen, setIsNodeModalOpen] = useState(false);
  const [selectedGraphTemplate, setSelectedGraphTemplate] = useState<UpsertGraphTemplateResponse | null>(null);
  const [isGraphModalOpen, setIsGraphModalOpen] = useState(false);

  // Fetch configuration and namespaces on component mount
  useEffect(() => {
    const fetchConfigAndNamespaces = async () => {
      try {
        // Fetch configuration
        const configResponse = await fetch('/api/config');
        if (configResponse.ok) {
          const config = await configResponse.json();
          setNamespace(config.defaultNamespace);
        }

        // Fetch available namespaces
        const namespacesData = await clientApiService.getNamespaces();
        setAvailableNamespaces(namespacesData.namespaces || []);
        
        // If no namespaces available and we have a default, add it
        if (namespacesData.namespaces?.length === 0) {
          setAvailableNamespaces(['default']);
        }
      } catch (error) {
        console.warn('Failed to fetch config or namespaces, using defaults');
        setAvailableNamespaces(['default']);
      }
    };

    fetchConfigAndNamespaces();
  }, []);

  const handleSaveGraphTemplate = async (template: UpsertGraphTemplateRequest) => {
    try {
      await clientApiService.upsertGraphTemplate(namespace, graphName, template);
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
      const graphTemplate = await clientApiService.getGraphTemplate(namespace, graphName);
      graphTemplate.name = graphName;
      graphTemplate.namespace = namespace;
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

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <img src="/exospheresmall.png" alt="Exosphere Logo" className="w-8 h-8" />
                <div>
                  <h1 className="text-xl font-bold text-foreground">Exosphere Dashboard</h1>
                  <p className="text-sm text-muted-foreground">AI Workflow State Manager</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-muted-foreground">Namespace:</span>
                <Select
                  value={namespace}
                  onChange={(e) => setNamespace(e.target.value)}
                  className="w-32 h-8"
                >
                  {availableNamespaces.map((ns) => (
                    <option key={ns} value={ns}>
                      {ns}
                    </option>
                  ))}
                  {/* Show current namespace even if not in the list */}
                  {!availableNamespaces.includes(namespace) && (
                    <option key={namespace} value={namespace}>
                      {namespace}
                    </option>
                  )}
                </Select>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Error Display */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <Alert className="mb-6">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
              <AlertDescription className="ml-2">Processing...</AlertDescription>
            </div>
          </Alert>
        )}

        {/* Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'overview' | 'runs')} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-8">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>Overview</span>
            </TabsTrigger>
            {/* <TabsTrigger value="graph" className="flex items-center space-x-2">
              <GitBranch className="w-4 h-4" />
              <span>Graph Template</span>
            </TabsTrigger> */}
            <TabsTrigger value="runs" className="flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <span>Runs</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardContent>
                <NamespaceOverview
                  namespace={namespace}
                  onOpenNode={handleOpenNodeModal}
                  onOpenGraphTemplate={handleOpenGraphModal}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="graph" className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6">
                <div>
                  <CardTitle>Graph Template Builder</CardTitle>
                  <CardDescription>
                    Design and configure your AI workflow graph templates
                  </CardDescription>
                </div>
                {graphTemplate && (
                  <Button
                    onClick={() => handleOpenGraphModal(graphName)}
                    variant="outline"
                  >
                    View Template
                  </Button>
                )}
              </CardHeader>
              <CardContent>
                <GraphTemplateBuilder
                  graphTemplate={graphTemplate || undefined}
                  onSave={handleSaveGraphTemplate}
                  readOnly={false}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="runs" className="space-y-6">
            <Card>
              <CardContent>
                <RunsTable namespace={namespace} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
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
