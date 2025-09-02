import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.EXOSPHERE_STATE_MANAGER_URL || 'http://localhost:8000';
const API_KEY = process.env.EXOSPHERE_STATE_MANAGER_API_KEY;

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const namespace = searchParams.get('namespace');
    const runId = searchParams.get('runId');

    if (!namespace || !runId) {
      return NextResponse.json({ error: 'Namespace and runId are required' }, { status: 400 });
    }

    if (!API_KEY) {
      return NextResponse.json({ error: 'API key not configured' }, { status: 500 });
    }

    const response = await fetch(`${API_BASE_URL}/v0/namespace/${namespace}/states/run/${runId}/graph`, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`State manager API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching graph structure:', error);
    return NextResponse.json(
      { error: 'Failed to fetch graph structure' },
      { status: 500 }
    );
  }
} 