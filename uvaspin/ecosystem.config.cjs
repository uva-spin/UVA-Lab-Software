module.exports = {
  apps: [{
    name: 'uvaspin',
    cwd: __dirname,
    script: './src/server.js',
    interpreter: 'node',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 5000
    }
  }]
};
