import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const backendPredictUrl = 'http://backend-java:8080/predict';
  const backendPredictionUrl = 'http://backend-java:8080/prediction';

  try {
    const body = await req.json();
    const predictPayload = {
      fl_date: body.flight_datetime,
      op_unique_carrier: body.op_unique_carrier,
      origin: body.origin,
      dest: body.dest
    };
    const predictRes = await fetch(backendPredictUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(predictPayload)
    });

    if (predictRes.ok) {
      const data = await predictRes.json();
      return NextResponse.json(data);
    }

    if (predictRes.status !== 404) {
      const text = await predictRes.text();
      return NextResponse.json(
        { error: `Backend error ${predictRes.status}`, details: text },
        { status: predictRes.status }
      );
    }

    const predictionRes = await fetch(backendPredictionUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!predictionRes.ok) {
      const text = await predictionRes.text();
      return NextResponse.json(
        { error: `Backend error ${predictionRes.status}`, details: text },
        { status: predictionRes.status }
      );
    }

    const data = await predictionRes.json();
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message || 'Unknown error when fetching backend' }, { status: 500 });
  }
}
