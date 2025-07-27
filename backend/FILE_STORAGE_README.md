# File and Link Storage System

This document explains how to set up and use the simplified file and link storage system in your Puckr backend.

## Overview

The system supports two main types of content:

1. **Files**: PDFs and Word documents only
2. **Links**: URLs to blogs, Twitter/X, YouTube, GitHub, Reddit, and other websites

Both are linked to users and support tagging, descriptions, and public/private visibility.

## Database Schema

### Files Table
- `id`: Unique identifier (UUID)
- `user_id`: Reference to auth.users table
- `name`: Display name for the file
- `description`: Optional description
- `tags`: Array of tags for categorization
- `is_public`: Whether the file is publicly accessible
- `file_type`: Type of file (pdf, word)
- `file_path`: Storage path in Supabase
- `file_url`: Public URL for accessing the file
- `file_size`: File size in bytes
- `mime_type`: MIME type of the file
- `original_filename`: Original filename from upload
- `created_at`, `updated_at`: Timestamps

### Links Table
- `id`: Unique identifier (UUID)
- `user_id`: Reference to auth.users table
- `title`: Display title for the link
- `description`: Optional description
- `tags`: Array of tags for categorization
- `is_public`: Whether the link is publicly accessible
- `url`: The actual URL
- `link_type`: Type of link (blog, twitter, youtube, github, reddit, other)
- `created_at`, `updated_at`: Timestamps

## Setup Instructions

### 1. Database Setup

1. Go to your Supabase dashboard
2. Navigate to the SQL Editor
3. Copy and paste the contents of `database_schema.sql`
4. Execute the SQL commands

### 2. Storage Bucket Setup

1. In your Supabase dashboard, go to Storage
2. Create a new bucket called `files`
3. Set it as public (if you want public file access)
4. The storage policies are already defined in the schema

### 3. Environment Variables

Make sure your `.env` file includes:

```env
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
```

## API Endpoints

### Files

#### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data

file: [PDF or Word file]
name: "My Document"
description: "Optional description"
tags: "document,important,work"
is_public: false
```

#### List Files
```http
GET /api/files/?page=1&per_page=20&file_type=pdf&search=report
```

#### Get File Details
```http
GET /api/files/{file_id}
```

#### Update File
```http
PUT /api/files/{file_id}
Content-Type: multipart/form-data

name: "Updated Name"
description: "Updated description"
tags: "new,tags"
is_public: true
```

#### Delete File
```http
DELETE /api/files/{file_id}
```

### Links

#### Create Link
```http
POST /api/links/
Content-Type: application/json

{
  "title": "My Blog Post",
  "description": "A great article about technology",
  "tags": ["blog", "technology"],
  "url": "https://example.com/blog/post",
  "link_type": "blog",
  "is_public": false
}
```

#### List Links
```http
GET /api/links/?page=1&per_page=20&link_type=blog&search=technology
```

#### Get Link Details
```http
GET /api/links/{link_id}
```

#### Update Link
```http
PUT /api/links/{link_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "tags": ["updated", "tags"]
}
```

#### Delete Link
```http
DELETE /api/links/{link_id}
```

## Supported File Types

### Documents
- PDF (.pdf)
- Word (.doc, .docx)

## Supported Link Types

### Auto-Detected
- **Twitter/X**: twitter.com, x.com
- **YouTube**: youtube.com, youtu.be
- **GitHub**: github.com
- **Reddit**: reddit.com
- **Blogs**: medium.com, dev.to, hashnode.dev, substack.com, blogspot.com, wordpress.com
- **Other**: Any other website

### Features
- Automatic link type detection
- Simple and clean API

## Security Features

### Row Level Security (RLS)
- Users can only access their own files and links
- Public files/links can be viewed by anyone
- Proper authentication required for all operations

### Storage Security
- Files are stored in user-specific folders
- Storage policies ensure users can only access their own files
- Public files have special access policies

### File Upload Limits
- Maximum file size: 50MB
- Only PDF and Word files allowed
- Secure file naming with UUIDs

## Usage Examples

### Python Client Example

```python
import requests

# Upload a file
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    data = {
        'name': 'My Document',
        'description': 'Important document',
        'tags': 'document,important',
        'is_public': False
    }
    response = requests.post(
        'http://localhost:8000/api/files/upload',
        files=files,
        data=data,
        headers={'Authorization': 'Bearer your-jwt-token'}
    )

# Create a link
link_data = {
    'title': 'Great Article',
    'description': 'Must read article',
    'url': 'https://medium.com/article',
    'tags': ['blog', 'technology'],
    'is_public': True
}
response = requests.post(
    'http://localhost:8000/api/links/',
    json=link_data,
    headers={'Authorization': 'Bearer your-jwt-token'}
)
```

### JavaScript/TypeScript Client Example

```typescript
// Upload a file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('name', 'My Document');
formData.append('description', 'Important document');
formData.append('tags', 'document,important');
formData.append('is_public', 'false');

const response = await fetch('/api/files/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

// Create a link
const linkData = {
  title: 'Great Article',
  description: 'Must read article',
  url: 'https://medium.com/article',
  tags: ['blog', 'technology'],
  is_public: true
};

const response = await fetch('/api/links/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(linkData)
});
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid data or unsupported file type)
- `401`: Unauthorized (missing or invalid token)
- `403`: Forbidden (user doesn't own the resource)
- `404`: Not found
- `413`: File too large
- `500`: Internal server error

## Performance Considerations

- Files are stored in Supabase Storage for scalability
- Database indexes optimize queries by user, type, and date
- Pagination is implemented for large datasets
- File metadata is cached in the database
- GIN indexes on tags for efficient tag-based searches 