export interface WebApp {
  name: string;
  path: string;
  models: FileInfo[];
  views: FileInfo[];
  controllers: FileInfo[];
  router?: FileInfo;
  init?: FileInfo;
}

export interface FileInfo {
  name: string;
  path: string;
  content: string;
  type: 'model' | 'view' | 'controller' | 'router';
}

export interface Route {
  path: string;
  method: string;
  controller: string;
  action: string;
  view: string;
}

export interface ServerStatus {
  isRunning: boolean;
  port?: number | null;
  pid?: number | null;
  logs: string[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface HttpRequest {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  headers: Record<string, string>;
  body?: any;
}

export interface HttpResponse {
  status: number;
  headers: Record<string, string>;
  body: any;
  viewOutput?: string;
  contentType?: string;
} 