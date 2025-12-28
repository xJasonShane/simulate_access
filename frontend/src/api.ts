// src/api.ts
import axios from 'axios';
import type { SimulationConfig, SimulationStatus } from './types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const startSimulation = async (config: SimulationConfig): Promise<SimulationStatus> => {
  const response = await api.post('/api/tasks', config);
  return response.data;
};

export const getSimulationStatus = async (taskId: string): Promise<SimulationStatus> => {
  const response = await api.get(`/api/tasks/${taskId}`);
  return response.data;
};
