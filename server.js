const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
    if (req.url === '/' || req.url === '/index.html') {
        fs.readFile('index.html', 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500);
                res.end('Error loading file');
                return;
            }
            
            // Inject API key
            const apiKey = process.env.GEMINI_API_KEY || '';
            const content = data.replace('GEMINI_API_KEY_PLACEHOLDER', apiKey);
            
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(content);
        });
    } else {
        // Serve other files
        const filePath = path.join(__dirname, req.url.slice(1));
        fs.readFile(filePath, (err, data) => {
            if (err) {
                res.writeHead(404);
                res.end('File not found');
                return;
            }
            res.writeHead(200);
            res.end(data);
        });
    }
});

const PORT = 5000;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`PDF E-Reader with AI server running on port ${PORT}`);
});