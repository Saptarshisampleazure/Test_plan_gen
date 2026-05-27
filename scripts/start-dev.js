const { spawn } = require('child_process');
const { join } = require('path');
const fs = require('fs');
const net = require('net');

const root = join(__dirname, '..');
const backend = join(root, 'backend');
const isWin = process.platform === 'win32';

function isPortOpen(port, host = '127.0.0.1') {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    socket.setTimeout(1000);
    socket.on('connect', () => {
      socket.destroy();
      resolve(true);
    });
    socket.on('error', () => resolve(false));
    socket.on('timeout', () => resolve(false));
    socket.connect(port, host);
  });
}

async function start() {
  if (isWin) {
    const ps = join(__dirname, 'start-dev.ps1');
    const p = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-File', ps], { stdio: 'inherit' });
    p.on('close', (code) => process.exit(code));
    return;
  }

  const backendPortOpen = await isPortOpen(8000);
  if (!backendPortOpen) {
    const venvPy = join(backend, '.venv', 'bin', 'python');
    if (!fs.existsSync(venvPy)) {
      console.error(`Backend virtual environment was not found at ${venvPy}`);
    } else {
      console.log('Starting backend...');
      spawn(venvPy, ['-m', 'uvicorn', 'app.main:app', '--reload', '--reload-dir', 'app', '--host', '127.0.0.1', '--port', '8000'], {
        cwd: backend,
        stdio: 'inherit',
      });
    }
  } else {
    console.log('Backend already running on http://127.0.0.1:8000/');
  }

  const frontendPortOpen = await isPortOpen(5173);
  if (!frontendPortOpen) {
    console.log('Starting frontend dev server...');
    spawn('npm', ['run', 'dev:frontend'], { cwd: root, stdio: 'inherit' });
  } else {
    console.log('Frontend already running on http://127.0.0.1:5173/');
  }
}

start().catch((err) => {
  console.error(err);
  process.exit(1);
});
