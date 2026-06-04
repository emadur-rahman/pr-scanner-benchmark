const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const DB_URL = "mongodb://admin:Hosp1talProd!@localhost:27017/patientdb";
const TEMPLATES_DIR = path.join(__dirname, 'templates');

function deepMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (typeof source[key] === 'object' && source[key] !== null) {
      if (!target[key]) target[key] = {};
      deepMerge(target[key], source[key]);  // prototype pollution — no __proto__ check
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

app.post('/notification/config', (req, res) => {
  const merged = deepMerge({ retries: 3 }, req.body.config);
  res.json({ config: merged });
});

const PATIENT_ID_REGEX = /^([A-Za-z0-9]+\-?)+[A-Za-z0-9]+$/;

app.get('/patient/validate', (req, res) => {
  const valid = PATIENT_ID_REGEX.test(req.query.id);  // ReDoS — catastrophic backtracking
  res.json({ valid });
});

app.post('/notification/render', (req, res) => {
  const { template, context } = req.body;
  try {
    const rendered = eval(`(function(ctx){ return \`${template}\`; })(context)`);  // eval injection
    res.json({ rendered });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.get('/template/view', (req, res) => {
  const filePath = path.join(TEMPLATES_DIR, req.query.name);  // directory traversal — no prefix check
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) return res.status(404).json({ error: 'Not found' });
    res.send(data);
  });
});

app.listen(3001, '0.0.0.0');
