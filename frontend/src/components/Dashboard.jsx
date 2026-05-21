import React, { useState, useEffect } from 'react';
import {
  listMeetings, createMeeting, endMeeting,
  getTranscripts, processMeeting, getAnalytics, agentAnalyze
} from '../api';
import AudioCapture from './AudioCapture';
import SpeakerPanel from './SpeakerPanel';
import SentimentChart from './SentimentChart';
import ActionItems from './ActionItems';
import TopicClusters from './TopicClusters';
import RAGQuery from './RAGQuery';

const Card = ({ title, children }) => (
  <div style={{ background: '#fff', borderRadius: 10, padding: 20, boxShadow: '0 1px 4px rgba(0,0,0,0.1)', marginBottom: 20 }}>
    <h3 style={{ margin: '0 0 14px', fontSize: 16, color: '#333' }}>{title}</h3>
    {children}
  </div>
);

export default function Dashboard() {
  const [meetings, setMeetings] = useState([]);
  const [activeMeeting, setActiveMeeting] = useState(null);
  const [transcripts, setTranscripts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [agentReport, setAgentReport] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  const [processing, setProcessing] = useState(false);
  const [agentLoading, setAgentLoading] = useState(false);
  const [error, setError] = useState('');

  // Auto-refresh transcripts every 3 seconds when a meeting is active
  useEffect(() => {
    if (!activeMeeting) return;
    const interval = setInterval(async () => {
      try {
        const res = await getTranscripts(activeMeeting.id);
        setTranscripts(res.data);
      } catch {}
    }, 3000);
    return () => clearInterval(interval);
  }, [activeMeeting]);

  useEffect(() => { loadMeetings(); }, []);

  const loadMeetings = async () => {
    try {
      const res = await listMeetings();
      setMeetings(res.data);
    } catch (e) {
      setError('Cannot reach backend at http://localhost:9000');
    }
  };

  const handleCreate = async () => {
    const res = await createMeeting(newTitle || 'New Meeting');
    setActiveMeeting(res.data);
    setTranscripts([]);
    setAnalytics(null);
    setAgentReport(null);
    setNewTitle('');
    loadMeetings();
  };

  const handleSelect = async (m) => {
    setActiveMeeting(m);
    setAnalytics(null);
    setAgentReport(null);
    setError('');
    const res = await getTranscripts(m.id);
    setTranscripts(res.data);
    try {
      const a = await getAnalytics(m.id);
      if (a.data?.summary) setAnalytics(a.data);
    } catch { }
  };

  const handleTranscript = (data) => {
    setTranscripts(prev => [...prev, data]);
  };

  const handleProcess = async () => {
    if (!activeMeeting) return;
    setError('');
    setProcessing(true);
    try {
      const res = await processMeeting(activeMeeting.id);
      setAnalytics(res.data);
    } catch (e) {
      const msg = e.response?.data?.detail || e.message;
      setError('Process failed: ' + msg);
    } finally {
      setProcessing(false);
    }
  };

  const handleAgent = async () => {
    if (!activeMeeting) return;
    setError('');
    setAgentLoading(true);
    try {
      const res = await agentAnalyze(activeMeeting.id);
      setAgentReport(res.data);
    } catch (e) {
      const msg = e.response?.data?.detail || e.message;
      setError('Agent failed: ' + msg);
    } finally {
      setAgentLoading(false);
    }
  };

  const handleEnd = async () => {
    if (!activeMeeting) return;
    await endMeeting(activeMeeting.id);
    loadMeetings();
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f0f2f5', fontFamily: 'Inter, sans-serif' }}>
      {/* Sidebar */}
      <div style={{ width: 260, background: '#1a237e', color: '#fff', padding: 20, flexShrink: 0 }}>
        <h2 style={{ margin: '0 0 20px', fontSize: 18 }}>🎙 AI Meeting Platform</h2>
        <div style={{ marginBottom: 16 }}>
          <input
            value={newTitle}
            onChange={e => setNewTitle(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreate()}
            placeholder="Meeting title..."
            style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: 'none', fontSize: 13, boxSizing: 'border-box' }}
          />
          <button onClick={handleCreate} style={{ width: '100%', marginTop: 8, padding: '8px', background: '#42a5f5', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontWeight: 600 }}>
            + New Meeting
          </button>
        </div>
        <p style={{ fontSize: 12, opacity: 0.7, marginBottom: 8 }}>Recent Meetings</p>
        {meetings.map(m => (
          <div
            key={m.id}
            onClick={() => handleSelect(m)}
            style={{
              padding: '8px 10px', borderRadius: 6, cursor: 'pointer', marginBottom: 4,
              background: activeMeeting?.id === m.id ? 'rgba(255,255,255,0.2)' : 'transparent',
              fontSize: 13,
            }}
          >
            <div style={{ fontWeight: 600 }}>{m.title}</div>
            <div style={{ fontSize: 11, opacity: 0.7 }}>{m.status} · {new Date(m.started_at).toLocaleDateString()}</div>
          </div>
        ))}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, padding: 24, overflowY: 'auto' }}>
        {/* Global error banner */}
        {error && (
          <div style={{ background: '#ffebee', border: '1px solid #ef9a9a', borderRadius: 8, padding: '10px 16px', marginBottom: 16, color: '#c62828', fontSize: 13, display: 'flex', justifyContent: 'space-between' }}>
            ⚠️ {error}
            <span style={{ cursor: 'pointer', fontWeight: 700 }} onClick={() => setError('')}>✕</span>
          </div>
        )}

        {!activeMeeting ? (
          <div style={{ textAlign: 'center', marginTop: 80, color: '#999' }}>
            <h2>Select or create a meeting to get started</h2>
          </div>
        ) : (
          <>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 10 }}>
              <div>
                <h2 style={{ margin: 0 }}>{activeMeeting.title}</h2>
                <span style={{ fontSize: 12, color: '#888' }}>ID: {activeMeeting.id} · {activeMeeting.status}</span>
              </div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <button onClick={handleEnd} style={{ padding: '7px 14px', background: '#ef5350', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
                  ⏹ End
                </button>
                <button onClick={handleProcess} disabled={processing} style={{ padding: '7px 14px', background: processing ? '#aaa' : '#43a047', color: '#fff', border: 'none', borderRadius: 6, cursor: processing ? 'not-allowed' : 'pointer' }}>
                  {processing ? '⏳ Processing...' : '⚡ Process Meeting'}
                </button>
                <button onClick={handleAgent} disabled={agentLoading} style={{ padding: '7px 14px', background: agentLoading ? '#aaa' : '#7b1fa2', color: '#fff', border: 'none', borderRadius: 6, cursor: agentLoading ? 'not-allowed' : 'pointer' }}>
                  {agentLoading ? '⏳ Running...' : '🤖 Run Agent'}
                </button>
              </div>
            </div>

            {/* Audio capture */}
            <Card title="🎙 Live Audio Capture">
              <AudioCapture meetingId={activeMeeting.id} onTranscript={handleTranscript} />
            </Card>

            {/* Live transcript */}
            <Card title={`📝 Live Transcript (${transcripts.length} segments)`}>
              <div
                id="transcript-box"
                style={{ maxHeight: 250, overflowY: 'auto', fontSize: 13 }}
                ref={el => { if (el) el.scrollTop = el.scrollHeight; }}
              >
                {transcripts.length === 0
                  ? <p style={{ color: '#999' }}>No transcripts yet. Start recording or use capture_system_audio.py</p>
                  : transcripts.map((t, i) => (
                    <div key={i} style={{ marginBottom: 6, padding: '6px 10px', background: '#f9f9f9', borderRadius: 6 }}>
                      <strong style={{ color: '#1976d2' }}>{t.speaker}</strong>
                      <span style={{ fontSize: 11, color: '#999', marginLeft: 8 }}>
                        {t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : ''}
                      </span>
                      <p style={{ margin: '3px 0 0' }}>{t.text}</p>
                    </div>
                  ))
                }
              </div>
            </Card>

            {analytics ? (
              <>
                <Card title="📋 AI Summary">
                  <p style={{ fontSize: 14, lineHeight: 1.6, color: '#333' }}>{analytics.summary}</p>
                </Card>

                <Card title="🏷 Topic Clusters">
                  <TopicClusters topics={analytics.topics} />
                </Card>

                <Card title="👥 Speaker Activity">
                  <SpeakerPanel speakers={analytics.speakers} />
                </Card>

                <Card title="😊 Sentiment Trend">
                  <SentimentChart transcripts={transcripts} />
                </Card>

                <Card title="✅ Action Items">
                  <ActionItems items={analytics.action_items} />
                </Card>

                {analytics.engagement_score !== undefined && (
                  <Card title="📊 Engagement Score">
                    <div style={{ fontSize: 48, fontWeight: 700, color: analytics.engagement_score >= 60 ? '#43a047' : '#fb8c00' }}>
                      {analytics.engagement_score}
                      <span style={{ fontSize: 20, color: '#999' }}>/100</span>
                    </div>
                  </Card>
                )}
              </>
            ) : (
              <Card title="📋 Analytics">
                <p style={{ color: '#999', fontSize: 13 }}>
                  Add transcripts first, then click <strong>⚡ Process Meeting</strong> to generate summary, action items, and analytics.
                </p>
              </Card>
            )}

            {agentReport && (
              <Card title="🤖 AI Agent Report">
                <div style={{ fontSize: 13 }}>
                  <p><strong>Escalation needed:</strong> {agentReport.needs_escalation ? '⚠️ Yes' : '✅ No'}</p>
                  {agentReport.escalation_reason && <p><strong>Reason:</strong> {agentReport.escalation_reason}</p>}
                  {agentReport.unresolved_topics?.length > 0 && (
                    <div><strong>Unresolved topics:</strong>
                      <ul>{agentReport.unresolved_topics.map((t, i) => <li key={i}>{t}</li>)}</ul>
                    </div>
                  )}
                  {agentReport.reminders?.length > 0 && (
                    <div><strong>Reminders:</strong>
                      <ul>{agentReport.reminders.map((r, i) => <li key={i}><strong>{r.assignee}:</strong> {r.reminder}</li>)}</ul>
                    </div>
                  )}
                  {agentReport.prioritized_followups?.length > 0 && (
                    <div><strong>Follow-ups:</strong>
                      <ul>{agentReport.prioritized_followups.map((f, i) => (
                        <li key={i}><span style={{ color: f.priority === 'high' ? '#e53935' : f.priority === 'medium' ? '#fb8c00' : '#43a047', fontWeight: 700 }}>[{f.priority}]</span> {f.task} — {f.reason}</li>
                      ))}</ul>
                    </div>
                  )}
                </div>
              </Card>
            )}

            <Card title="🔍 Ask About Meetings (RAG)">
              <RAGQuery meetingId={activeMeeting.id} />
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
