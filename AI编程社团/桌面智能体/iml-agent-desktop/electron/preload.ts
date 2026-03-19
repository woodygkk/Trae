import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronStore', {
  get: (key: string) => ipcRenderer.invoke('store-get', key),
  set: (key: string, value: any) => ipcRenderer.invoke('store-set', key, value),
  delete: (key: string) => ipcRenderer.invoke('store-delete', key),
});

contextBridge.exposeInMainWorld('fileSystem', {
  selectFile: () => ipcRenderer.invoke('dialog-open-file'),
  executeCommand: (command: string) => ipcRenderer.invoke('execute-command', command),
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
});
