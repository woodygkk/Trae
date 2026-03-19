import { useState, useEffect, useCallback } from 'react';
import { Config, convertContent, LinkInfo } from './core/linkConverter';
import { loadConfig } from './core/configManager';
import { ConfigPanel } from './components/ConfigPanel';
import { InputPanel } from './components/InputPanel';
import { OutputPanel } from './components/OutputPanel';
import './App.css';

function App() {
  const [inputContent, setInputContent] = useState('');
  const [outputContent, setOutputContent] = useState('');
  const [config, setConfig] = useState<Config>(loadConfig());
  const [links, setLinks] = useState<LinkInfo[]>([]);
  const [linkCount, setLinkCount] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [isConverted, setIsConverted] = useState(false);

  // 当输入内容或配置变化时，自动检测链接
  useEffect(() => {
    if (!inputContent) {
      setLinks([]);
      setLinkCount(0);
      return;
    }

    const result = convertContent(inputContent, config);
    setLinks(result.links);
    setLinkCount(result.linkCount);
  }, [inputContent, config]);

  // 执行转换
  const handleConvert = useCallback(() => {
    if (!inputContent) {
      setStatusMessage('请先输入内容');
      return;
    }

    const result = convertContent(inputContent, config);
    setOutputContent(result.content);
    setLinks(result.links);
    setLinkCount(result.linkCount);
    setIsConverted(true);
    setStatusMessage(`转换完成，已处理 ${result.linkCount} 个链接`);

    // 3秒后清除状态消息
    setTimeout(() => setStatusMessage(''), 3000);
  }, [inputContent, config]);

  // 复制成功回调
  const handleCopySuccess = () => {
    setStatusMessage('已复制到剪贴板');
    setTimeout(() => setStatusMessage(''), 2000);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>链接转换工具</h1>
        <div className="header-actions">
          <button className="btn-settings">设置</button>
        </div>
      </header>

      <main className="app-main">
        <div className="three-column-layout">
          <InputPanel content={inputContent} onChange={setInputContent} />

          <div className="config-column">
            <ConfigPanel config={config} onConfigChange={setConfig} />
            <button
              className="btn-convert"
              onClick={handleConvert}
              disabled={!inputContent}
            >
              开始转换
            </button>
          </div>

          <OutputPanel
            content={outputContent}
            links={isConverted ? links : []}
            onCopy={handleCopySuccess}
          />
        </div>
      </main>

      <footer className="app-footer">
        <span className="status">
          {statusMessage || `已识别 ${linkCount} 个链接`}
        </span>
      </footer>
    </div>
  );
}

export default App;
