import request from 'supertest';
import express from 'express';
import healthRouter from '../src/routes/health';

describe('GET /api/v1/health', () => {
  const app = express();
  app.use('/api/v1/health', healthRouter);

  it('should return API health status', async () => {
    const res = await request(app).get('/api/v1/health');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('status', 'ok');
  });
}); 