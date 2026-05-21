import React from 'react';

export default function ActionItems({ items }) {
  if (!items?.length) return <p style={{ color: '#999' }}>No action items yet.</p>;

  const priorityColor = { high: '#e53935', medium: '#fb8c00', low: '#43a047' };

  return (
    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
      {items.map((item, i) => (
        <li key={i} style={{
          display: 'flex', alignItems: 'flex-start', gap: 10,
          padding: '8px 0', borderBottom: '1px solid #f0f0f0'
        }}>
          <span style={{
            background: priorityColor[item.priority] || '#999',
            color: '#fff', borderRadius: 4, padding: '2px 7px', fontSize: 11, fontWeight: 700,
            minWidth: 48, textAlign: 'center', marginTop: 2,
          }}>
            {item.priority?.toUpperCase()}
          </span>
          <div>
            <strong style={{ fontSize: 13 }}>{item.assignee}</strong>
            <p style={{ margin: '2px 0 0', fontSize: 13, color: '#444' }}>{item.task}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}
