import express from 'express';
import dotenv from 'dotenv';
import healthRouter from './routes/health';
import type { Request, Response, NextFunction } from 'express';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

app.use(express.json());

app.use('/api/v1/health', healthRouter);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
}); 