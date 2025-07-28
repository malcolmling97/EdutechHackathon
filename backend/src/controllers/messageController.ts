import { Request, Response } from 'express';
import { Pool } from 'pg';
import { OpenAI } from 'openai';
import dotenv from 'dotenv';

dotenv.config();

// Initialize PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

/**
 * Get messages for a specific space
 */
export const getMessages = async (req: Request, res: Response) => {
  const { spaceId } = req.params;
  const userId = req.headers['x-user-id'] as string;

  if (!userId) {
    return res.status(401).json({
      error: {
        code: 'UNAUTHORIZED',
        message: 'User ID is required'
      }
    });
  }

  try {
    // Check if space exists and belongs to the user
    const spaceResult = await pool.query(
      `SELECT s.id FROM spaces s 
       JOIN folders f ON s.folder_id = f.id 
       WHERE s.id = $1 AND f.owner_id = $2`,
      [spaceId, userId]
    );

    if (spaceResult.rows.length === 0) {
      return res.status(404).json({
        error: {
          code: 'NOT_FOUND',
          message: 'Space not found or access denied'
        }
      });
    }

    // Get messages for the space
    const messagesResult = await pool.query(
      `SELECT id, content, role, created_at 
       FROM messages 
       WHERE space_id = $1 
       ORDER BY created_at ASC`,
      [spaceId]
    );

    return res.json({
      data: {
        messages: messagesResult.rows.map(msg => ({
          id: msg.id,
          content: msg.content,
          role: msg.role,
          createdAt: msg.created_at
        }))
      }
    });
  } catch (error) {
    console.error(`[getMessages] Error fetching messages for spaceId ${spaceId}:`, error);
    console.error(`[getMessages] Query parameters: spaceId=${spaceId}, userId=${userId}`);
    return res.status(500).json({
      error: {
        code: 'SERVER_ERROR',
        message: 'Error fetching messages: ' + (error instanceof Error ? error.message : String(error))
      }
    });
  }
};

/**
 * Send a new message to a space and get AI response
 */
export const sendMessage = async (req: Request, res: Response) => {
  const { spaceId } = req.params;
  const { content } = req.body;
  const userId = req.headers['x-user-id'] as string;

  if (!userId) {
    return res.status(401).json({
      error: {
        code: 'UNAUTHORIZED',
        message: 'User ID is required'
      }
    });
  }

  if (!content || typeof content !== 'string') {
    return res.status(400).json({
      error: {
        code: 'INVALID_REQUEST',
        message: 'Message content is required'
      }
    });
  }

  try {
    // Check if space exists and belongs to the user
    const spaceResult = await pool.query(
      `SELECT s.id FROM spaces s 
       JOIN folders f ON s.folder_id = f.id 
       WHERE s.id = $1 AND f.owner_id = $2`,
      [spaceId, userId]
    );

    if (spaceResult.rows.length === 0) {
      return res.status(404).json({
        error: {
          code: 'NOT_FOUND',
          message: 'Space not found or access denied'
        }
      });
    }

    // Begin transaction
    const client = await pool.connect();
    try {
      await client.query('BEGIN');

      // Save user message
      const userMessageResult = await client.query(
        `INSERT INTO messages (id, space_id, role, content, created_at)
         VALUES (uuid_generate_v4(), $1, 'user', $2, NOW())
         RETURNING id, content, role, created_at`,
        [spaceId, content]
      );

      const userMessage = userMessageResult.rows[0];

      // Get conversation history
      const historyResult = await client.query(
        `SELECT content, role 
         FROM messages 
         WHERE space_id = $1 
         ORDER BY created_at ASC`,
        [spaceId]
      );

      // Format messages for OpenAI API
      const messages = historyResult.rows.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Call OpenAI API
      const completion = await openai.chat.completions.create({
        model: "gpt-4o",
        messages: messages,
        temperature: 0.7,
        max_tokens: 1000,
      });

      const aiResponse = completion.choices[0].message.content;

      // Save AI response
      const aiMessageResult = await client.query(
        `INSERT INTO messages (id, space_id, role, content, created_at)
         VALUES (uuid_generate_v4(), $1, 'assistant', $2, NOW())
         RETURNING id, content, role, created_at`,
        [spaceId, aiResponse]
      );

      const aiMessage = aiMessageResult.rows[0];

      await client.query('COMMIT');

      return res.json({
        data: {
          userMessage: {
            id: userMessage.id,
            content: userMessage.content,
            role: userMessage.role,
            createdAt: userMessage.created_at
          },
          assistantMessage: {
            id: aiMessage.id,
            content: aiMessage.content,
            role: aiMessage.role,
            createdAt: aiMessage.created_at
          }
        }
      });
    } catch (err) {
      await client.query('ROLLBACK');
      throw err;
    } finally {
      client.release();
    }
  } catch (error) {
    console.error(`[sendMessage] Error sending message for spaceId ${spaceId}:`, error);
    console.error(`[sendMessage] Query parameters: spaceId=${spaceId}, userId=${userId}`);
    console.error(`[sendMessage] Message content length: ${content.length}`);
    return res.status(500).json({
      error: {
        code: 'SERVER_ERROR',
        message: 'Error sending message: ' + (error instanceof Error ? error.message : String(error))
      }
    });
  }
};
