const { MongoClient, ServerApiVersion } = require('mongodb');
require('dotenv').config();

// Get the connection string from environment variables
const uri = process.env.DB_key;

if (!uri) {
    throw new Error('MongoDB connection string not found in environment variables. Please check your .env file.');
}

// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(uri, {
    serverApi: {
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
    }
});

// Function to connect to MongoDB
async function connectToMongoDB() {
    try {
        await client.connect();
        await client.db("admin").command({ ping: 1 });
        console.log("Successfully connected to MongoDB!");
        return client;
    } catch (error) {
        console.error("Error connecting to MongoDB:", error);
        throw error;
    }
}

// Function to search courses
async function searchCourses(query) {
    try {
        const db = client.db("cluster0");
        const courses = db.collection("Documents.Courses");
        
        const results = await courses.find({
            $or: [
                { code: { $regex: query, $options: "i" } },
                { title: { $regex: query, $options: "i" } }
            ]
        }).limit(10).toArray();
        
        return results;
    } catch (error) {
        console.error("Error searching courses:", error);
        throw error;
    }
}

// Function to add a course
async function addCourse(courseData) {
    try {
        const db = client.db("cluster0");
        const userCourses = db.collection("user_courses");
        
        // Check if course already exists
        const existingCourse = await userCourses.findOne({
            caseid: courseData.caseid,
            code: courseData.code
        });
        
        if (existingCourse) {
            throw new Error("Course already exists in your list");
        }
        
        // Add the course
        await userCourses.insertOne(courseData);
        return { message: "Course added successfully" };
    } catch (error) {
        console.error("Error adding course:", error);
        throw error;
    }
}

// Export the functions
module.exports = {
    connectToMongoDB,
    searchCourses,
    addCourse
}; 