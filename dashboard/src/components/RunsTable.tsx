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

interface RunsTableProps {
  namespace: string;
}

const REFRESH_OPTIONS = [
  { label: "Off", value: 0 },
  { label: "5 seconds", value: 5000 },
  { label: "10 seconds", value: 10000 },
  { label: "30 seconds", value: 30000 },
  { label: "1 minute", value: 60000 },
];

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
  const [refreshInterval, setRefreshInterval] = useState(0);

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
    if (refreshInterval === 0) return;

    const interval = setInterval(() => {
      loadRuns(currentPage, pageSize);
    }, refreshInterval);

    return () => clearInterval(interval);
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

  const handleVisualizeGraph = (runId: string) => {
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
        return 'bg-green-100 text-green-800 border-green-200';
      case RunStatusEnum.PENDING:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case RunStatusEnum.FAILED:
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getProgressPercentage = (run: RunListItem) => {
    if (run.total_count === 0) return 0;
    return Math.round((run.success_count / run.total_count) * 100);
  };

  if (isLoading && !runsData) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-[#031035]" />
        <span className="ml-2 text-gray-600">Loading runs...</span>
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
              onClick={() => loadRuns(currentPage, pageSize)}
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

  return (
    <div className="w-full max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-8 h-8 text-[#031035]" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Runs</h2>
            <p className="text-sm text-gray-600">Monitor and visualize workflow executions</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-700">Auto-refresh:</label>
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="border border-gray-300 rounded-md px-2 py-1 text-sm"
          >
            {REFRESH_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={() => loadRuns(currentPage, pageSize)}
          className="flex items-center space-x-2 px-4 py-2 bg-[#031035] text-white rounded-lg hover:bg-[#0a1a4a] transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Graph Visualization */}
      {showGraph && selectedRunId && (
        <div className="mb-6">
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">
                Graph Visualization for Run: {selectedRunId}
              </h3>
              <button
                onClick={() => setShowGraph(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            <GraphVisualization
              namespace={namespace}
              runId={selectedRunId}
            />
          </div>
        </div>
      )}

      {/* Runs Table */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-800">
              {runsData ? `${runsData.total} total runs` : 'Loading runs...'}
            </h3>
            <div className="flex items-center space-x-4">
              <label className="text-sm text-gray-600">Page size:</label>
              <select
                value={pageSize}
                onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                className="border border-gray-300 rounded-md px-2 py-1 text-sm"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Run ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Graph Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  States
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date & Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {runsData?.runs.map((run) => (
                <tr key={run.run_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <Hash className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-mono text-gray-900 font-medium">
                        {run.run_id.slice(0, 8)}...
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900 font-medium">
                      {run.graph_name}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(run.status)}
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(run.status)}`}>
                        {run.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${getProgressPercentage(run)}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600 w-12">
                        {getProgressPercentage(run)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
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
                        <span className="text-gray-400">/ {run.total_count}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        {new Date(run.created_at).toLocaleDateString()} {new Date(run.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleVisualizeGraph(run.run_id)}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-[#031035] hover:bg-[#0a1a4a] transition-colors"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      Visualize
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {runsData && runsData.total > pageSize && (
          <div className="bg-white px-6 py-3 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, runsData.total)} of {runsData.total} results
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="inline-flex items-center px-2 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </button>
                <span className="text-sm text-gray-700">
                  Page {currentPage} of {Math.ceil(runsData.total / pageSize)}
                </span>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage >= Math.ceil(runsData.total / pageSize)}
                  className="inline-flex items-center px-2 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Empty State */}
      {runsData && runsData.runs.length === 0 && (
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No runs found</h3>
          <p className="text-gray-500">There are no runs in this namespace yet.</p>
        </div>
      )}
    </div>
  );
}; 