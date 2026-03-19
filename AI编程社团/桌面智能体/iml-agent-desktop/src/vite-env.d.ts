/// <reference types="vite/client" />

interface ElectronStore {
  get: (key: string) => Promise<any>;
  set: (key: string, value: any) => Promise<void>;
  delete: (key: string) => Promise<void>;
}

interface CommandResult {
  success: boolean;
  stdout: string;
  stderr: string;
  error?: string;
}

interface ExternalResult {
  success: boolean;
  error?: string;
}

interface FileSystemAPI {
  selectFile: () => Promise<{ path: string; name: string; content: string } | null>;
  executeCommand: (command: string) => Promise<CommandResult>;
  openExternal: (url: string) => Promise<ExternalResult>;
}

interface Window {
  electronStore: ElectronStore;
  fileSystem?: FileSystemAPI;
}
