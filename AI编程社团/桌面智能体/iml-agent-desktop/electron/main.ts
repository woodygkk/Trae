import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron';
import path from 'path';
import Store from 'electron-store';
import fs from 'fs/promises';
import { exec } from 'child_process';

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
import('electron-squirrel-startup').then((squirrelStartup) => {
  if (squirrelStartup.default) {
    app.quit();
  }
});

const setupStore = () => {
  const store = new Store();

  ipcMain.handle('store-get', (_event, key) => {
    return store.get(key);
  });

  ipcMain.handle('store-set', (_event, key, value) => {
    store.set(key, value);
  });

  ipcMain.handle('store-delete', (_event, key) => {
    store.delete(key as any);
  });
};

const setupFileHandlers = () => {
  ipcMain.handle('dialog-open-file', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
      properties: ['openFile'],
      filters: [
        { name: 'Text/Code', extensions: ['txt', 'md', 'js', 'ts', 'tsx', 'json', 'py', 'html', 'css', 'csv'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (canceled || filePaths.length === 0) {
      return null;
    }

    try {
      const content = await fs.readFile(filePaths[0], 'utf-8');
      return {
        path: filePaths[0],
        name: path.basename(filePaths[0]),
        content: content
      };
    } catch (error) {
      console.error('Failed to read file:', error);
      throw error;
    }
  });

  // Execute terminal command
  ipcMain.handle('execute-command', async (_event, command: string) => {
    return new Promise((resolve) => {
      exec(command, { timeout: 30000, maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
        if (error) {
          resolve({ success: false, stdout: stdout, stderr: stderr, error: error.message });
        } else {
          resolve({ success: true, stdout: stdout, stderr: stderr });
        }
      });
    });
  });

  // Open URL in browser
  ipcMain.handle('open-external', async (_event, url: string) => {
    try {
      await shell.openExternal(url);
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  });
};

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: true,
      contextIsolation: true, // Enable context isolation
      webSecurity: false, // Disable web security to allow CORS requests
    },
    titleBarStyle: 'hidden', // Mac style, or custom title bar
    titleBarOverlay: {
      color: '#ffffff',
      symbolColor: '#74b1be'
    }
  });

  // and load the index.html of the app.
  if (!app.isPackaged) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', () => {
  setupStore();
  setupFileHandlers();
  createWindow();
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
