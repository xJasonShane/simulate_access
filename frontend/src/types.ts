// src/types.ts

export interface SimulationConfig {
  url: string;
  min_interval: number;
  max_interval: number;
  count: number;
  timeout: number;
  retries: number;
  retry_delay: number;
}

export interface SimulationResult {
  id: number;
  status: string;
  status_code: number;
  message: string;
  created_at: string;
}

export interface SimulationStatus {
  id: string;
  url: string;
  min_interval: number;
  max_interval: number;
  count: number;
  timeout: number;
  retries: number;
  retry_delay: number;
  status: 'running' | 'completed' | 'failed';
  success_count: number;
  fail_count: number;
  created_at: string;
  updated_at: string;
  results: SimulationResult[];
}

export interface TaskListItem {
  id: string;
  url: string;
  status: string;
  success_count: number;
  fail_count: number;
  created_at: string;
}
