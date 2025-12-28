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
  success: boolean;
  status_code: number;
  message: string;
}

export interface SimulationStatus {
  task_id: string;
  status: 'running' | 'completed' | 'failed';
  success_count: number;
  fail_count: number;
  results: SimulationResult[];
}
