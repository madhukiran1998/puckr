-- =============================================================================
-- PUCKR DATABASE SCHEMA FOR SUPABASE
-- =============================================================================
-- This file contains the SQL schema for storing files and links in Supabase
-- Run these commands in your Supabase SQL editor to set up the database

-- =============================================================================
-- ENABLE EXTENSIONS
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- FILES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    file_type VARCHAR(50) NOT NULL CHECK (file_type IN ('pdf', 'word')),
    file_path TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    original_filename VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- LINKS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    url TEXT NOT NULL,
    link_type VARCHAR(50) NOT NULL CHECK (link_type IN ('blog', 'twitter', 'youtube', 'github', 'reddit', 'other')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Files table indexes
CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_file_type ON files(file_type);
CREATE INDEX IF NOT EXISTS idx_files_created_at ON files(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_files_is_public ON files(is_public);
CREATE INDEX IF NOT EXISTS idx_files_tags ON files USING GIN(tags);

-- Links table indexes
CREATE INDEX IF NOT EXISTS idx_links_user_id ON links(user_id);
CREATE INDEX IF NOT EXISTS idx_links_link_type ON links(link_type);
CREATE INDEX IF NOT EXISTS idx_links_created_at ON links(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_links_is_public ON links(is_public);
CREATE INDEX IF NOT EXISTS idx_links_tags ON links USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_links_url ON links(url);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for files table
CREATE TRIGGER update_files_updated_at 
    BEFORE UPDATE ON files 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Triggers for links table
CREATE TRIGGER update_links_updated_at 
    BEFORE UPDATE ON links 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================

-- Enable RLS on tables
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE links ENABLE ROW LEVEL SECURITY;

-- Files table policies
CREATE POLICY "Users can view their own files" ON files
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own files" ON files
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own files" ON files
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own files" ON files
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Public files can be viewed by anyone" ON files
    FOR SELECT USING (is_public = true);

-- Links table policies
CREATE POLICY "Users can view their own links" ON links
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own links" ON links
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own links" ON links
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own links" ON links
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Public links can be viewed by anyone" ON links
    FOR SELECT USING (is_public = true);

-- =============================================================================
-- STORAGE BUCKET SETUP
-- =============================================================================

-- Create storage bucket for files (run this in Supabase dashboard or via API)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('files', 'files', true);

-- Storage policies for files bucket
CREATE POLICY "Users can upload their own files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'files' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can view their own files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'files' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can update their own files" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'files' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete their own files" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'files' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Public files can be viewed by anyone" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'files' AND 
        EXISTS (
            SELECT 1 FROM files 
            WHERE file_path = name AND is_public = true
        )
    ); 