import { networkInterfaces } from 'os';

const PORT = process.env.PORT || 5000;

console.log('Server will be accessible at:');
console.log(`- http://localhost:${PORT}`);
console.log(`- http://127.0.0.1:${PORT}`);

// Get network interfaces
const interfaces = networkInterfaces();
for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
        if (iface.family === 'IPv4' && !iface.internal) {
            console.log(`- http://${iface.address}:${PORT}`);
        }
    }
}
