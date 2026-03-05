const { execSync } = require('child_process');

try {
    console.log("Stopping container...");
    execSync('docker stop stocktheme-backend', { stdio: 'inherit' });
    console.log("Removing container...");
    execSync('docker rm stocktheme-backend', { stdio: 'inherit' });
    console.log("Starting compose...");
    execSync('docker-compose up -d --build backend', { stdio: 'inherit' });
    console.log("SUCCESS");
} catch (e) {
    console.error("ERROR", e);
}
