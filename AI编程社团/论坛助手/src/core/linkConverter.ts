// 类型定义
export interface Config {
  sourceDomain: string;
  targetDomain: string;
  sourceProtocol: string;
  targetProtocol: string;
}

export interface LinkInfo {
  original: string;
  converted: string;
  changed: boolean;
}

export interface ConvertResult {
  content: string;
  links: LinkInfo[];
  linkCount: number;
}

// 提取纯文本中的URL
export function extractUrls(text: string): string[] {
  const urlRegex = /https?:\/\/[^\s<>"']+/gi;
  return text.match(urlRegex) || [];
}

// 提取HTML中的链接
export function extractHtmlLinks(html: string): { tag: string; href: string; index: number }[] {
  const linkRegex = /<a[^>]*href=["']([^"']+)["'][^>]*>/gi;
  const links: { tag: string; href: string; index: number }[] = [];
  let match;

  while ((match = linkRegex.exec(html)) !== null) {
    links.push({
      tag: match[0],
      href: match[1],
      index: match.index,
    });
  }

  return links;
}

// 解析域名
export function parseUrl(url: string): { protocol: string; domain: string; path: string } {
  try {
    const match = url.match(/^(https?:\/\/)?([^/]+)(\/.*)?$/);
    if (!match) {
      return { protocol: 'http:', domain: '', path: '' };
    }
    return {
      protocol: match[1] || 'http:',
      domain: match[2] || '',
      path: match[3] || '/',
    };
  } catch {
    return { protocol: 'http:', domain: '', path: '' };
  }
}

// 转换URL
export function convertUrl(url: string, config: Config): string {
  const parsed = parseUrl(url);

  // 检查是否匹配源域名
  if (parsed.domain !== config.sourceDomain) {
    return url; // 不匹配，不转换
  }

  // 构建新URL
  const newProtocol = config.targetProtocol.endsWith(':')
    ? config.targetProtocol
    : config.targetProtocol + ':';

  return `${newProtocol}//${config.targetDomain}${parsed.path}`;
}

// 转换HTML内容
export function convertHtml(html: string, config: Config): ConvertResult {
  const links = extractHtmlLinks(html);
  let result = html;
  const linkInfos: LinkInfo[] = [];

  // 从后往前替换，避免索引偏移问题
  for (let i = links.length - 1; i >= 0; i--) {
    const link = links[i];
    const converted = convertUrl(link.href, config);
    const newTag = link.tag.replace(link.href, converted);

    result = result.substring(0, link.index) + newTag + result.substring(link.index + link.tag.length);

    linkInfos.push({
      original: link.href,
      converted,
      changed: link.href !== converted,
    });
  }

  // 反转数组使顺序正确
  linkInfos.reverse();

  return {
    content: result,
    links: linkInfos,
    linkCount: links.length,
  };
}

// 转换纯文本内容
export function convertPlainText(text: string, config: Config): ConvertResult {
  const urls = extractUrls(text);
  let result = text;
  const linkInfos: LinkInfo[] = [];

  // 从后往前替换
  for (let i = urls.length - 1; i >= 0; i--) {
    const url = urls[i];
    const converted = convertUrl(url, config);
    const index = result.lastIndexOf(url);

    result = result.substring(0, index) + converted + result.substring(index + url.length);

    linkInfos.push({
      original: url,
      converted,
      changed: url !== converted,
    });
  }

  linkInfos.reverse();

  return {
    content: result,
    links: linkInfos,
    linkCount: urls.length,
  };
}

// 主转换函数 - 自动检测内容类型
export function convertContent(content: string, config: Config): ConvertResult {
  // 检测是否为HTML（包含HTML标签）
  const isHtml = /<[a-z][\s\S]*>/i.test(content);

  if (isHtml) {
    return convertHtml(content, config);
  } else {
    return convertPlainText(content, config);
  }
}

// 检测内容中的链接（不转换，只检测）
export function detectLinks(content: string): LinkInfo[] {
  const isHtml = /<[a-z][\s\S]*>/i.test(content);

  if (isHtml) {
    const result = convertHtml(content, {
      sourceDomain: '',
      targetDomain: '',
      sourceProtocol: '',
      targetProtocol: '',
    });
    return result.links;
  } else {
    const result = convertPlainText(content, {
      sourceDomain: '',
      targetDomain: '',
      sourceProtocol: '',
      targetProtocol: '',
    });
    return result.links;
  }
}
