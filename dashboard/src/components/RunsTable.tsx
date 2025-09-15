'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { clientApiService } from '@/services/clientApi';
import { RunsResponse, RunListItem, RunStatusEnum } from '@/types/state-manager';
import { GraphVisualization } from './GraphVisualization';
import { 
  ChevronLeft, 
  ChevronRight, 
  Eye, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader2,
  RefreshCw,
  AlertCircle,
  BarChart3,
  Calendar,
  Hash
} from 'lucide-react';

// Shadcn components
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select } from './ui/select';

interface RunsTableProps {
  namespace: string;
}

const REFRESH_OPTIONS = [
  { label: "Off", value: 0 },
  { label: "5 seconds", value: 5000 },
  { label: "10 seconds", value: 10000 },
  { label: "30 seconds", value: 30000 },
  { label: "1 minute", value: 60000 },
] as const;

type RefreshMs = typeof REFRESH_OPTIONS[number]['value'];

export const RunsTable: React.FC<RunsTableProps> = ({
  namespace
}) => {
  const [runsData, setRunsData] = useState<RunsResponse | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [showGraph, setShowGraph] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<RefreshMs>(0);

  const loadRuns = useCallback(async (page: number, size: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await clientApiService.getRuns(namespace, page, size);
      setRunsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load runs');
    } finally {
      setIsLoading(false);
    }
  }, [namespace]);

  useEffect(() => {
    if (namespace) {
      loadRuns(currentPage, pageSize);
    }
  }, [namespace, currentPage, pageSize, loadRuns]);

  useEffect(() => {
    if (refreshInterval === 0) {
      return;
    }

    let isCancelled = false;
    let timeoutId: ReturnType<typeof setTimeout>;

    const poll = () => {
      loadRuns(currentPage, pageSize).finally(() => {
        if (!isCancelled) {
          timeoutId = setTimeout(poll, refreshInterval);
        }
      });
    };

    timeoutId = setTimeout(poll, refreshInterval);

    return () => {
      isCancelled = true;
      clearTimeout(timeoutId);
    };
  }, [refreshInterval, currentPage, pageSize, loadRuns]);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    setSelectedRunId(null);
    setShowGraph(false);
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setCurrentPage(1);
    setSelectedRunId(null);
    setShowGraph(false);
  };

  const handleRowClick = (runId: string) => {
    setSelectedRunId(runId);
    setShowGraph(true);
  };

  const getStatusIcon = (status: RunStatusEnum) => {
    switch (status) {
      case RunStatusEnum.SUCCESS:
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case RunStatusEnum.PENDING:
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case RunStatusEnum.FAILED:
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: RunStatusEnum) => {
    switch (status) {
      case RunStatusEnum.SUCCESS:
        return 'success';
      case RunStatusEnum.PENDING:
        return 'secondary';
      case RunStatusEnum.FAILED:
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getProgressPercentage = (run: RunListItem) => {
    if (run.total_count === 0) return 0;
    return Math.round((run.success_count / run.total_count) * 100);
  };

  if (isLoading && !runsData) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-2 text-muted-foreground">Loading runs...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Error loading runs: {error}
          <Button
            onClick={() => loadRuns(currentPage, pageSize)}
            variant="outline"
            size="sm"
            className="ml-2"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-8 h-8 text-primary" />
          <div>
            <h2 className="text-2xl font-bold text-foreground">Workflow Runs</h2>
            <p className="text-sm text-muted-foreground">Monitor and visualize workflow executions</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <label 
              htmlFor="auto-refresh-select" 
              className="text-sm font-medium text-muted-foreground"
            >
              Auto-refresh:
            </label>
            <Select
              id="auto-refresh-select"
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value) as RefreshMs)}
              className="px-3 py-2 text-sm border border-input rounded-md bg-background shadow-sm 
                 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary 
                 hover:border-muted-foreground transition-colors"
            >
              {REFRESH_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          </div>

          <Button
            onClick={() => loadRuns(currentPage, pageSize)}
            variant="outline"
            size="sm"
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
        </div>
      </div>


      {/* Graph Visualization */}
      {showGraph && selectedRunId && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle>Graph Visualization for Run: {selectedRunId}</CardTitle>
            <Button
              onClick={() => setShowGraph(false)}
              variant="ghost"
              size="sm"
            >
              <XCircle className="w-5 h-5" />
            </Button>
          </CardHeader>
          <CardContent>
            <GraphVisualization
              namespace={namespace}
              runId={selectedRunId}
            />
          </CardContent>
        </Card>
      )}

      {/* Runs Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle>
            {runsData ? `${runsData.total} total runs` : 'Loading runs...'}
          </CardTitle>
          <div className="flex items-center space-x-4">
            <label className="text-sm text-muted-foreground">Page size:</label>
            <select
              value={pageSize}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
              className="border border-input rounded-md px-2 py-1 text-sm bg-background"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </CardHeader>
        <CardContent className="p-0">

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Run ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Graph Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    States
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Date & Time
                  </th>
                </tr>
              </thead>
              <tbody className="bg-card divide-y divide-border">
              {runsData?.runs.map((run) => (
                <tr 
                  key={run.run_id} 
                  className="hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => handleRowClick(run.run_id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <Hash className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm font-mono text-foreground font-medium">
                        {run.run_id.slice(0, 8)}...
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-foreground font-medium">
                      {run.graph_name}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(run.status)}
                      <Badge variant={getStatusColor(run.status)}>
                        {run.status}
                      </Badge>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-muted rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${getProgressPercentage(run)}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-muted-foreground w-12">
                        {getProgressPercentage(run)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-foreground">
                      <div className="flex items-center space-x-4">
                        <span className="flex items-center space-x-1">
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          <span>{run.success_count}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3 h-3 text-yellow-500" />
                          <span>{run.pending_count}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <XCircle className="w-3 h-3 text-red-500" />
                          <span>{run.errored_count}</span>
                        </span>
                        <span className="text-muted-foreground">/ {run.total_count}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {new Date(run.created_at).toLocaleDateString()} {new Date(run.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

          {/* Pagination */}
          {runsData && runsData.total > pageSize && (
            <div className="bg-card px-6 py-3 border-t border-border">
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, runsData.total)} of {runsData.total} results
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    variant="outline"
                    size="sm"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    Previous
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    Page {currentPage} of {Math.ceil(runsData.total / pageSize)}
                  </span>
                  <Button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage >= Math.ceil(runsData.total / pageSize)}
                    variant="outline"
                    size="sm"
                  >
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Empty State */}
      {runsData && runsData.runs.length === 0 && (
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-lg font-medium text-foreground mb-2">No runs found</h3>
          <p className="text-muted-foreground">There are no runs in this namespace yet.</p>
        </div>
      )}
    </div>
  );
}; 