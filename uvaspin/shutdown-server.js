#!/usr/bin/env node

import http from 'http';

const PORT = process.env.PORT || 5000;
const HOST = process.env.HOST || 'localhost';

console.log(`Attempting to shutdown server at http://${HOST}:${PORT}`);

const postData = JSON.stringify({});

const options = {
    hostname: HOST,
    port: PORT,
    path: '/shutdown',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
    }
};

const req = http.request(options, (res) => {
    console.log(`Response status: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        try {
            const response = JSON.parse(data);
            console.log('Server response:', response.message);
        } catch (e) {
            console.log('Server response:', data);
        }
        console.log('Shutdown request sent successfully');
    });
});

req.on('error', (error) => {
    console.error('Error sending shutdown request:', error.message);
    console.log('Server may already be stopped or not running on the expected port');
    process.exit(1);
});

req.write(postData);
req.end();
