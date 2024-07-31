const express = require('express');
const cors = require('cors');
const app = express();
app.use(express.json());
app.use(cors());


const { coarsePredict } = require('./coarsepredictor');
const { explainMessage } = require('./explainLogic');

app.get('/', (req, res) => {
  res.send('Welcome to the Coarse Prediction Service!');
});
app.post('/coarsepredict', async (req, res) => {
  const { input } = req.body;
  if (!input) return res.status(400).json({ error: 'Text is required' });
  try {
    const result = await coarsePredict(input);
    res.json(result);
  } catch (error) {
    console.error('Error during prediction:', error);
    res.status(500).json({ error: 'Failed to make prediction' });
  }
});
app.post('/explaincoarse', async (req, res) => {
  const { input } = req.body;

  if (!input) {
    return res.status(400).json({ error: "Input is required" });
  }

  try {
    const { predictedClass, classScores } = await coarsePredict(input);
    const explanation = await explainMessage(input, predictedClass, classScores);
    res.json({ predictedClass, classScores, explanation });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});
app.listen(3000, () => console.log('Coarse Prediction service listening on port 3000!'));
