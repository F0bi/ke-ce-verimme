const { spawn } = require('child_process');

// Path to your Python script
const pythonScript = '../main.py';

// Dynamic value from Node.js
const dynamicValue = 'Hello from Node.js';

export default function handler(req, res) {
  res.status(200).end('Hello Cron!');

  // Spawn a child process
  const pythonProcess = spawn('python3', [pythonScript, dynamicValue]);

  // Listen for data from the Python script
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python Output: ${data}`);
  });

  // Listen for any errors from the Python script
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error from Python: ${data}`);
  });

  // Listen for the process to exit
  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });
}
