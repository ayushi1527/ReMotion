// const express = require("express");
// const bodyParser = require("body-parser");
// const cors = require("cors");

// const app = express();
// app.use(cors());
// app.use(bodyParser.json());

// const users = [
//   { email: "user1@example.com", password: "1234", name: "Aarav" },
//   { email: "user2@example.com", password: "abcd", name: "Diya" }
// ];

// app.post("/login", (req, res) => {
//   const { email, password } = req.body;
//   const user = users.find(u => u.email === email && u.password === password);

//   if (user) {
//     res.json({ message: "Login successful", name: user.name });
//   } else {
//     res.status(401).json({ message: "Invalid email or password" });
//   }
// });

// app.listen(3000, () => console.log("Server running on http://localhost:3000"));


// // --- SIGNUP ENDPOINT (NEW) ---
// app.post("/signup", (req, res) => {
//     const { name, email, password } = req.body;

//     // 1. Validation: Check if user already exists
//     if (users.find(u => u.email === email)) {
//         return res.status(409).json({ message: "Email already registered." });
//     }

//     // 2. Simple password length validation
//     if (!password || password.length < 6) {
//         return res.status(400).json({ message: "Password must be at least 6 characters." });
//     }

//     // 3. Add new user to mock database
//     const newUser = { name, email, password };
//     users.push(newUser);
    
//     // Log the successful registration
//     console.log("New user signed up:", newUser);
//     console.log("Current user count:", users.length);

//     // Respond with success
//     res.status(201).json({ message: "Account created successfully.", name: newUser.name });
// });

// app.listen(3000, () => console.log("Server running on http://localhost:3000"));


const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
// Using a permissive CORS policy for development
app.use(cors()); 
app.use(bodyParser.json());

// Mock database (in-memory array)
const users = [
    { email: "user1@example.com", password: "1234", name: "Aarav" },
    { email: "user2@example.com", password: "abcd", name: "Diya" }
];

// --- LOGIN ENDPOINT ---
app.post("/login", (req, res) => {
    const { email, password } = req.body;
    const user = users.find(u => u.email === email && u.password === password);

    if (user) {
        res.json({ message: "Login successful", name: user.name });
    } else {
        res.status(401).json({ message: "Invalid email or password" });
    }
});

// --- SIGNUP ENDPOINT (NEW) ---
app.post("/signup", (req, res) => {
    const { name, email, password } = req.body;

    // 0. New Check: Ensure all fields are provided
    if (!name || !email || !password) {
        return res.status(400).json({ message: "Missing required fields." });
    }

    // 1. Validation: Check if user already exists
    if (users.find(u => u.email === email)) {
        return res.status(409).json({ message: "Email already registered." });
    }

    // 2. Simple password length validation
    if (password.length < 6) {
        // Updated condition to be safer
        return res.status(400).json({ message: "Password must be at least 6 characters." });
    }

    // 3. Add new user to mock database
    const newUser = { name, email, password };
    users.push(newUser);
    
    // Log the successful registration
    console.log("New user signed up:", newUser);
    // 🌟 Check the total user count after signup 🌟
    console.log("Current user count:", users.length); 

    // Respond with success
    res.status(201).json({ message: "Account created successfully.", name: newUser.name });
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
