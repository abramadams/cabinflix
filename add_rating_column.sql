-- Add rating column to existing movies table
ALTER TABLE movies ADD COLUMN IF NOT EXISTS rating VARCHAR(10);
