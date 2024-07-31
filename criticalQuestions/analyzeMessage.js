const OpenAI = require("openai");
const dotenv = require("dotenv");

dotenv.config();

const openai = new OpenAI(process.env.OPENAI_API_KEY);

async function analyzeMessage(message) {
  const completion = await openai.chat.completions.create({
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: `To critically analyze this message: "${message}", what questions should I ask myself about it?` }
    ],
    model: "gpt-3.5-turbo",
  });

  return completion.choices[0];
}
module.exports= {analyzeMessage };