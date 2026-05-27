const { spawn, spawnSync } = require('child_process');
const { join } = require('path');
const fs = require('fs');

const root = join(__dirname, '..');
const backend = join(root, 'backend');
const isWin = process.platform === 'win32';

if (isWin) {
  const ps = join(__dirname, 'start-app.ps1');
  const p = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-File', ps], { stdio: 'inherit' });
  p.on('close', (code) => process.exit(code));
} else {
  console.log('Building frontend...');
  const build = spawnSync('npm', ['run', 'build'], { cwd: root, stdio: 'inherit' });
  if (build.status !== 0) process.exit(build.status);

  const venvPy = join(backend, '.venv', 'bin', 'python');
  if (!fs.existsSync(venvPy)) {
    console.error(`Backend virtual environment was not found at ${venvPy}`);
    process.exit(1);
  }

  console.log('Starting Python backend with the built frontend mounted.');
  console.log('Open: http://127.0.0.1:8000/');

  const proc = spawn(venvPy, ['-m', 'uvicorn', 'app.main:app', '--reload', '--reload-dir', 'app', '--host', '127.0.0.1', '--port', '8000'], {
    cwd: backend,
    stdio: 'inherit',
  });

  proc.on('close', (code) => process.exit(code));
}
