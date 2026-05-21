import React, { useState } from 'react';
import { queryRAG } from '../api';

export default function RAGQuery({ meetingId }) {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await queryRAG(question, meetingId || undefined);
      setResult(res.data);
    } catch (e) {
      setResult({ answer: 'Error: ' + e.message, sources: [] });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleQuery()}
          placeholder="Ask about past meetings..."
          style={{ flex: 1, padding: '8px 12px', borderRadius: 6, border: '1px solid #ccc', fontSize: 14 }}
        />
        <button
          onClick={handleQuery}
          disabled={loading}
          style={{ padding: '8px 18px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}
        >
          {loading ? '...' : 'Ask'}
        </button>
      </div>
      {result && (
        <div style={{ marginTop: 12 }}>
          <p style={{ fontWeight: 600, marginBottom: 6 }}>Answer:</p>
          <p style={{ background: '#f5f5f5', padding: 12, borderRadius: 6, fontSize: 14 }}>{result.answer}</p>
          {result.sources?.length > 0 && (
            <details style={{ marginTop: 8 }}>
              <summary style={{ cursor: 'pointer', fontSize: 13, color: '#666' }}>
                {result.sources.length} source(s)
              </summary>
              {result.sources.map((s, i) => (
                <p key={i} style={{ fontSize: 12, color: '#888', margin: '4px 0', paddingLeft: 12 }}>
                  [{s.score?.toFixed(3)}] {s.text?.slice(0, 120)}...
                </p>
              ))}
            </details>
          )}
        </div>
      )}
    </div>
  );
}
