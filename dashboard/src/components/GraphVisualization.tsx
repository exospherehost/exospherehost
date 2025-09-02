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
  EdgeTypes,
  ConnectionLineType,
  Handle
} from 'reactflow';
import 'reactflow/dist/style.css';
import { clientApiService } from '@/services/clientApi';
import { 
  GraphStructureResponse,
  GraphNode as GraphNodeType,
  GraphEdge as GraphEdgeType
} from '@/types/state-manager';
import {  
  RefreshCw, 
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Filter,
  Network,
  BarChart3
} from 'lucide-react';

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
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CREATED':
        return 'bg-[#031035]';
      case 'QUEUED':
        return 'bg-[#0a1a4a]';
      case 'EXECUTED':
      case 'SUCCESS':
        return 'bg-green-400';
      case 'ERRORED':
      case 'TIMEDOUT':
      case 'CANCELLED':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CREATED':
        return <Clock className="w-4 h-4 text-[#031035]" />;
      case 'QUEUED':
        return <Loader2 className="w-4 h-4 text-[#0a1a4a] animate-spin" />;
      case 'EXECUTED':
      case 'SUCCESS':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'ERRORED':
      case 'TIMEDOUT':
      case 'CANCELLED':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="px-4 py-2 shadow-lg rounded-lg bg-white border-2 border-[#031035]/20 min-w-[150px] relative">
      {/* Source Handle (Right side) */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#10b981', width: '12px', height: '12px' }}
      />
      
      {/* Target Handle (Left side) */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#10b981', width: '12px', height: '12px' }}
      />
      
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {getStatusIcon(data.status)}
          <span className={`text-xs px-2 py-1 rounded-full text-white ${getStatusColor(data.status)}`}>
            {data.status}
          </span>
        </div>
      </div>
      <div className="text-sm font-medium text-gray-800 mb-1">{data.label}</div>
      <div className="text-xs text-gray-500">{data.identifier}</div>
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
    const reactFlowEdges: Edge[] = graphData.edges.map(edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: 'default',
      animated: false,
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
        color: '#10b981',
      },
      style: {
        stroke: '#10b981',
        strokeWidth: 3,
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
    setSelectedNode(node.data.node);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-[#031035]" />
        <span className="ml-2 text-gray-600">Loading graph structure...</span>
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
              onClick={loadGraphStructure}
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

  if (!graphData) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Network className="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>No graph data available</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-6">
             <div className="flex items-center justify-between mb-6">
         <div className="flex items-center space-x-3">
           <Network className="w-6 h-6 text-green-400" />
           <div>
             <h2 className="text-2xl font-bold text-gray-800">Graph Visualization</h2>
             <p className="text-sm text-gray-600">
               Run ID: {runId} | Graph: {graphData.graph_name}
             </p>
           </div>
         </div>
         <button
           onClick={loadGraphStructure}
           className="flex items-center space-x-2 px-4 py-2 bg-green-400 text-white rounded-lg hover:bg-green-500 transition-colors"
         >
           <RefreshCw className="w-4 h-4" />
           <span>Refresh</span>
         </button>
       </div>

             {/* Execution Summary */}
       <div className="bg-white rounded-lg shadow-md border border-[#031035]/20 p-6 mb-6">
         <div className="flex items-center space-x-2 mb-4">
           <BarChart3 className="w-5 h-5 text-green-400" />
           <h3 className="text-lg font-semibold text-gray-800">Execution Summary</h3>
         </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {Object.entries(graphData.execution_summary).map(([status, count]) => (
            <div key={status} className="text-center">
              <div className="text-2xl font-bold text-gray-800">{count}</div>
              <div className="text-sm text-gray-600 capitalize">{status.toLowerCase()}</div>
            </div>
          ))}
        </div>
      </div>

             {/* Graph Visualization */}
       <div className="bg-white rounded-lg shadow-md border border-[#031035]/20 p-6">
         <div className="flex items-center justify-between mb-4">
           <h3 className="text-lg font-semibold text-gray-800">Graph Structure</h3>
           <div className="text-sm text-gray-500">
             {graphData.node_count} nodes, {graphData.edge_count} edges | 
             React Flow: {reactFlowNodes.length} nodes, {reactFlowEdges.length} edges
           </div>
         </div>

         <div className="border border-[#031035]/20 rounded-lg overflow-hidden" style={{ height: '800px' }}>
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
            <Background color="#eff6ff" gap={20} />
            <Controls />
          </ReactFlow>
        </div>
      </div>

      {/* Node Details Modal */}
      {selectedNode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Node Details</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                                 {(() => {
                   switch (selectedNode.status) {
                     case 'CREATED':
                       return <Clock className="w-4 h-4 text-[#031035]" />;
                     case 'QUEUED':
                       return <Loader2 className="w-4 h-4 text-[#0a1a4a] animate-spin" />;
                     case 'EXECUTED':
                     case 'SUCCESS':
                       return <CheckCircle className="w-4 h-4 text-green-400" />;
                     case 'ERRORED':
                     case 'TIMEDOUT':
                     case 'CANCELLED':
                       return <XCircle className="w-4 h-4 text-red-500" />;
                     default:
                       return <Clock className="w-4 h-4 text-gray-500" />;
                   }
                 })()}
                <div>
                  <h4 className="font-medium text-gray-800">{selectedNode.node_name}</h4>
                  <p className="text-sm text-gray-500">{selectedNode.identifier}</p>
                </div>
                                 <span className={`text-xs px-2 py-1 rounded ${
                   (() => {
                     switch (selectedNode.status) {
                       case 'CREATED': return 'bg-[#031035]';
                       case 'QUEUED': return 'bg-[#0a1a4a]';
                       case 'EXECUTED':
                       case 'SUCCESS': return 'bg-green-400';
                       case 'ERRORED':
                       case 'TIMEDOUT':
                       case 'CANCELLED': return 'bg-red-500';
                       default: return 'bg-gray-500';
                     }
                   })()
                 } text-white`}>
                  {selectedNode.status}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h5 className="font-medium text-gray-700 mb-2">Inputs</h5>
                  <pre className="text-xs text-black bg-gray-50 p-2 rounded overflow-x-auto">
                    {JSON.stringify(selectedNode.inputs, null, 2)}
                  </pre>
                </div>
                <div>
                  <h5 className="font-medium text-gray-700 mb-2">Outputs</h5>
                  <pre className="text-xs text-black bg-gray-50 p-2 rounded overflow-x-auto">
                    {JSON.stringify(selectedNode.outputs, null, 2)}
                  </pre>
                </div>
              </div>

              {selectedNode.error && (
                <div>
                  <h5 className="font-medium text-red-700 mb-2">Error</h5>
                  <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                    {selectedNode.error}
                  </div>
                </div>
              )}

              <div className="text-xs text-gray-500">
                Created: {new Date(selectedNode.created_at).toLocaleString()}
                {selectedNode.updated_at !== selectedNode.created_at && (
                  <span className="ml-4">
                    Updated: {new Date(selectedNode.updated_at).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
