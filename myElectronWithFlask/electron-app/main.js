const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let flaskProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.loadFile('index.html');

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (flaskProcess) flaskProcess.kill();
  });
}

app.on('ready', () => {
  const flaskExecutable = path.join(__dirname, '..', 'flask-app', 'dist', 'app');
  flaskProcess = spawn(flaskExecutable);

  flaskProcess.stdout.on('data', (data) => {
    console.log(`[Flask]: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`[Flask]: ${data}`);
  });

  flaskProcess.on('error', (err) => {
    console.error(`Failed to start Flask process: ${err.message}`);
  });

  createWindow();
});

  

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});