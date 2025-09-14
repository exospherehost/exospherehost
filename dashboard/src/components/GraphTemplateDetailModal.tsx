'use client';

import React from 'react';
import { UpsertGraphTemplateResponse, NodeTemplate } from '@/types/state-manager';
import { X, GitBranch, Settings, ArrowRight, Key, Code, Database, Workflow, Clock } from 'lucide-react';

// Shadcn components
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface GraphTemplateDetailModalProps {
  graphTemplate: UpsertGraphTemplateResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

const RETRY_STRATEGIES = [
  { value: 'EXPONENTIAL', label: 'Exponential' },
  { value: 'EXPONENTIAL_FULL_JITTER', label: 'Exponential Full Jitter' },
  { value: 'EXPONENTIAL_EQUAL_JITTER', label: 'Exponential Equal Jitter' },
  { value: 'LINEAR', label: 'Linear' },
  { value: 'LINEAR_FULL_JITTER', label: 'Linear Full Jitter' },
  { value: 'LINEAR_EQUAL_JITTER', label: 'Linear Equal Jitter' },
  { value: 'FIXED', label: 'Fixed' },
  { value: 'FIXED_FULL_JITTER', label: 'Fixed Full Jitter' },
  { value: 'FIXED_EQUAL_JITTER', label: 'Fixed Equal Jitter' },
];

const GraphVisualizer: React.FC<{ nodes: NodeTemplate[] }> = ({ nodes }) => {
  const renderNode = (node: NodeTemplate, index: number) => {
    const connections = node.next_nodes.map(nextNodeId => {
      const nextNodeIndex = nodes.findIndex(n => n.identifier === nextNodeId);
      return { from: index, to: nextNodeIndex, label: nextNodeId };
    });

    return (
      <div key={index} className="relative">
        <Card className="border-2 border-primary/30 shadow-md">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm">{node.identifier}</CardTitle>
              <Badge variant="outline" className="text-xs">
                {index + 1}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-xs text-muted-foreground space-y-1">
              <div><span className="font-medium">Node:</span> {node.node_name}</div>
              <div><span className="font-medium">Namespace:</span> {node.namespace}</div>
              <div><span className="font-medium">Inputs:</span> {Object.keys(node.inputs).length}</div>
            </div>
          </CardContent>
        </Card>
        
        {/* Connection lines */}
        {connections.map((connection, connIndex) => (
          <div key={connIndex} className="absolute top-1/2 left-full w-8 h-0.5 bg-primary/30 transform -translate-y-1/2">
            <ArrowRight className="absolute right-0 top-1/2 transform -translate-y-1/2 w-4 h-4 text-primary" />
          </div>
        ))}
      </div>
    );
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center space-x-2">
          <GitBranch className="w-4 h-4" />
          <span>Graph Structure</span>
        </CardTitle>
        <CardDescription>Visual representation of the workflow nodes</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {nodes.map((node, index) => renderNode(node, index))}
        </div>
        
        {nodes.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <Settings className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No nodes in this graph template.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const NodeDetailView: React.FC<{ node: NodeTemplate; index: number }> = ({ node, index }) => {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">
            Node {index + 1}: {node.identifier}
          </CardTitle>
          <Badge variant="outline" className="text-xs">
            {index + 1}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground">Node Name</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {node.node_name}
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground">Namespace</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {node.namespace}
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground">Identifier</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {node.identifier}
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground">Next Nodes</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {node.next_nodes.length > 0 ? node.next_nodes.join(', ') : 'None'}
            </div>
          </div>
        </div>

        <div>
          <label className="text-xs font-medium text-muted-foreground mb-2 block">Node Inputs</label>
          <div className="bg-muted p-3 rounded border max-h-32 overflow-y-auto">
            <pre className="text-xs font-mono text-foreground whitespace-pre-wrap">
              {JSON.stringify(node.inputs, null, 2)}
            </pre>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const RetryPolicyViewer: React.FC<{ 
  retryPolicy: any;
}> = ({ retryPolicy }) => {
  const getStrategyLabel = (strategy: string) => {
    return RETRY_STRATEGIES.find(s => s.value === strategy)?.label || strategy;
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center space-x-2">
          <Clock className="w-4 h-4" />
          <span>Retry Policy Configuration</span>
        </CardTitle>
        <CardDescription>Current retry policy settings for handling node execution failures</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground">Max Retries</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {retryPolicy.max_retries}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Maximum number of retry attempts</p>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground">Retry Strategy</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {getStrategyLabel(retryPolicy.strategy)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Strategy for calculating retry delays</p>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground">Backoff Factor</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {retryPolicy.backoff_factor} ms
            </div>
            <p className="text-xs text-muted-foreground mt-1">Base delay in milliseconds</p>
          </div>

          <div>
            <label className="text-xs font-medium text-muted-foreground">Exponent</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {retryPolicy.exponent}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Multiplier for exponential strategies</p>
          </div>

          <div className="md:col-span-2">
            <label className="text-xs font-medium text-muted-foreground">Max Delay</label>
            <div className="text-sm font-mono bg-muted p-2 rounded mt-1">
              {retryPolicy.max_delay ? `${retryPolicy.max_delay} ms` : 'No maximum delay'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Maximum delay cap in milliseconds</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const StoreConfigViewer: React.FC<{ 
  storeConfig: any;
}> = ({ storeConfig }) => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center space-x-2">
            <Database className="w-4 h-4" />
            <span>Required Keys</span>
          </CardTitle>
          <CardDescription>Keys that must be present in the store when triggering the graph</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            {storeConfig.required_keys && storeConfig.required_keys.length > 0 ? (
              storeConfig.required_keys.map((key: string, index: number) => (
                <div key={index} className="text-sm font-mono bg-muted p-2 rounded">
                  {key}
                </div>
              ))
            ) : (
              <div className="text-center py-4 text-muted-foreground">
                <p>No required keys configured</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center space-x-2">
            <Settings className="w-4 h-4" />
            <span>Default Values</span>
          </CardTitle>
          <CardDescription>Default values for store keys when they are not provided</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            {storeConfig.default_values && Object.keys(storeConfig.default_values).length > 0 ? (
              Object.entries(storeConfig.default_values).map(([key, value]) => (
                <div key={key} className="grid grid-cols-2 gap-2">
                  <div className="text-sm font-mono bg-muted p-2 rounded">
                    {key}
                  </div>
                  <div className="text-sm font-mono bg-muted p-2 rounded">
                    {value as string}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-4 text-muted-foreground">
                <p>No default values configured</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
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
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <Card className="max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <CardHeader className="bg-primary/10 border-b">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">{graphTemplate.name}</CardTitle>
              <CardDescription className="mt-1">
                Graph Template Configuration
              </CardDescription>
            </div>
            <Button
              onClick={onClose}
              variant="ghost"
              size="sm"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>

        {/* Content */}
        <CardContent className="p-6">
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="visualization">Visualization</TabsTrigger>
              <TabsTrigger value="nodes">Nodes</TabsTrigger>
              <TabsTrigger value="retry-policy">Retry Policy</TabsTrigger>
              <TabsTrigger value="store-config">Store Config</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center space-x-2">
                      <Database className="w-4 h-4" />
                      <span>Template Information</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <label className="text-xs font-medium text-muted-foreground">Name</label>
                      <div className="text-sm font-mono bg-muted p-2 rounded mt-1">{graphTemplate.name}</div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-muted-foreground">Namespace</label>
                      <div className="text-sm font-mono bg-muted p-2 rounded mt-1">{graphTemplate.namespace}</div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-muted-foreground">Created</label>
                      <div className="text-sm bg-muted p-2 rounded mt-1">
                        {new Date(graphTemplate.created_at).toLocaleString()}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center space-x-2">
                      <Workflow className="w-4 h-4" />
                      <span>Statistics</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Total Nodes</span>
                      <Badge variant="secondary">{graphTemplate.nodes?.length || 0}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Secrets</span>
                      <Badge variant="secondary">
                        {graphTemplate.secrets ? Object.keys(graphTemplate.secrets).length : 0}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Status</span>
                      <Badge variant={graphTemplate.validation_status === 'VALID' ? 'default' : 'destructive'}>
                        {graphTemplate.validation_status}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {graphTemplate.validation_errors && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Validation Errors</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-sm bg-muted p-3 rounded border">
                      {graphTemplate.validation_errors}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="visualization" className="mt-6">
              <GraphVisualizer nodes={graphTemplate.nodes || []} />
            </TabsContent>

            <TabsContent value="nodes" className="space-y-4 mt-6">
              {graphTemplate.nodes && graphTemplate.nodes.length > 0 ? (
                <div className="space-y-4">
                  {graphTemplate.nodes.map((node, index) => (
                    <NodeDetailView key={index} node={node} index={index} />
                  ))}
                </div>
              ) : (
                <Card>
                  <CardContent className="text-center py-8">
                    <Database className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                    <h3 className="text-lg font-medium text-foreground mb-2">No Nodes</h3>
                    <p className="text-muted-foreground">This graph template doesn't have any nodes configured.</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="retry-policy" className="mt-6">
              <RetryPolicyViewer retryPolicy={graphTemplate.retry_policy} />
            </TabsContent>

            <TabsContent value="store-config" className="mt-6">
              <StoreConfigViewer storeConfig={graphTemplate.store_config} />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};
