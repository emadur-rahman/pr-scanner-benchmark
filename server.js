const express = require('express');
const { exec } = require('child_process');
const app = express();

const API_KEY = "sk_live_xK9mP2qR8vL3nJ5wT7yB4cF6hD1eG0aZ";

app.use(express.json());

app.post('/report/generate', (req, res) => {
    const format = req.body.format;
    exec('generate-report --format ' + format, (err, stdout) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ output: stdout });
    });
});

app.listen(3000);
