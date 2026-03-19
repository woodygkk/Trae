import { LinkInfo } from '../core/linkConverter';

interface OutputPanelProps {
  content: string;
  links: LinkInfo[];
  onCopy: () => void;
}

export function OutputPanel({ content, links, onCopy }: OutputPanelProps) {
  const renderHighlightedContent = () => {
    if (!content) {
      return <div className="placeholder">转换结果将显示在这里</div>;
    }

    // 为HTML内容创建高亮版本
    let highlighted = content;

    // 标记已转换的链接
    links.forEach((link) => {
      if (link.changed) {
        // 替换href中的链接
        const escapedOriginal = link.original.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(escapedOriginal, 'g');
        highlighted = highlighted.replace(
          regex,
          `<span class="link-changed">${link.converted}</span>`
        );
      }
    });

    return (
      <div
        className="content-preview"
        dangerouslySetInnerHTML={{ __html: highlighted }}
      />
    );
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      onCopy();
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  return (
    <div className="output-panel">
      <div className="panel-header">
        <h3>转换结果</h3>
        <div className="panel-actions">
          <button className="btn-primary" onClick={handleCopy} disabled={!content}>
            复制结果
          </button>
        </div>
      </div>

      <div className="panel-content">{renderHighlightedContent()}</div>

      {links.length > 0 && (
        <div className="link-list">
          <h4>检测到的链接 ({links.length})</h4>
          <ul>
            {links.map((link, index) => (
              <li key={index} className={link.changed ? 'changed' : ''}>
                <span className="original">{link.original}</span>
                {link.changed && (
                  <>
                    <span className="arrow">→</span>
                    <span className="converted">{link.converted}</span>
                  </>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
