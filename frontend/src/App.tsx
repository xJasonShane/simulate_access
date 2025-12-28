import React, { useState, useEffect } from 'react';
import './App.css';
import { SimulationConfig, SimulationStatus } from './types';
import { startSimulation, getSimulationStatus, getAllTasks, deleteTask } from './api';

function App() {
  // 配置表单状态
  const [config, setConfig] = useState<SimulationConfig>({
    url: '',
    min_interval: 2,
    max_interval: 5,
    count: 10,
    timeout: 10,
    retries: 0,
    retry_delay: 1,
  });

  // 模拟状态
  const [currentTask, setCurrentTask] = useState<SimulationStatus | null>(null);
  const [tasks, setTasks] = useState<SimulationStatus[]>([]);
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
  const handleStartSimulation = async () => {
    if (!config.url) {
      alert('请输入目标URL');
      return;
    }

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

  // 轮询获取任务状态
  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (isPolling && currentTask?.status === 'running') {
      intervalId = setInterval(async () => {
        try {
          const updatedTask = await getSimulationStatus(currentTask.task_id);
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
  }, [isPolling, currentTask]);

  // 初始加载任务
  useEffect(() => {
    fetchTasks();
  }, []);

  // 删除任务
  const handleDeleteTask = async (taskId: string) => {
    if (window.confirm('确定要删除该任务吗？')) {
      try {
        await deleteTask(taskId);
        fetchTasks();
        if (currentTask?.task_id === taskId) {
          setCurrentTask(null);
          setIsPolling(false);
        }
      } catch (error) {
        console.error('删除任务失败:', error);
      }
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>网站访问模拟器</h1>
        <p className="warning">警告: 请勿用于非法用途，仅用于测试和学习</p>
      </header>

      <main className="app-main">
        {/* 配置表单 */}
        <section className="config-section">
          <h2>配置模拟访问</h2>
          <form className="config-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="url">目标URL</label>
                <input
                  type="text"
                  id="url"
                  value={config.url}
                  onChange={(e) => setConfig({ ...config, url: e.target.value })}
                  placeholder="https://example.com 或 example.com"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="min-interval">最小间隔 (秒)</label>
                <input
                  type="number"
                  id="min-interval"
                  value={config.min_interval}
                  onChange={(e) => setConfig({ ...config, min_interval: parseInt(e.target.value) })}
                  min="1"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="max-interval">最大间隔 (秒)</label>
                <input
                  type="number"
                  id="max-interval"
                  value={config.max_interval}
                  onChange={(e) => setConfig({ ...config, max_interval: parseInt(e.target.value) })}
                  min="1"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="count">访问次数</label>
                <input
                  type="number"
                  id="count"
                  value={config.count}
                  onChange={(e) => setConfig({ ...config, count: parseInt(e.target.value) })}
                  min="1"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="timeout">超时时间 (秒)</label>
                <input
                  type="number"
                  id="timeout"
                  value={config.timeout}
                  onChange={(e) => setConfig({ ...config, timeout: parseInt(e.target.value) })}
                  min="1"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="retries">重试次数</label>
                <input
                  type="number"
                  id="retries"
                  value={config.retries}
                  onChange={(e) => setConfig({ ...config, retries: parseInt(e.target.value) })}
                  min="0"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="retry-delay">重试延迟 (秒)</label>
                <input
                  type="number"
                  id="retry-delay"
                  value={config.retry_delay}
                  onChange={(e) => setConfig({ ...config, retry_delay: parseInt(e.target.value) })}
                  min="0"
                  required
                />
              </div>
            </div>

            <button
              type="button"
              className="start-btn"
              onClick={handleStartSimulation}
              disabled={isLoading}
            >
              {isLoading ? '开始中...' : '开始模拟访问'}
            </button>
          </form>
        </section>

        {/* 实时监控 */}
        {currentTask && (
          <section className="monitor-section">
            <h2>实时监控</h2>
            <div className="task-info">
              <div className="task-header">
                <h3>任务 ID: {currentTask.task_id}</h3>
                <span className={`status-badge ${currentTask.status}`}>
                  {currentTask.status === 'running' ? '运行中' : currentTask.status === 'completed' ? '已完成' : '失败'}
                </span>
              </div>
              <div className="task-stats">
                <div className="stat-item">
                  <span className="stat-label">成功次数:</span>
                  <span className="stat-value success">{currentTask.success_count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">失败次数:</span>
                  <span className="stat-value fail">{currentTask.fail_count}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">总次数:</span>
                  <span className="stat-value">{currentTask.success_count + currentTask.fail_count}</span>
                </div>
              </div>
              <div className="results-list">
                <h4>访问结果:</h4>
                <ul>
                  {currentTask.results.slice().reverse().slice(0, 5).map((result, index) => (
                    <li key={index} className={`result-item ${result.success ? 'success' : 'fail'}`}>
                      {result.message}
                    </li>
                  ))}
                  {currentTask.results.length > 5 && (
                    <li className="result-more">
                      ... 还有 {currentTask.results.length - 5} 条结果
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </section>
        )}

        {/* 历史记录 */}
        <section className="history-section">
          <h2>历史任务</h2>
          {tasks.length === 0 ? (
            <p className="no-tasks">暂无任务记录</p>
          ) : (
            <div className="tasks-list">
              {tasks.map((task) => (
                <div key={task.task_id} className="task-card">
                  <div className="task-header">
                    <h3>任务 ID: {task.task_id}</h3>
                    <span className={`status-badge ${task.status}`}>
                      {task.status === 'running' ? '运行中' : task.status === 'completed' ? '已完成' : '失败'}
                    </span>
                  </div>
                  <div className="task-stats">
                    <div className="stat-item">
                      <span className="stat-label">成功:</span>
                      <span className="stat-value success">{task.success_count}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">失败:</span>
                      <span className="stat-value fail">{task.fail_count}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">总次数:</span>
                      <span className="stat-value">{task.success_count + task.fail_count}</span>
                    </div>
                  </div>
                  <div className="task-actions">
                    <button
                      className="view-btn"
                      onClick={() => setCurrentTask(task)}
                    >
                      查看详情
                    </button>
                    <button
                      className="delete-btn"
                      onClick={() => handleDeleteTask(task.task_id)}
                    >
                      删除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="app-footer">
        <p>网站访问模拟器 - 用于测试和学习目的</p>
      </footer>
    </div>
  );
}

export default App;
