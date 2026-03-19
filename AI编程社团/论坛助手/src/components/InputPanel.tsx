interface InputPanelProps {
  content: string;
  onChange: (content: string) => void;
}

export function InputPanel({ content, onChange }: InputPanelProps) {
  const handleClear = () => {
    onChange('');
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      onChange(text);
    } catch (error) {
      console.error('Failed to read clipboard:', error);
    }
  };

  return (
    <div className="input-panel">
      <div className="panel-header">
        <h3>输入内容</h3>
        <div className="panel-actions">
          <button className="btn-secondary" onClick={handlePaste}>
            粘贴
          </button>
          <button className="btn-secondary" onClick={handleClear}>
            清空
          </button>
        </div>
      </div>

      <div className="panel-content">
        <textarea
          value={content}
          onChange={(e) => onChange(e.target.value)}
          placeholder="在此粘贴或输入需要转换的内容...
支持 HTML 格式和纯文本"
          className="content-textarea"
        />
      </div>
    </div>
  );
}
