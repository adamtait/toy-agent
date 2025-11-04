import fs from 'fs/promises';
import path from 'path';

const logsDir = 'logs';

let loggingSetup = false;

async function setupLogging() {
  if (loggingSetup) {
    return;
  }
  try {
    await fs.mkdir(logsDir);
  } catch (error) {
    if (error.code !== 'EEXIST') {
      throw error;
    }
  }
  loggingSetup = true;
}

async function log(data) {
  await setupLogging();
  const timestamp = new Date().toISOString();
  const logFile = path.join(logsDir, `${timestamp}.json`);
  await fs.writeFile(logFile, JSON.stringify(data, null, 2));
}

export { log };
