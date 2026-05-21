import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function SentimentChart({ transcripts }) {
  if (!transcripts?.length) return <p style={{ color: '#999' }}>No transcript data yet.</p>;

  const data = transcripts.map((t, i) => ({
    idx: i + 1,
    sentiment: t.sentiment_score ?? 0,
    speaker: t.speaker,
  }));

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <XAxis dataKey="idx" label={{ value: 'Turn', position: 'insideBottom', offset: -2 }} tick={{ fontSize: 11 }} />
        <YAxis domain={[-1, 1]} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(v, n, p) => [`${v.toFixed(3)}`, `${p.payload.speaker}`]} />
        <ReferenceLine y={0} stroke="#ccc" strokeDasharray="4 4" />
        <Line type="monotone" dataKey="sentiment" stroke="#1976d2" dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
