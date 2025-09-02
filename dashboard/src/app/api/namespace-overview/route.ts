import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.EXOSPHERE_STATE_MANAGER_URI || 'http://localhost:8000';
const API_KEY = process.env.EXOSPHERE_API_KEY;

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const namespace = searchParams.get('namespace');

    if (!namespace) {
      return NextResponse.json({ error: 'Namespace is required' }, { status: 400 });
    }

    if (!API_KEY) {
      return NextResponse.json({ error: 'API key not configured' }, { status: 500 });
    }

    // Fetch registered nodes
    const nodesResponse = await fetch(`${API_BASE_URL}/v0/namespace/${namespace}/nodes/`, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
    });

    // Fetch graph templates
    const graphsResponse = await fetch(`${API_BASE_URL}/v0/namespace/${namespace}/graphs/`, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
    });

    // Fetch current states
    const statesResponse = await fetch(`${API_BASE_URL}/v0/namespace/${namespace}/states/`, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
    });

    const [nodesData, graphsData, statesData] = await Promise.all([
      nodesResponse.ok ? nodesResponse.json() : { namespace, count: 0, nodes: [] },
      graphsResponse.ok ? graphsResponse.json() : { namespace, count: 0, templates: [] },
      statesResponse.ok ? statesResponse.json() : { namespace, count: 0, states: [], run_ids: [] }
    ]);

    return NextResponse.json({
      namespace,
      nodes: nodesData,
      graphs: graphsData,
      states: statesData
    });
  } catch (error) {
    console.error('Error fetching namespace overview:', error);
    return NextResponse.json(
      { error: 'Failed to fetch namespace overview' },
      { status: 500 }
    );
  }
} 