import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    defaultNamespace: process.env.NEXT_PUBLIC_DEFAULT_NAMESPACE || 'default',
    // Add other client-side config here if needed
  });
} 