-- Create a test folder for development
INSERT INTO folders (id, title, owner_id) 
VALUES 
  ('00000000-0000-0000-0000-000000000001', 'Test Folder', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;
