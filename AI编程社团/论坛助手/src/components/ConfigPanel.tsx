import { useState, useEffect } from 'react';
import { Config } from '../core/linkConverter';
import { loadConfig, saveConfig, defaultConfig } from '../core/configManager';

interface ConfigPanelProps {
  config: Config;
  onConfigChange: (config: Config) => void;
}

export function ConfigPanel({ config, onConfigChange }: ConfigPanelProps) {
  const [localConfig, setLocalConfig] = useState<Config>(config);

  useEffect(() => {
    const saved = loadConfig();
    setLocalConfig(saved);
    onConfigChange(saved);
  }, []);

  const handleChange = (field: keyof Config, value: string) => {
    const newConfig = { ...localConfig, [field]: value };
    setLocalConfig(newConfig);
    saveConfig(newConfig);
    onConfigChange(newConfig);
  };

  const handleReset = () => {
    setLocalConfig(defaultConfig);
    saveConfig(defaultConfig);
    onConfigChange(defaultConfig);
  };

  return (
    <div className="config-panel">
      <div className="config-header">
        <h3>转换配置</h3>
        <button className="btn-reset" onClick={handleReset}>
          重置
        </button>
      </div>

      <div className="config-form">
        <div className="form-group">
          <label>原域名</label>
          <input
            type="text"
            value={localConfig.sourceDomain}
            onChange={(e) => handleChange('sourceDomain', e.target.value)}
            placeholder="例如: itsk.com"
          />
        </div>

        <div className="form-group">
          <label>新域名</label>
          <input
            type="text"
            value={localConfig.targetDomain}
            onChange={(e) => handleChange('targetDomain', e.target.value)}
            placeholder="例如: 192.168.1.168:8090"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>原协议</label>
            <select
              value={localConfig.sourceProtocol}
              onChange={(e) => handleChange('sourceProtocol', e.target.value)}
            >
              <option value="https">https://</option>
              <option value="http">http://</option>
            </select>
          </div>

          <div className="form-group">
            <label>新协议</label>
            <select
              value={localConfig.targetProtocol}
              onChange={(e) => handleChange('targetProtocol', e.target.value)}
            >
              <option value="http">http://</option>
              <option value="https">https://</option>
            </select>
          </div>
        </div>
      </div>

      <div className="config-preview">
        <div className="preview-item">
          <span className="preview-label">转换示例:</span>
          <span className="preview-value">
            {localConfig.sourceProtocol}://{localConfig.sourceDomain}/thread/123
            <span className="arrow">→</span>
            {localConfig.targetProtocol}://{localConfig.targetDomain}/thread/123
          </span>
        </div>
      </div>
    </div>
  );
}
