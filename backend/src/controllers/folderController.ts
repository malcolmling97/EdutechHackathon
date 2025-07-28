import { Request, Response } from 'express';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function getFolders(req: Request, res: Response) {
  try {
    const userId = req.headers['x-user-id'] || '00000000-0000-0000-0000-000000000001';
    
    const result = await pool.query(
      'SELECT * FROM folders WHERE owner_id = $1 ORDER BY created_at DESC',
      [userId]
    );
    
    return res.status(200).json({
      data: result.rows,
      meta: { total: result.rowCount }
    });
  } catch (error) {
    console.error('Error fetching folders:', error);
    return res.status(500).json({ 
      error: { 
        code: 'INTERNAL_ERROR', 
        message: 'Failed to fetch folders' 
      } 
    });
  }
}
