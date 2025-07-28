// Simple script to create a test folder in the database
const { Pool } = require('pg');
require('dotenv').config();

// Database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function createTestFolder() {
  try {
    console.log('Creating test folder in database...');
    
    // Check if folder already exists
    const checkResult = await pool.query(
      'SELECT * FROM folders WHERE id = $1',
      ['00000000-0000-0000-0000-000000000001']
    );
    
    if (checkResult.rowCount > 0) {
      console.log('Test folder already exists:', checkResult.rows[0]);
      return;
    }
    
    // Create test folder
    const result = await pool.query(
      'INSERT INTO folders (id, title, owner_id) VALUES ($1, $2, $3) RETURNING *',
      ['00000000-0000-0000-0000-000000000001', 'Test Folder', '00000000-0000-0000-0000-000000000001']
    );
    
    console.log('Test folder created successfully:', result.rows[0]);
  } catch (error) {
    console.error('Error creating test folder:', error);
  } finally {
    // Close the pool
    await pool.end();
  }
}

// Run the function
createTestFolder();
