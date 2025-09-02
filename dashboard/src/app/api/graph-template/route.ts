import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.EXOSPHERE_STATE_MANAGER_URL || 'http://localhost:8000';
const API_KEY = process.env.EXOSPHERE_STATE_MANAGER_API_KEY;

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const namespace = searchParams.get('namespace');
    const graphName = searchParams.get('graphName');

    if (!namespace || !graphName) {
      return NextResponse.json({ error: 'Namespace and graphName are required' }, { status: 400 });
    }

    if (!API_KEY) {
      return NextResponse.json({ error: 'API key not configured' }, { status: 500 });
    }

    const response = await fetch(`${API_BASE_URL}/v0/namespace/${namespace}/graph/${graphName}`, {
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
    console.error('Error fetching graph template:', error);
    return NextResponse.json(
      { error: 'Failed to fetch graph template' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const namespace = searchParams.get('namespace');
    const graphName = searchParams.get('graphName');

    if (!namespace || !graphName) {
      return NextResponse.json({ error: 'Namespace and graphName are required' }, { status: 400 });
    }

    if (!API_KEY) {
      return NextResponse.json({ error: 'API key not configured' }, { status: 500 });
    }

    const body = await request.json();

    const response = await fetch(`${API_BASE_URL}/v0/namespace/${namespace}/graph/${graphName}`, {
      method: 'PUT',
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`State manager API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error updating graph template:', error);
    return NextResponse.json(
      { error: 'Failed to update graph template' },
      { status: 500 }
    );
  }
} 