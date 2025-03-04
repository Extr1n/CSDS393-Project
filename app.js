const express = require('express');
const axios = require('axios');
const cors = require('cors');  // Add this line
require('dotenv').config();
const app = express();
const port = 3000;

// Middleware to enable CORS
app.use(cors());

// Middleware to parse JSON request bodies
app.use(express.json());

// Route for AI query
app.get('/ask-ai', async (req, res) => {
    const query = req.query.query;

    if (!query) {
        return res.status(400).json({ error: 'No query provided' });
    }

    try {
        const client = new Groq();
        
        const chatCompletion = await client.chat.completions.create({
            messages: [
                { "role": "system", "content": "You are an advisor for Case Western Reserve University." },
                { "role": "user", "content": query }
            ],
            model: "llama-3.3-70b-versatile",
            temperature: 0.5,
            max_completion_tokens: 1024,
            top_p: 1,
            stop: null,
            stream: false,
        });

        const aiResponse = chatCompletion.choices[0].message.content;
        res.json({ response: aiResponse });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
