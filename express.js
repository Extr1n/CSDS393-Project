const express = require('express');
const axios = require('axios');
require('dotenv').config();
const Groq = require('groq');  // Import Groq for your query model
const app = express();
const port = 3000;

// Middleware to parse JSON request bodies
app.use(express.json());

// Route for AI query
app.post('/ask-ai', async (req, res) => {
    const query = req.body.query; // Expecting a 'query' from the frontend in POST request
    
    if (!query) {
        return res.status(400).json({ error: 'No query provided' });
    }

    try {
        const client = new Groq();  // Initialize Groq client
        
        // Send the query to the AI model
        const chatCompletion = await client.chat.completions.create({
            messages: [
                { "role": "system", "content": "You are an advisor for Case Western Reserve University." },
                { "role": "user", "content": query }
            ],
            model: "llama-3.3-70b-versatile",  // Make sure the model name is correct
            temperature: 0.5,
            max_completion_tokens: 1024,
            top_p: 1,
            stop: null,
            stream: false,
        });

        const aiResponse = chatCompletion.choices[0].message.content;
        res.json({ response: aiResponse });  // Return AI response back to the frontend
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
