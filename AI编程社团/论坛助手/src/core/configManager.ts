import { Config } from './linkConverter';

const CONFIG_KEY = 'link-converter-config';

// 默认配置
export const defaultConfig: Config = {
  sourceDomain: 'itsk.com',
  targetDomain: '192.168.1.168:8090',
  sourceProtocol: 'https',
  targetProtocol: 'http',
};

// 保存配置到 localStorage
export function saveConfig(config: Config): void {
  try {
    localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
  } catch (error) {
    console.error('Failed to save config:', error);
  }
}

// 加载配置
export function loadConfig(): Config {
  try {
    const saved = localStorage.getItem(CONFIG_KEY);
    if (saved) {
      return { ...defaultConfig, ...JSON.parse(saved) };
    }
  } catch (error) {
    console.error('Failed to load config:', error);
  }
  return defaultConfig;
}

// 重置配置
export function resetConfig(): Config {
  localStorage.removeItem(CONFIG_KEY);
  return defaultConfig;
}
