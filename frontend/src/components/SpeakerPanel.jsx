import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#1976d2', '#43a047', '#fb8c00', '#e53935', '#8e24aa'];

export default function SpeakerPanel({ speakers }) {
  if (!speakers?.length) return <p style={{ color: '#999' }}>No speaker data yet.</p>;

  return (
    <div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={speakers} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis unit="s" tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v) => `${v}s`} />
          <Bar dataKey="speaking_time_seconds" name="Speaking Time">
            {speakers.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <table style={{ width: '100%', fontSize: 13, borderCollapse: 'collapse', marginTop: 8 }}>
        <thead>
          <tr style={{ background: '#f5f5f5' }}>
            {['Speaker', 'Turns', 'Avg Sentiment'].map(h => (
              <th key={h} style={{ padding: '4px 8px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {speakers.map((s, i) => (
            <tr key={i}>
              <td style={{ padding: '4px 8px' }}>{s.name}</td>
              <td style={{ padding: '4px 8px' }}>{s.turn_count}</td>
              <td style={{ padding: '4px 8px', color: s.avg_sentiment >= 0 ? '#43a047' : '#e53935' }}>
                {s.avg_sentiment?.toFixed(3)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
