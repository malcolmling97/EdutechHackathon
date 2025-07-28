import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import healthRouter from './routes/health';
import folderRouter from './routes/folders';
import spaceRouter from './routes/spaces';
import messageRouter from './routes/messages';
import type { Request, Response, NextFunction } from 'express';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/v1/health', healthRouter);
app.use('/api/v1/folders', folderRouter);
app.use('/api/v1/folders', spaceRouter);
app.use('/api/v1/spaces', messageRouter);

// Error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred'
    }
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});