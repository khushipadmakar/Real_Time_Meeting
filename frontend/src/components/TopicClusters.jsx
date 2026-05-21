import React from 'react';

export default function TopicClusters({ topics }) {
  if (!topics?.length) return <p style={{ color: '#999' }}>No topics yet.</p>;

  const colors = ['#e3f2fd', '#e8f5e9', '#fff3e0', '#fce4ec', '#f3e5f5'];

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
      {topics.map((topic, i) => (
        <span key={i} style={{
          background: colors[i % colors.length],
          border: `1px solid #ccc`,
          borderRadius: 16,
          padding: '4px 14px',
          fontSize: 13,
          fontWeight: 500,
        }}>
          {typeof topic === 'string' ? topic : topic.label}
        </span>
      ))}
    </div>
  );
}
