import React, { useState, useRef, useEffect } from 'react';
import { addTranscript } from '../api';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:9000';

export default function AudioCapture({ meetingId, onTranscript }) {
  const [recording, setRecording] = useState(false);
  const [status, setStatus] = useState('idle');
  const wsRef = useRef(null);
  const processorRef = useRef(null);
  const contextRef = useRef(null);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const ctx = new AudioContext({ sampleRate: 16000 });
    contextRef.current = ctx;

    const ws = new WebSocket(`${WS_URL}/ws/audio/${meetingId}`);
    wsRef.current = ws;

    ws.onmessage = async (e) => {
      const data = JSON.parse(e.data);
      onTranscript(data);
      // Also persist to DB
      await addTranscript({ meeting_id: meetingId, speaker: data.speaker, text: data.text });
    };

    ws.onopen = () => setStatus('connected');
    ws.onerror = () => setStatus('error');

    const source = ctx.createMediaStreamSource(stream);
    await ctx.audioWorklet.addModule('/audio-processor.js');
    const processor = new AudioWorkletNode(ctx, 'pcm-processor');
    processorRef.current = processor;

    processor.port.onmessage = (e) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(e.data.buffer);
      }
    };

    source.connect(processor);
    processor.connect(ctx.destination);
    setRecording(true);
    setStatus('recording');
  };

  const stopRecording = () => {
    if (wsRef.current) {
      wsRef.current.send('END');
      wsRef.current.close();
    }
    if (contextRef.current) contextRef.current.close();
    setRecording(false);
    setStatus('stopped');
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <button
        onClick={recording ? stopRecording : startRecording}
        style={{
          padding: '8px 20px',
          background: recording ? '#e53935' : '#1976d2',
          color: '#fff',
          border: 'none',
          borderRadius: 6,
          cursor: 'pointer',
          fontWeight: 600,
        }}
      >
        {recording ? '⏹ Stop Recording' : '🎙 Start Recording'}
      </button>
      <span style={{ fontSize: 13, color: '#666' }}>Status: {status}</span>
    </div>
  );
}
