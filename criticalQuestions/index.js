const express = require('express');
const bodyParser = require('body-parser');
const { analyzeMessage } = require('./analyzeMessage');
const cors = require('cors'); // Import cors package

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Enable CORS for all origins
app.use(cors());

// Endpoint for analyzing messages
app.post('/analyze', async (req, res) => {
  const { message } = req.body;

  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  try {
    const analysisResult = await analyzeMessage(message);
    res.json({ analysisResult });
  } catch (error) {
    console.error('Error analyzing message:', error);
    res.status(500).json({ error: 'Error analyzing message' });
  }
});

// Default route
app.get('/', (req, res) => {
  res.send('OpenAI Message Analyzer');
});

// Start server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
