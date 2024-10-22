const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const { exec } = require('child_process');
const path = require('path');

let pythonProcess;
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: true, // Required for secure IPC usage
      enableRemoteModule: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  pythonProcess = exec('dist/your_flask_app.exe'); // Start Python app
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    pythonProcess.kill(); // Stop Python process when Electron app closes
    app.quit();
  }
});

// Handle file selection via Electron's dialog
ipcMain.handle('dialog:selectFile', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile']
  });
  if (canceled || filePaths.length === 0) {
    return null; // No file selected
  } else {
    return filePaths[0]; // Return selected file path
  }
});