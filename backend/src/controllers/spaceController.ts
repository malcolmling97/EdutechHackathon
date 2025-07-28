import { Request, Response } from 'express';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function getSpaces(req: Request, res: Response) {
  try {
    const { folderId } = req.params;
    
    const result = await pool.query(
      'SELECT * FROM spaces WHERE folder_id = $1 ORDER BY created_at DESC',
      [folderId]
    );
    
    return res.status(200).json({
      data: result.rows,
      meta: { total: result.rowCount }
    });
  } catch (error) {
    console.error('Error fetching spaces:', error);
    return res.status(500).json({ 
      error: { 
        code: 'INTERNAL_ERROR', 
        message: 'Failed to fetch spaces' 
      } 
    });
  }
}

export async function createSpace(req: Request, res: Response) {
  try {
    const { folderId } = req.params;
    const { title, type = 'chat' } = req.body;
    const userId = req.headers['x-user-id'] as string;
    
    console.log(`[spaceController] Creating space in folder: ${folderId}, type: ${type}, title: ${title}`);
    
    // Verify folder exists and belongs to user
    const folderResult = await pool.query(
      'SELECT id FROM folders WHERE id = $1 AND owner_id = $2',
      [folderId, userId]
    );
    
    if (folderResult.rowCount === 0) {
      console.log(`[spaceController] Folder not found or access denied for folder: ${folderId}, user: ${userId}`);
      return res.status(404).json({
        error: {
          code: 'NOT_FOUND',
          message: 'Folder not found or access denied'
        }
      });
    }
    
    // Create the space
    const result = await pool.query(
      'INSERT INTO spaces (folder_id, type, title) VALUES ($1, $2, $3) RETURNING *',
      [folderId, type, title]
    );
    
    const newSpace = result.rows[0];
    console.log(`[spaceController] Space created successfully: ${newSpace.id}`);
    
    return res.status(201).json({
      data: newSpace
    });
  } catch (error) {
    console.error('Error creating space:', error);
    return res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to create space'
      }
    });
  }
}
