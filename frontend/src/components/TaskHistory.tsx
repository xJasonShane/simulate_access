import React from 'react';
import { SimulationStatus } from '../types';

interface TaskHistoryProps {
  tasks: SimulationStatus[];
  onViewTask: (task: SimulationStatus) => void;
  onDeleteTask: (taskId: string) => void;
}

const TaskHistory: React.FC<TaskHistoryProps> = ({ tasks, onViewTask, onDeleteTask }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <section className="history-section">
      <h2>历史任务</h2>
      {tasks.length === 0 ? (
        <p className="no-tasks">暂无任务记录</p>
      ) : (
        <div className="tasks-list">
          {tasks.map((task) => (
            <div key={task.id} className="task-card">
              <div className="task-header">
                <h3>任务 ID: {task.id}</h3>
                <span className={`status-badge ${task.status}`}>
                  {task.status === 'running' ? '运行中' : task.status === 'completed' ? '已完成' : '失败'}
                </span>
              </div>
              <div className="task-info-small">
                <p><strong>URL:</strong> {task.url}</p>
                <p><strong>创建时间:</strong> {formatDate(task.created_at)}</p>
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
                  onClick={() => onViewTask(task)}
                >
                  查看详情
                </button>
                <button
                  className="delete-btn"
                  onClick={() => onDeleteTask(task.id)}
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default TaskHistory;
