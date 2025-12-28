import { useState, useEffect } from 'react';
import './App.css';
import type { SimulationConfig, SimulationStatus } from './types';
import { startSimulation, getSimulationStatus } from './api';
import ConfigForm from './components/ConfigForm';
import TaskMonitor from './components/TaskMonitor';

function App() {
  // 模拟状态
  const [currentTask, setCurrentTask] = useState<SimulationStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);

  // 开始模拟访问
  const handleStartSimulation = async (config: SimulationConfig) => {
    try {
      setIsLoading(true);
      const task = await startSimulation(config);
      setCurrentTask(task);
      setIsPolling(true);
    } catch (error: any) {
      alert(`开始模拟失败: ${error.response?.data?.detail || '未知错误'}`);
      console.error('开始模拟失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 轮询获取任务状态
  useEffect(() => {
    let intervalId: number;

    if (isPolling && currentTask?.id) {
      intervalId = window.setInterval(async () => {
        try {
          const updatedTask = await getSimulationStatus(currentTask.id);
          setCurrentTask(updatedTask);
          
          // 如果任务已完成或失败，停止轮询
          if (updatedTask.status !== 'running') {
            setIsPolling(false);
          }
        } catch (error) {
          console.error('获取任务状态失败:', error);
          setIsPolling(false);
        }
      }, 2000);
    }

    return () => {
      if (intervalId) {
        window.clearInterval(intervalId);
      }
    };
  }, [isPolling, currentTask?.id]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>网站访问模拟器</h1>
        <p className="warning">警告: 请勿用于非法用途，仅用于测试和学习</p>
      </header>

      <main className="app-main">
        {/* 配置表单 */}
        <ConfigForm
          onStartSimulation={handleStartSimulation}
          isLoading={isLoading}
        />

        {/* 实时监控 */}
        {currentTask && (
          <TaskMonitor task={currentTask} />
        )}
      </main>

      <footer className="app-footer">
        <p>网站访问模拟器 - 用于测试和学习目的</p>
      </footer>
    </div>
  );
}

export default App;
