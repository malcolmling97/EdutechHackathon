# EdutechHackathon Backend

This is the backend API for EdutechHackathon, built with **Express** and **TypeScript**.

## Tech Stack
- Node.js
- Express.js
- TypeScript
- dotenv (environment variables)
- Jest (testing)
- Nodemon (development)

## Folder Structure
```
backend/
├── src/
│   ├── controllers/
│   ├── middleware/
│   ├── models/
│   ├── routes/
│   └── utils/
├── tests/
├── .env.example
├── package.json
├── tsconfig.json
└── README.md
```

## Setup Instructions

1. **Install dependencies:**
   ```bash
   npm install
   ```
2. **Copy and configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```
3. **Run in development mode:**
   ```bash
   npm run dev
   ```
4. **Build for production:**
   ```bash
   npm run build
   ```
5. **Run tests:**
   ```bash
   npm test
   ```

## Sample Health Route
After starting the server, visit [http://localhost:4000/api/v1/health](http://localhost:4000/api/v1/health) to verify the backend is running. 