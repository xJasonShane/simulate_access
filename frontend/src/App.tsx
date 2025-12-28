import React, { useState, useEffect } from 'react';
import './App.css';
import { SimulationConfig, SimulationStatus, TaskListItem } from './types';
import { startSimulation, getSimulationStatus, getAllTasks, deleteTask, getTaskDetails } from './api';
import ConfigForm from './components/ConfigForm';
import TaskMonitor from './components/TaskMonitor';
import TaskHistory from './components/TaskHistory';

function App() {
  // 模拟状态
  const [currentTask, setCurrentTask] = useState<SimulationStatus | null>(null);
  const [tasks, setTasks] = useState<TaskListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);

  // 获取所有任务
  const fetchTasks = async () => {
    try {
      const allTasks = await getAllTasks();
      setTasks(allTasks);
    } catch (error) {
      console.error('获取任务失败:', error);
    }
  };

  // 开始模拟访问
  const handleStartSimulation = async (config: SimulationConfig) => {
    try {
      setIsLoading(true);
      const task = await startSimulation(config);
      setCurrentTask(task);
      setIsPolling(true);
      fetchTasks();
    } catch (error: any) {
      alert(`开始模拟失败: ${error.response?.data?.detail || '未知错误'}`);
      console.error('开始模拟失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 查看任务详情
  const handleViewTask = async (taskId: string) => {
    try {
      setIsLoading(true);
      const task = await getTaskDetails(taskId);
      setCurrentTask(task);
      setIsPolling(task.status === 'running');
    } catch (error) {
      console.error('获取任务详情失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 删除任务
  const handleDeleteTask = async (taskId: string) => {
    if (window.confirm('确定要删除该任务吗？')) {
      try {
        await deleteTask(taskId);
        fetchTasks();
        if (currentTask?.id === taskId) {
          setCurrentTask(null);
          setIsPolling(false);
        }
      } catch (error) {
        console.error('删除任务失败:', error);
      }
    }
  };

  // 轮询获取任务状态
  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (isPolling && currentTask?.id) {
      intervalId = setInterval(async () => {
        try {
          const updatedTask = await getSimulationStatus(currentTask.id);
          setCurrentTask(updatedTask);
          
          // 如果任务已完成或失败，停止轮询
          if (updatedTask.status !== 'running') {
            setIsPolling(false);
            fetchTasks();
          }
        } catch (error) {
          console.error('获取任务状态失败:', error);
          setIsPolling(false);
        }
      }, 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isPolling, currentTask?.id]);

  // 初始加载任务
  useEffect(() => {
    fetchTasks();
  }, []);

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

        {/* 历史记录 */}
        <TaskHistory
          tasks={tasks}
          onViewTask={(task) => handleViewTask(task.id)}
          onDeleteTask={handleDeleteTask}
        />
      </main>

      <footer className="app-footer">
        <p>网站访问模拟器 - 用于测试和学习目的</p>
      </footer>
    </div>
  );
}

export default App;
