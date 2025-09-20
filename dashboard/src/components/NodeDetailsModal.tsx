'use client';

import React, { useState, useEffect } from 'react';
import { 
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { GraphNode as GraphNodeType, NodeRunDetailsResponse } from '@/types/state-manager';
import { clientApiService } from '@/services/clientApi';

interface NodeDetailsModalProps {
  selectedNode: GraphNodeType | null;
  selectedNodeDetails: NodeRunDetailsResponse | null;
  isLoadingNodeDetails: boolean;
  nodeDetailsError: string | null;
  namespace: string;
  onClose: () => void;
  onRefreshGraph: () => void;
}

export const NodeDetailsModal: React.FC<NodeDetailsModalProps> = ({
  selectedNode,
  selectedNodeDetails,
  isLoadingNodeDetails,
  nodeDetailsError,
  namespace,
  onClose,
  onRefreshGraph
}) => {
  const [retryState, setRetryState] = useState<'idle' | 'confirm' | 'loading' | 'success' | 'error'>('idle');
  const [retryError, setRetryError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState<number | null>(null);

  // Reset retry state when modal closes or node changes
  useEffect(() => {
    setRetryState('idle');
    setRetryError(null);
    setCountdown(null);
  }, [selectedNode]);

  // Countdown timer for reverting from confirm state
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (retryState === 'confirm' && countdown !== null && countdown > 0) {
      timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
    } else if (retryState === 'confirm' && countdown === 0) {
      setRetryState('idle');
      setCountdown(null);
    }
    return () => clearTimeout(timer);
  }, [retryState, countdown]);

  const handleRetryClick = async () => {
    if (!selectedNode) return;

    if (retryState === 'idle') {
      // First click - show confirmation
      setRetryState('confirm');
      setCountdown(10);
    } else if (retryState === 'confirm') {
      // Second click - execute retry
      setRetryState('loading');
      setRetryError(null);
      setCountdown(null);

      try {
        // Generate UUID for fanout_id
        const fanoutId = crypto.randomUUID ? crypto.randomUUID() : 
          'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
          });
        
        await clientApiService.manualRetryState(namespace, selectedNode.id, fanoutId);
        
        setRetryState('success');
        
        // Refresh the graph visualization to show updated state
        onRefreshGraph();
        
        // Reset to idle after 3 seconds
        setTimeout(() => {
          setRetryState('idle');
        }, 3000);
      } catch (error) {
        setRetryError(error instanceof Error ? error.message : 'Failed to retry state');
        setRetryState('error');
        
        // Reset to idle after 5 seconds
        setTimeout(() => {
          setRetryState('idle');
          setRetryError(null);
        }, 5000);
      }
    }
  };

  const getRetryButtonContent = () => {
    switch (retryState) {
      case 'confirm':
        return (
          <>
            <RefreshCw className="w-4 h-4 mr-2" />
            Confirm Retry? ({countdown}s)
          </>
        );
      case 'loading':
        return (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Retrying...
          </>
        );
      case 'success':
        return (
          <>
            <CheckCircle className="w-4 h-4 mr-2" />
            Retry Initiated
          </>
        );
      case 'error':
        return (
          <>
            <XCircle className="w-4 h-4 mr-2" />
            Retry Failed
          </>
        );
      default:
        return (
          <>
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </>
        );
    }
  };

  const getRetryButtonVariant = () => {
    switch (retryState) {
      case 'confirm':
        return 'pending' as const;
      case 'success':
        return 'default' as const;
      case 'error':
        return 'destructive' as const;
      default:
        return 'outline' as const;
    }
  };

  if (!selectedNode) return null;

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <Card className="max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Node Details</CardTitle>
            <Button
              onClick={onClose}
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

          {/* Retry Button Section */}
          <div className="flex items-center justify-between p-4 bg-muted/20 border border-border rounded-md">
            <div>
              <h5 className="font-medium text-foreground mb-1">Node Actions</h5>
              <p className="text-sm text-muted-foreground">Retry this node&apos;s execution</p>
              {retryError && (
                <p className="text-sm text-destructive mt-1">{retryError}</p>
              )}
            </div>
            <Button
              onClick={handleRetryClick}
              variant={getRetryButtonVariant()}
              disabled={retryState === 'loading' || retryState === 'success'}
              className="min-w-[140px]"
            >
              {getRetryButtonContent()}
            </Button>
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
  );
}; 