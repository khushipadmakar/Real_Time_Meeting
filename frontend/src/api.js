import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:9000';

const api = axios.create({ baseURL: BASE });

export const createMeeting = (title) => api.post('/meetings/', { title });
export const listMeetings = () => api.get('/meetings/');
export const endMeeting = (id) => api.post(`/meetings/${id}/end`);
export const addTranscript = (data) => api.post('/transcripts/', data);
export const getTranscripts = (id) => api.get(`/transcripts/${id}`);
export const processMeeting = (id) => api.post(`/analytics/${id}/process`);
export const getAnalytics = (id) => api.get(`/analytics/${id}`);
export const queryRAG = (question, meeting_id) => api.post('/rag/query', { question, meeting_id });
export const agentAnalyze = (id) => api.post(`/agent/${id}/analyze`);
export const generateEmail = (summary, action_items) => api.post('/rag/followup-email', { summary, action_items });
