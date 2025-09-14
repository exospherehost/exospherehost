'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Position,
  MarkerType,
  NodeTypes,
  ConnectionLineType,
  Handle
} from 'reactflow';
import 'reactflow/dist/style.css';
import { clientApiService } from '@/services/clientApi';
import { 
  GraphStructureResponse,
  GraphNode as GraphNodeType,
  NodeRunDetailsResponse
} from '@/types/state-manager';
import {  
  RefreshCw, 
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Network,
  BarChart3
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface GraphVisualizationProps {
  namespace: string;
  runId: string;
}

// Custom Node Component
const CustomNode: React.FC<{
  data: {
    label: string;
    status: string;
    identifier: string;
    node: GraphNodeType;
  };
}> = ({ data }) => {
  const getStatusVariant = (status: string): "default" | "success" | "destructive" | "secondary" => {
    switch (status) {
      case 'EXECUTED':
      case 'SUCCESS':
        return 'success';
      case 'ERRORED':
      case 'TIMEDOUT':
      case 'CANCELLED':
        return 'destructive';
      case 'QUEUED':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CREATED':
        return <Clock className="w-4 h-4" />;
      case 'QUEUED':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'EXECUTED':
      case 'SUCCESS':
        return <CheckCircle className="w-4 h-4" />;
      case 'ERRORED':
      case 'TIMEDOUT':
      case 'CANCELLED':
        return <XCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="px-4 py-3 shadow-sm rounded-xl  border border-border min-w-[160px] relative">
      {/* Source Handle (Right side) */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: 'hsl(var(--primary))', width: '12px', height: '12px' }}
      />
      
      {/* Target Handle (Left side) */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: 'hsl(var(--primary))', width: '12px', height: '12px' }}
      />
      
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getStatusIcon(data.status)}
          <Badge variant={getStatusVariant(data.status)}>
            {data.status}
          </Badge>
        </div>
      </div>
      <div className="text-sm font-medium text-card-foreground mb-1">{data.label}</div>
      <div className="text-xs text-muted-foreground">{data.identifier}</div>
    </div>
  );
};

