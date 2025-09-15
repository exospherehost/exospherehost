'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { clientApiService } from '@/services/clientApi';
import { 
  ListRegisteredNodesResponse, 
  ListGraphTemplatesResponse,
  NodeRegistration,
} from '@/types/state-manager';
import { 
  Database, 
  GitBranch, 
  RefreshCw, 
  AlertCircle,
  CheckCircle,
  Clock,
  Loader2
} from 'lucide-react';

// Shadcn components
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';

interface NamespaceOverviewProps {
  namespace: string;
  onOpenNode?: (node: NodeRegistration) => void;
  onOpenGraphTemplate?: (graphName: string) => void;
}

export const NamespaceOverview: React.FC<NamespaceOverviewProps> = ({
  namespace,
  onOpenNode,
  onOpenGraphTemplate
}) => {
  const [nodesResponse, setNodesResponse] = useState<ListRegisteredNodesResponse | null>(null);
  const [templatesResponse, setTemplatesResponse] = useState<ListGraphTemplatesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadNamespaceData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await clientApiService.getNamespaceOverview(namespace);
      
      setNodesResponse(data.nodes);
      setTemplatesResponse(data.graphs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load namespace data');
    } finally {
      setIsLoading(false);
    }
  }, [namespace]);

  useEffect(() => {
    if (namespace) {
      loadNamespaceData();
    }
  }, [namespace, loadNamespaceData]);

  const getValidationStatusColor = (status: string) => {
    switch (status) {
      case 'VALID':
        return 'success';
      case 'INVALID':
        return 'destructive';
      case 'PENDING':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getValidationIcon = (status: string) => {
    switch (status) {
      case 'VALID':
        return <CheckCircle className="w-4 h-4" />;
      case 'INVALID':
        return <AlertCircle className="w-4 h-4" />;
      case 'PENDING':
        return <Clock className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-2 text-muted-foreground">Loading namespace data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Error loading namespace data: {error}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Namespace Overview</h2>
          <p className="text-muted-foreground">Monitor your registered nodes and graph templates</p>
        </div>
        <Button
          onClick={loadNamespaceData}
          variant="outline"
          className="flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Registered Nodes */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Database className="w-6 h-6 text-primary" />
                <CardTitle>Registered Nodes</CardTitle>
              </div>
              <span className="text-sm text-muted-foreground">
                {nodesResponse?.count || 0} nodes
              </span>
            </div>
            <CardDescription>
              Active workflow nodes in the {namespace} namespace
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            {nodesResponse?.nodes && nodesResponse.nodes.length > 0 ? (
              <div className="space-y-3">
                {nodesResponse.nodes.map((node, index) => (
                  <div 
                    key={index} 
                    className="p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() => onOpenNode?.(node)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-foreground">{node.name}</h4>
                    </div>
                    
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Database className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No registered nodes found</p>
                <p className="text-sm mt-1">Nodes will appear here once registered</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Graph Templates */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <GitBranch className="w-6 h-6 text-primary" />
                <CardTitle>Graph Templates</CardTitle>
              </div>
              <span className="text-sm text-muted-foreground">
                {templatesResponse?.count || 0} templates
              </span>
            </div>
            <CardDescription>
              Workflow graph templates in the {namespace} namespace
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            {templatesResponse?.templates && templatesResponse.templates.length > 0 ? (
              <div className="space-y-3">
                {templatesResponse.templates.map((template, index) => (
                  <div 
                    key={index} 
                    className="p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() => onOpenGraphTemplate?.(template.name)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-foreground">{template.name}</h4>
                      <Badge variant={getValidationStatusColor(template.validation_status)}>
                        {getValidationIcon(template.validation_status)}
                        {template.validation_status}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground space-y-1">
                      <div>Namespace: <span className="font-mono">{template.namespace}</span></div>
                      <div>Nodes: <span className="font-mono">{template.nodes?.length || 0}</span></div>
                      {template.validation_errors && (
                        <div className="text-xs mt-2 p-2 bg-muted rounded border">
                          {template.validation_errors}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <GitBranch className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No graph templates found</p>
                <p className="text-sm mt-1">Templates will appear here once created</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
