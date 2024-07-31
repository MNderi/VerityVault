const express = require('express');
const app = express();
const cors = require('cors');
app.use(cors());
app.use(express.json());

const { finePredict } = require('./finepredictor');
const {explainFineMessage} =require('./explainFineLogic');

app.get('/', (req, res) => {
    res.send('Welcome to the Fine Prediction Service!');
  });

app.post('/finepredict', async (req, res) => {
  const { input } = req.body;
  if (!input) return res.status(400).json({ error: 'Text is required' });
  try {
    const result = await finePredict(input);
    res.json(result);
  } catch (error) {
    console.error('Error during prediction:', error);
    res.status(500).json({ error: 'Failed to make prediction' });
  }
});
app.post('/explainfine', async (req, res) => {
    const { input } = req.body;
  
    if (!input) {
      return res.status(400).json({ error: "Input is required" });
    }
  
    try {
      const { predictedClass, classScores } = await finePredict(input);
      const explanation = await explainFineMessage(input, predictedClass, classScores);
      res.json({ predictedClass, classScores, explanation });
    } catch (error) {
      console.error(error);
      res.status(500).json({ error: "Internal Server Error" });
    }
  });

app.listen(3000, () => console.log('fine Prediction service listening on port 3000!'));
