const http = require('http');
const fs = require('fs');

http.get('http://localhost:8000/api/v1/rankings/volume-rank-by-theme?market=ALL', (res) => {
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
    });
    res.on('end', () => {
        fs.writeFileSync('node_out.txt', data);
        console.log('done');
    });
}).on("error", (err) => {
    fs.writeFileSync('node_out.txt', "Error: " + err.message);
});
