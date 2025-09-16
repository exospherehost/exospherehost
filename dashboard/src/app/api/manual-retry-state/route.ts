import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.EXOSPHERE_STATE_MANAGER_URI || 'http://localhost:8000';
const API_KEY = process.env.EXOSPHERE_API_KEY;

export async function POST(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const namespace = searchParams.get('namespace');
    const stateId = searchParams.get('stateId');

    if (!namespace || !stateId) {
      return NextResponse.json({ error: 'Namespace and stateId are required' }, { status: 400 });
    }

    if (!API_KEY) {
      return NextResponse.json({ error: 'API key not configured' }, { status: 500 });
    }

    const body = await request.json();

    if (!body.fanout_id) {
      return NextResponse.json({ error: 'fanout_id is required in request body' }, { status: 400 });
    }

    const response = await fetch(`${API_BASE_URL}/v0/namespace/${namespace}/state/${stateId}/manual-retry`, {
      method: 'POST',
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`State manager API error: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error retrying state:', error);
    return NextResponse.json(
      { error: 'Failed to retry state' },
      { status: 500 }
    );
  }
} 