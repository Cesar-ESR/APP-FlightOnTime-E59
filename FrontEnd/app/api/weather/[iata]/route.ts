import { NextResponse } from 'next/server';

export async function GET(_req: Request, { params }: { params: Promise<{ iata: string }> }) {
  const { iata } = await params;

  if (!iata || !/^[A-Z]{3}$/i.test(iata)) {
    return NextResponse.json({ error: 'Invalid IATA code (expected 3 letters).' }, { status: 400 });
  }

  const code = iata.toUpperCase();
  const backendUrl = `http://backend-java:8080/weather/${code}`;

  try {
    const res = await fetch(backendUrl);
    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json({ error: `Backend error ${res.status}`, details: text }, { status: res.status });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message || 'Unknown error when fetching backend' }, { status: 500 });
  }
}
