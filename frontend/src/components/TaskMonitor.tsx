import React from 'react';
import type { SimulationStatus } from '../types';

interface TaskMonitorProps {
  task: SimulationStatus;
}

const TaskMonitor: React.FC<TaskMonitorProps> = ({ task }) => {
  return (
    <section className="monitor-section">
      <h2>实时监控</h2>
      <div className="task-info">
        <div className="task-header">
          <h3>任务 ID: {task.id}</h3>
          <span className={`status-badge ${task.status}`}>
            {task.status === 'running' ? '运行中' : task.status === 'completed' ? '已完成' : '失败'}
          </span>
        </div>
        <div className="task-stats">
          <div className="stat-item">
            <span className="stat-label">成功次数:</span>
            <span className="stat-value success">{task.success_count}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">失败次数:</span>
            <span className="stat-value fail">{task.fail_count}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">总次数:</span>
            <span className="stat-value">{task.success_count + task.fail_count}</span>
          </div>
        </div>
        <div className="results-list">
          <h4>访问结果:</h4>
          <ul>
            {task.results.slice().reverse().slice(0, 5).map((result) => (
              <li key={result.id} className={`result-item ${result.status === 'success' ? 'success' : 'fail'}`}>
                {result.message}
              </li>
            ))}
            {task.results.length > 5 && (
              <li className="result-more">
                ... 还有 {task.results.length - 5} 条结果
              </li>
            )}
          </ul>
        </div>
      </div>
    </section>
  );
};

export default TaskMonitor;
