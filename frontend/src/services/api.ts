import axios from 'axios';
import type { ChatRequest, ChatResponse, RetrievedLaw } from '@/types';

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const consultingApi = {
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const { data } = await api.post<ChatResponse>('/consulting/chat', request);
    return data;
  },

  async health(): Promise<any> {
    const { data } = await api.get('/consulting/health');
    return data;
  },

  async searchLaws(query: string, topK = 5): Promise<RetrievedLaw[]> {
    const { data } = await api.get<RetrievedLaw[]>('/laws/search', {
      params: { query, top_k: topK },
    });
    return data;
  },

  async getLawsStats(): Promise<any> {
    const { data } = await api.get('/laws/stats');
    return data;
  },
};

export default api;
