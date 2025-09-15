import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.EXOSPHERE_STATE_MANAGER_URI || 'http://localhost:8000';
const API_KEY = process.env.EXOSPHERE_API_KEY;

export async function GET(request: NextRequest) {
  try {
    if (!API_KEY) {
      return NextResponse.json({ error: 'API key not configured' }, { status: 500 });
    }

    const response = await fetch(`${API_BASE_URL}/v0/namespaces`, {
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
    console.error('Error fetching namespaces:', error);
    return NextResponse.json(
      { error: 'Failed to fetch namespaces' },
      { status: 500 }
    );
  }
} 