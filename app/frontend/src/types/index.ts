// API Request/Response Types

import React from 'react';

export interface ChatRequest {
  query: string;
  session_id?: string;
}

export interface ChatResponse {
  answer: string;
  source_url?: string;
  last_updated: string;
  is_refusal: boolean;
  query_type: 'factual' | 'advisory' | 'ambiguous';
  response_time_ms?: number;
  chunks_retrieved?: number;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  request_id?: string;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  vector_store_docs?: number;
  last_ingestion?: string;
  server_start_time: string;
  uptime_seconds: number;
}

export interface SchemeInfo {
  name: string;
  category: string;
  url: string;
}

export interface SchemesResponse {
  schemes: SchemeInfo[];
}

// UI Component Types

export interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  source_url?: string;
  last_updated?: string;
  is_refusal?: boolean;
  query_type?: 'factual' | 'advisory' | 'ambiguous';
  timestamp: Date;
  isLoading?: boolean;
}

export interface ExampleQuestion {
  text: string;
  query: string;
  icon?: React.ReactNode;
}
