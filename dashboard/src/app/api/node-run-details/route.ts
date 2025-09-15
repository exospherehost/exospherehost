import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.EXOSPHERE_STATE_MANAGER_URI || 'http://localhost:8000';
const API_KEY = process.env.EXOSPHERE_API_KEY;

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const namespace = searchParams.get('namespace');
    const graphName = searchParams.get('graphName');
    const runId = searchParams.get('runId');
    const nodeId = searchParams.get('nodeId');

    if (!namespace || !graphName || !runId || !nodeId) {
      return NextResponse.json({ error: 'Namespace, graphName, runId, and nodeId are required' }, { status: 400 });
    }

    if (!API_KEY) {
      return NextResponse.json({ error: 'API key not configured' }, { status: 500 });
    }

    const response = await fetch(`${API_BASE_URL}/v0/namespace/${encodeURIComponent(namespace)}/graph/${encodeURIComponent(graphName)}/run/${encodeURIComponent(runId)}/node/${encodeURIComponent(nodeId)}`, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Propagate upstream error with original status and body
      let upstreamBody: string;
      const contentType = response.headers.get('Content-Type');
      
      try {
        if (contentType?.includes('application/json')) {
          const jsonData = await response.json();
          upstreamBody = JSON.stringify(jsonData);
        } else {
          upstreamBody = await response.text();
        }
      } catch {
        upstreamBody = `Upstream error: ${response.status} ${response.statusText}`;
      }

      return new Response(upstreamBody, {
        status: response.status,
        headers: {
          'Content-Type': contentType || 'text/plain',
        },
      });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching node run details:', error);
    return NextResponse.json(
      { error: 'Failed to fetch node run details' },
      { status: 500 }
    );
  }
} 