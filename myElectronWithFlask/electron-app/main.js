const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

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

function copyExecutableToTempDir(sourcePath) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'flask-'));
  const destPath = path.join(tempDir, 'app');
  
  try {
    // Copy the executable to a writable temporary directory
    fs.copyFileSync(sourcePath, destPath);
    fs.chmodSync(destPath, '755');
    return destPath;
  } catch (err) {
    console.error(`Failed to copy executable: ${err.message}`);
    return null;
  }
}

app.on('ready', () => {
  // Determine the path to the Flask executable
  let flaskExecutable;
  
  // Check if running in development or packaged environment
  if (app.isPackaged) {
    // For packaged app, use the executable in the app's resources
    flaskExecutable = path.join(process.resourcesPath, 'flask-app', 'dist', 'app');
  } else {
    // For development, use the local path
    flaskExecutable = path.join(__dirname, 'flask-app', 'dist', 'app');
  }

  console.log(`Attempting to run Flask executable from: ${flaskExecutable}`);

  // Verify the executable exists before trying to spawn
  if (!fs.existsSync(flaskExecutable)) {
    console.error(`Flask executable not found at: ${flaskExecutable}`);
    console.error(`Contents of resources path: ${fs.readdirSync(process.resourcesPath)}`);
    app.quit();
    return;
  }

  // Handle read-only filesystem by copying to a temporary directory
  const executablePath = copyExecutableToTempDir(flaskExecutable);
  
  if (!executablePath) {
    console.error('Failed to prepare Flask executable');
    app.quit();
    return;
  }

  // Spawn the Flask process
  flaskProcess = spawn(executablePath);

  flaskProcess.stdout.on('data', (data) => {
    console.log(`[Flask]: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`[Flask]: ${data}`);
  });

  flaskProcess.on('error', (err) => {
    console.error(`Failed to start Flask process: ${err.message}`);
    app.quit();
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