const nodeTypes: NodeTypes = {
  custom: CustomNode,
};

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  namespace,
  runId
}) => {
  const [graphData, setGraphData] = useState<GraphStructureResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNodeType | null>(null);
  const [selectedNodeDetails, setSelectedNodeDetails] = useState<NodeRunDetailsResponse | null>(null);
  const [isLoadingNodeDetails, setIsLoadingNodeDetails] = useState(false);
  const [nodeDetailsError, setNodeDetailsError] = useState<string | null>(null);

  const loadGraphStructure = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await clientApiService.getGraphStructure(namespace, runId);
      setGraphData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load graph structure');
    } finally {
      setIsLoading(false);
    }
  };

  const loadNodeDetails = async (nodeId: string, graphName: string) => {
    setIsLoadingNodeDetails(true);
    setNodeDetailsError(null);
    
    try {
      const details = await clientApiService.getNodeRunDetails(namespace, graphName, runId, nodeId);
      setSelectedNodeDetails(details);
    } catch (err) {
      setNodeDetailsError(err instanceof Error ? err.message : 'Failed to load node details');
    } finally {
      setIsLoadingNodeDetails(false);
    }
  };

  useEffect(() => {
    if (namespace && runId) {
      loadGraphStructure();
    }
  }, [namespace, runId]);

  // Convert graph data to React Flow format with horizontal layout
  const { nodes, edges } = useMemo(() => {
    if (!graphData) return { nodes: [], edges: [] };

    // Build adjacency lists for layout calculation
    const nodeMap = new Map<string, GraphNodeType>();
    const childrenMap = new Map<string, string[]>();
    const parentMap = new Map<string, string[]>();

    // Initialize maps
    graphData.nodes.forEach(node => {
      nodeMap.set(node.id, node);
      childrenMap.set(node.id, []);
      parentMap.set(node.id, []);
    });

    // Build relationships
    graphData.edges.forEach(edge => {
      const children = childrenMap.get(edge.source) || [];
      children.push(edge.target);
      childrenMap.set(edge.source, children);

      const parents = parentMap.get(edge.target) || [];
      parents.push(edge.source);
      parentMap.set(edge.target, parents);
    });

    // Find root nodes (nodes with no parents)
    const rootNodes = graphData.nodes.filter(node => 
      (parentMap.get(node.id) || []).length === 0
    );

    // Build layers for horizontal layout
    const layers: GraphNodeType[][] = [];
    const visited = new Set<string>();

    // Start with root nodes
    if (rootNodes.length > 0) {
      layers.push(rootNodes);
      rootNodes.forEach(node => visited.add(node.id));
    }

    // Build layers
    let currentLayer = 0;
    while (visited.size < graphData.nodes.length && currentLayer < graphData.nodes.length) {
      const currentLayerNodes = layers[currentLayer] || [];
      const nextLayer: GraphNodeType[] = [];

      currentLayerNodes.forEach(node => {
        const children = childrenMap.get(node.id) || [];
        children.forEach(childId => {
          if (!visited.has(childId)) {
            const childNode = nodeMap.get(childId);
            if (childNode && !nextLayer.find(n => n.id === childId)) {
              nextLayer.push(childNode);
            }
          }
        });
      });

      if (nextLayer.length > 0) {
        layers.push(nextLayer);
        nextLayer.forEach(node => visited.add(node.id));
      }

      currentLayer++;
    }

    // Add any remaining nodes
    const remainingNodes = graphData.nodes.filter(node => !visited.has(node.id));
    if (remainingNodes.length > 0) {
      layers.push(remainingNodes);
    }

    // Convert to React Flow nodes with horizontal positioning
    const reactFlowNodes: Node[] = [];
    const layerWidth = 400; // Increased horizontal spacing between layers
    const nodeHeight = 150; // Increased vertical spacing between nodes

    layers.forEach((layer, layerIndex) => {
      const layerX = layerIndex * layerWidth + 150;
      const totalHeight = layer.length * nodeHeight;
      const startY = (800 - totalHeight) / 2; // Center vertically

      layer.forEach((node, nodeIndex) => {
        const y = startY + nodeIndex * nodeHeight + nodeHeight / 2;

        reactFlowNodes.push({
          id: node.id,
          type: 'custom',
          position: { x: layerX, y },
          data: {
            label: node.node_name,
            status: node.status,
            identifier: node.identifier,
            node: node
          },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
          connectable: true,
          draggable: false,
        });
      });
    });

    // Convert edges
    const reactFlowEdges: Edge[] = graphData.edges.map((edge, index) => ({
      id: `edge-${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      type: 'default',
      animated: false,
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 10,
        height: 10,
        color: '#87ceeb',
      },
      style: {
        stroke: '#87ceeb',
        strokeWidth: 2,
        strokeDasharray: 'none',
      },
    }));
    
    return { nodes: reactFlowNodes, edges: reactFlowEdges };
  }, [graphData]);

  const [reactFlowNodes, setReactFlowNodes, onNodesChange] = useNodesState(nodes);
  const [reactFlowEdges, setReactFlowEdges, onEdgesChange] = useEdgesState(edges);

  // Update React Flow nodes and edges when graph data changes
  useEffect(() => {
    setReactFlowNodes(nodes);
    setReactFlowEdges(edges);
  }, [nodes, edges, setReactFlowNodes, setReactFlowEdges]);

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    const graphNode = node.data.node;
    setSelectedNode(graphNode);
    setSelectedNodeDetails(null); // Clear previous details
    
    // Load detailed node information
    if (graphData?.graph_name) {
      loadNodeDetails(graphNode.id, graphData.graph_name);
    }
  }, [graphData?.graph_name]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-2 text-muted-foreground">Loading graph structure...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/20 bg-destructive/5">
        <CardContent className="pt-6">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-destructive" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-destructive">Error</h3>
              <div className="mt-2 text-sm text-destructive/80">{error}</div>
              <Button
                onClick={loadGraphStructure}
                variant="outline"
                size="sm"
                className="mt-3"
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Retry
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!graphData) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <Network className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
            <p className="text-muted-foreground">No graph data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Network className="w-8 h-8 text-primary" />
          <div>
            <h2 className="text-2xl font-bold text-foreground">Graph Visualization</h2>
            <p className="text-sm text-muted-foreground">
              Run ID: {runId} | Graph: {graphData.graph_name}
            </p>
          </div>
        </div>
        <Button onClick={loadGraphStructure} size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Execution Summary */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            <CardTitle>Execution Summary</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {Object.entries(graphData.execution_summary).map(([status, count]) => (
              <div key={status} className="text-center">
                <div className="text-2xl font-bold text-foreground">{count}</div>
                <div className="text-sm text-muted-foreground capitalize">{status.toLowerCase()}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Graph Visualization */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Graph Structure</CardTitle>
            <CardDescription>
              {graphData.node_count} nodes, {graphData.edge_count} edges 
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="border border-border rounded-xl overflow-hidden" style={{ height: '800px' }}>
            <ReactFlow
              nodes={reactFlowNodes}
              edges={reactFlowEdges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
              fitViewOptions={{ padding: 0.3 }}
              minZoom={0.1}
              maxZoom={2}
              defaultViewport={{ x: 0, y: 0, zoom: 0.7 }}
              proOptions={{ hideAttribution: true }}
              connectionLineType={ConnectionLineType.Straight}
              elementsSelectable={true}
              nodesConnectable={false}
              nodesDraggable={false}
            >
              <Controls />
            </ReactFlow>
          </div>
        </CardContent>
      </Card>

      {/* Node Details Modal */}
      {selectedNode && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
          <Card className="max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Node Details</CardTitle>
                <Button
                  onClick={() => {
                    setSelectedNode(null);
                    setSelectedNodeDetails(null);
                    setNodeDetailsError(null);
                  }}
                  variant="ghost"
                  size="icon"
                >
                  <XCircle className="w-5 h-5" />
                </Button>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Loading State */}
              {isLoadingNodeDetails && (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                  <span className="ml-2 text-muted-foreground">Loading node details...</span>
                </div>
              )}

              {/* Error State */}
              {nodeDetailsError && (
                <div className="flex items-center p-3 bg-destructive/5 border border-destructive/20 rounded-md">
                  <AlertCircle className="w-5 h-5 text-destructive" />
                  <div className="ml-3">
                    <p className="text-sm text-destructive">{nodeDetailsError}</p>
                  </div>
                </div>
              )}

              {/* Node Header - always show basic info */}
              <div className="flex items-center space-x-3">
                {(() => {
                  const status = selectedNodeDetails?.status || selectedNode.status;
                  switch (status) {
                    case 'CREATED':
                      return <Clock className="w-5 h-5 text-muted-foreground" />;
                    case 'QUEUED':
                      return <Loader2 className="w-5 h-5 text-secondary animate-spin" />;
                    case 'EXECUTED':
                    case 'SUCCESS':
                      return <CheckCircle className="w-5 h-5 text-chart-2" />;
                    case 'ERRORED':
                    case 'TIMEDOUT':
                    case 'CANCELLED':
                      return <XCircle className="w-5 h-5 text-destructive" />;
                    default:
                      return <Clock className="w-5 h-5 text-muted-foreground" />;
                  }
                })()}
                <div className="flex-1">
                  <h4 className="font-medium text-foreground">{selectedNodeDetails?.node_name || selectedNode.node_name}</h4>
                  <p className="text-sm text-muted-foreground">{selectedNodeDetails?.identifier || selectedNode.identifier}</p>
                </div>
                <Badge variant={(() => {
                  const status = selectedNodeDetails?.status || selectedNode.status;
                  switch (status) {
                    case 'EXECUTED':
                    case 'SUCCESS':
                      return 'success' as const;
                    case 'ERRORED':
                    case 'TIMEDOUT':
                    case 'CANCELLED':
                      return 'destructive' as const;
                    case 'QUEUED':
                      return 'secondary' as const;
                    default:
                      return 'default' as const;
                  }
                })()}>
                  {selectedNodeDetails?.status || selectedNode.status}
                </Badge>
              </div>

              {/* Only show detailed sections if not loading and no error */}
              {!isLoadingNodeDetails && !nodeDetailsError && (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h5 className="font-medium text-foreground mb-3">Node Information</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">ID:</span>
                          <span className="text-foreground font-mono">{selectedNodeDetails?.id || selectedNode.id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Name:</span>
                          <span className="text-foreground">{selectedNodeDetails?.node_name || selectedNode.node_name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Identifier:</span>
                          <span className="text-foreground font-mono">{selectedNodeDetails?.identifier || selectedNode.identifier}</span>
                        </div>
                        {selectedNodeDetails?.graph_name && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Graph:</span>
                            <span className="text-foreground">{selectedNodeDetails.graph_name}</span>
                          </div>
                        )}
                        {selectedNodeDetails?.run_id && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Run ID:</span>
                            <span className="text-foreground font-mono">{selectedNodeDetails.run_id}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div>
                      <h5 className="font-medium text-foreground mb-3">Status & Timestamps</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Current Status:</span>
                          <span className="text-foreground">{selectedNodeDetails?.status || selectedNode.status}</span>
                        </div>
                        {selectedNodeDetails?.created_at && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Created:</span>
                            <span className="text-foreground text-xs">{new Date(selectedNodeDetails.created_at).toLocaleString()}</span>
                          </div>
                        )}
                        {selectedNodeDetails?.updated_at && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Updated:</span>
                            <span className="text-foreground text-xs">{new Date(selectedNodeDetails.updated_at).toLocaleString()}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Error Section */}
                  {(selectedNodeDetails?.error || selectedNode.error) && (
                    <div>
                      <h5 className="font-medium text-destructive mb-3">Error</h5>
                      <div className="text-sm text-destructive bg-destructive/5 border border-destructive/20 p-3 rounded-md">
                        {selectedNodeDetails?.error || selectedNode.error}
                      </div>
                    </div>
                  )}

                  {/* Parent Nodes Section */}
                  {selectedNodeDetails?.parents && Object.keys(selectedNodeDetails.parents).length > 0 && (
                    <div>
                      <h5 className="font-medium text-foreground mb-3">Parent Nodes</h5>
                      <div className="bg-muted/20 border border-border rounded-md p-3">
                        <div className="space-y-1">
                          {Object.entries(selectedNodeDetails.parents).map(([identifier, parentId]) => (
                            <div key={identifier} className="flex justify-between text-sm">
                              <span className="text-muted-foreground">{identifier}:</span>
                              <span className="text-foreground font-mono">{parentId}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Inputs Section */}
                  <div>
                    <h5 className="font-medium text-foreground mb-3">Inputs</h5>
                    <div className="bg-muted/20 border border-border rounded-md p-3">
                      {(() => {
                        const inputs = selectedNodeDetails?.inputs || selectedNode.inputs || {};
                        return Object.keys(inputs).length > 0 ? (
                          <pre className="text-sm text-foreground whitespace-pre-wrap font-mono">
                            {JSON.stringify(inputs, null, 2)}
                          </pre>
                        ) : (
                          <p className="text-sm text-muted-foreground italic">No inputs</p>
                        );
                      })()}
                    </div>
                  </div>

                  {/* Outputs Section */}
                  <div>
                    <h5 className="font-medium text-foreground mb-3">Outputs</h5>
                    <div className="bg-muted/20 border border-border rounded-md p-3">
                      {(() => {
                        const outputs = selectedNodeDetails?.outputs || selectedNode.outputs || {};
                        return Object.keys(outputs).length > 0 ? (
                          <pre className="text-sm text-foreground whitespace-pre-wrap font-mono">
                            {JSON.stringify(outputs, null, 2)}
                          </pre>
                        ) : (
                          <p className="text-sm text-muted-foreground italic">No outputs</p>
                        );
                      })()}
                    </div>
                  </div>
                </>
              )}

              <div className="text-xs text-muted-foreground pt-4 border-t border-border">
                Node ID: {selectedNodeDetails?.id || selectedNode.id}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
