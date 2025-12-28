import React, { useState } from 'react';
import type { SimulationConfig } from '../types';

interface ConfigFormProps {
  onStartSimulation: (config: SimulationConfig) => void;
  isLoading: boolean;
}

const ConfigForm: React.FC<ConfigFormProps> = ({ onStartSimulation, isLoading }) => {
  const [config, setConfig] = useState<SimulationConfig>({
    url: '',
    min_interval: 2,
    max_interval: 5,
    count: 10,
    timeout: 10,
    retries: 0,
    retry_delay: 1,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!config.url) {
      alert('请输入目标URL');
      return;
    }
    onStartSimulation(config);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: isNaN(Number(value)) ? 0 : Number(value),
    }));
  };

  return (
    <section className="config-section">
      <h2>配置模拟访问</h2>
      <form className="config-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="url">目标URL</label>
            <input
              type="text"
              id="url"
              name="url"
              value={config.url}
              onChange={(e) => setConfig(prev => ({ ...prev, url: e.target.value }))}
              placeholder="https://example.com 或 example.com"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="min_interval">最小间隔 (秒)</label>
            <input
              type="number"
              id="min_interval"
              name="min_interval"
              value={config.min_interval}
              onChange={handleInputChange}
              min="1"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="max_interval">最大间隔 (秒)</label>
            <input
              type="number"
              id="max_interval"
              name="max_interval"
              value={config.max_interval}
              onChange={handleInputChange}
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
              name="count"
              value={config.count}
              onChange={handleInputChange}
              min="1"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="timeout">超时时间 (秒)</label>
            <input
              type="number"
              id="timeout"
              name="timeout"
              value={config.timeout}
              onChange={handleInputChange}
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
              name="retries"
              value={config.retries}
              onChange={handleInputChange}
              min="0"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="retry_delay">重试延迟 (秒)</label>
            <input
              type="number"
              id="retry_delay"
              name="retry_delay"
              value={config.retry_delay}
              onChange={handleInputChange}
              min="0"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          className="start-btn"
          disabled={isLoading}
        >
          {isLoading ? '开始中...' : '开始模拟访问'}
        </button>
      </form>
    </section>
  );
};

export default ConfigForm;
