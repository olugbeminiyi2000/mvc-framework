import axios from 'axios';
import { WebApp, Route, HttpRequest, HttpResponse } from '../types';

// API base URL pointing to Flask backend
const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const mvcService = {
  // Web App Management
  async getWebApps(): Promise<WebApp[]> {
    const response = await api.get('/webapps');
    return response.data;
  },

  async createWebApp(name: string): Promise<WebApp> {
    const response = await api.post('/webapps', { name });
    return response.data;
  },

  // File Operations
  async getFileContent(webappName: string, path: string): Promise<string> {
    const response = await api.get('/files/content', {
      params: { webapp: webappName, path },
    });
    return response.data;
  },

  async saveFileContent(webappName: string, path: string, content: string): Promise<void> {
    await api.post('/files/content', {
      webapp: webappName,
      path,
      content,
    });
  },

  // Route Management
  async getRoutes(webappName: string): Promise<Route[]> {
    const response = await api.get('/routes', {
      params: { webapp: webappName },
    });
    return response.data;
  },

  async testRoute(webappName: string, request: HttpRequest): Promise<HttpResponse> {
    const response = await api.post('/routes/test', {
      webapp: webappName,
      request,
    });
    return response.data;
  },

  // Server Management
  async getServerStatus(webappName: string): Promise<{
    isRunning: boolean;
    port?: number;
    pid?: number;
    logs: string[];
  }> {
    const response = await api.get('/server/status', {
      params: { webapp: webappName },
    });
    return response.data;
  },

  async startServer(webappName: string): Promise<void> {
    await api.post('/server/start', {
      webapp: webappName,
    });
  },

  async stopServer(webappName: string): Promise<void> {
    await api.post('/server/stop', {
      webapp: webappName,
    });
  },

  async restartServer(webappName: string): Promise<void> {
    await api.post('/server/restart', {
      webapp: webappName,
    });
  },

  async registerRoutes(webappName: string): Promise<{
    success: boolean;
    message: string;
    registered_routes?: string[];
  }> {
    const response = await api.post('/routes/register', {
      webapp: webappName,
    });
    return response.data;
  },

  // WebSocket connection for real-time updates
  connectWebSocket(webappName: string, onUpdate: (data: any) => void) {
    const ws = new WebSocket(`ws://localhost:5000/ws?webapp=${webappName}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data);
    };

    return {
      disconnect: () => ws.close(),
    };
  },
}; 