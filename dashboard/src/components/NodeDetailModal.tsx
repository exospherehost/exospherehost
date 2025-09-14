'use client';

import React from 'react';
import { NodeRegistration } from '@/types/state-manager';
import { X, Code, Eye, EyeOff, Key, ChevronDown, ChevronRight } from 'lucide-react';

// Shadcn components
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface SchemaProperty {
  type: string;
  description?: string;
  enum?: string[];
}

interface Schema {
  type?: string;
  properties?: Record<string, SchemaProperty>;
  required?: string[];
}

interface NodeDetailModalProps {
  node: NodeRegistration | null;
  isOpen: boolean;
  onClose: () => void;
}

const SchemaRenderer: React.FC<{ schema: Schema; title: string }> = ({ schema, title }) => {
  const [isExpanded, setIsExpanded] = React.useState(true);

  const renderSchemaProperties = (properties: Record<string, SchemaProperty>, required: string[] = []) => {
    return Object.entries(properties).map(([key, value]: [string, SchemaProperty]) => (
      <div key={key} className="border-l-2 border-primary/30 pl-4 py-2 bg-card/50 rounded-r-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-sm font-medium text-foreground">
              {key}
            </span>
            {required.includes(key) && (
              <Badge variant="destructive" className="text-xs">
                required
              </Badge>
            )}
          </div>
          <Badge variant="outline" className="text-xs font-mono">
            {value.type}
          </Badge>
        </div>
        {value.description && (
          <p className="text-xs text-muted-foreground mt-1">{value.description}</p>
        )}
        {value.enum && (
          <div className="mt-1">
            <span className="text-xs text-muted-foreground">Options: </span>
            <div className="flex flex-wrap gap-1 mt-1">
              {value.enum.map((option, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs">
                  {option}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    ));
  };

  if (!schema || !schema.properties) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No schema defined</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <Button
          variant="ghost"
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-between w-full p-0 h-auto"
        >
          <CardTitle className="text-sm flex items-center space-x-2">
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            <span>{title}</span>
          </CardTitle>
          <Badge variant="outline">{Object.keys(schema.properties).length} fields</Badge>
        </Button>
      </CardHeader>
      {isExpanded && (
        <CardContent className="pt-0 space-y-3">
          {renderSchemaProperties(schema.properties, schema.required)}
        </CardContent>
      )}
    </Card>
  );
};

export const NodeDetailModal: React.FC<NodeDetailModalProps> = ({
  node,
  isOpen,
  onClose
}) => {
  const [showSecrets, setShowSecrets] = React.useState(false);

  if (!isOpen || !node) return null;

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <CardHeader className="bg-primary/10 border-b">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">{node.name}</CardTitle>
              <CardDescription className="mt-1">
                Node Schema Details
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
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="inputs">Inputs</TabsTrigger>
              <TabsTrigger value="outputs">Outputs</TabsTrigger>

            </TabsList>

            <TabsContent value="overview" className="space-y-4 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Node Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <label className="text-xs font-medium text-muted-foreground">Name</label>
                      <div className="text-sm font-mono bg-muted p-2 rounded mt-1">{node.name}</div>
                    </div>
                  </CardContent>
                </Card>

              </div>
            </TabsContent>

            <TabsContent value="inputs" className="mt-6">
              <SchemaRenderer schema={node.inputs_schema} title="Input Schema" />
            </TabsContent>

            <TabsContent value="outputs" className="mt-6">
              <SchemaRenderer schema={node.outputs_schema} title="Output Schema" />
            </TabsContent>

          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};
