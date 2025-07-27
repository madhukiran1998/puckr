"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface User {
  id: string;
  username?: string;
  email?: string;
  avatar_url?: string;
}

interface File {
  id: string;
  name: string;
  description?: string;
  tags?: string[];
  is_public: boolean;
  file_type: "pdf" | "word";
  file_url: string;
  file_size?: number;
  mime_type?: string;
  original_filename: string;
  created_at: string;
  updated_at: string;
}

interface Link {
  id: string;
  title: string;
  description?: string;
  tags?: string[];
  is_public: boolean;
  url: string;
  link_type: "blog" | "twitter" | "youtube" | "github" | "reddit" | "other";
  created_at: string;
  updated_at: string;
}

interface FileListResponse {
  files: File[];
  total: number;
  page: number;
  per_page: number;
}

interface LinkListResponse {
  links: Link[];
  total: number;
  page: number;
  per_page: number;
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [links, setLinks] = useState<Link[]>([]);
  const [activeTab, setActiveTab] = useState<'files' | 'links'>('files');
  const [isUploading, setIsUploading] = useState(false);
  const [isAddingLink, setIsAddingLink] = useState(false);
  
  // File upload form state
  const [fileForm, setFileForm] = useState({
    name: '',
    description: '',
    tags: '',
    is_public: false
  });
  
  // Link form state
  const [linkForm, setLinkForm] = useState({
    title: '',
    description: '',
    url: '',
    tags: '',
    is_public: false
  });

  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Check if there's a token in URL (from OAuth redirect)
    const tokenFromUrl = searchParams.get("token");
    if (tokenFromUrl) {
      localStorage.setItem("jwt_token", tokenFromUrl);
      // Remove token from URL without refreshing
      window.history.replaceState({}, document.title, "/");
    }

    // Check authentication
    const checkAuth = async () => {
      const token = localStorage.getItem("jwt_token");
      if (!token) {
        setIsLoading(false);
        router.push("/login");
        return;
      }

      try {
        const res = await fetch("http://localhost:8000/api/auth/me", {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        });
        
        if (res.ok) {
          const userData = await res.json();
          setUser(userData);
          setIsAuthenticated(true);
          // Load initial data
          loadFiles();
          loadLinks();
        } else {
          // Token is invalid, remove it
          localStorage.removeItem("jwt_token");
          router.push("/login");
        }
      } catch (e) {
        console.error("Auth check failed:", e);
        localStorage.removeItem("jwt_token");
        router.push("/login");
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router, searchParams]);

  const getAuthHeaders = () => ({
    "Authorization": `Bearer ${localStorage.getItem("jwt_token")}`,
  });

  const loadFiles = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/files/", {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data: FileListResponse = await res.json();
        setFiles(data.files);
      }
    } catch (error) {
      console.error("Failed to load files:", error);
    }
  };

  const loadLinks = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/links/", {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data: LinkListResponse = await res.json();
        setLinks(data.links);
      }
    } catch (error) {
      console.error("Failed to load links:", error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', fileForm.name || file.name);
    formData.append('description', fileForm.description);
    formData.append('tags', fileForm.tags);
    formData.append('is_public', fileForm.is_public.toString());

    try {
      const res = await fetch("http://localhost:8000/api/files/upload", {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      });

      if (res.ok) {
        await loadFiles();
        // Reset form
        setFileForm({
          name: '',
          description: '',
          tags: '',
          is_public: false
        });
        event.target.value = '';
      } else {
        const error = await res.json();
        const errorMessage = error.detail || error.message || 'Upload failed';
        alert(`Upload failed: ${errorMessage}`);
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleAddLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAddingLink(true);

    try {
      const res = await fetch("http://localhost:8000/api/links/", {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: linkForm.title,
          description: linkForm.description,
          url: linkForm.url,
          tags: linkForm.tags ? linkForm.tags.split(',').map(tag => tag.trim()) : [],
          is_public: linkForm.is_public,
        }),
      });

      if (res.ok) {
        await loadLinks();
        // Reset form
        setLinkForm({
          title: '',
          description: '',
          url: '',
          tags: '',
          is_public: false
        });
      } else {
        const error = await res.json();
        console.error("Link creation error response:", error);
        const errorMessage = error.detail || error.message || JSON.stringify(error);
        alert(`Failed to add link: ${errorMessage}`);
      }
    } catch (error) {
      console.error("Add link error:", error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to add link';
      alert(`Failed to add link: ${errorMessage}`);
    } finally {
      setIsAddingLink(false);
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    if (!confirm("Are you sure you want to delete this file?")) return;

    try {
      const res = await fetch(`http://localhost:8000/api/files/${fileId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (res.ok) {
        await loadFiles();
      } else {
        alert("Failed to delete file");
      }
    } catch (error) {
      console.error("Delete file error:", error);
      alert("Failed to delete file");
    }
  };

  const handleDeleteLink = async (linkId: string) => {
    if (!confirm("Are you sure you want to delete this link?")) return;

    try {
      const res = await fetch(`http://localhost:8000/api/links/${linkId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (res.ok) {
        await loadLinks();
      } else {
        alert("Failed to delete link");
      }
    } catch (error) {
      console.error("Delete link error:", error);
      alert("Failed to delete link");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    router.push("/login");
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Loading...</div>
      </main>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">Puckr</h1>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Welcome,</span>
                <span className="font-medium">{user?.username || user?.email}</span>
                {user?.avatar_url && (
                  <img 
                    src={user.avatar_url} 
                    alt="Avatar" 
                    className="w-8 h-8 rounded-full"
                  />
                )}
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('files')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'files'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Files ({files.length})
            </button>
            <button
              onClick={() => setActiveTab('links')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'links'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Links ({links.length})
            </button>
          </nav>
        </div>

        {/* Content */}
        {activeTab === 'files' && (
          <div className="space-y-6">
            {/* File Upload Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Upload File</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    File Name
                  </label>
                  <input
                    type="text"
                    value={fileForm.name}
                    onChange={(e) => setFileForm({...fileForm, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter file name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <input
                    type="text"
                    value={fileForm.description}
                    onChange={(e) => setFileForm({...fileForm, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter description"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={fileForm.tags}
                    onChange={(e) => setFileForm({...fileForm, tags: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="file-public"
                    checked={fileForm.is_public}
                    onChange={(e) => setFileForm({...fileForm, is_public: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="file-public" className="ml-2 block text-sm text-gray-900">
                    Make public
                  </label>
                </div>
              </div>
              <div className="mt-4">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {isUploading && <p className="mt-2 text-sm text-gray-600">Uploading...</p>}
              </div>
            </div>

            {/* Files List */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Your Files</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {files.length === 0 ? (
                  <div className="px-6 py-8 text-center text-gray-500">
                    No files uploaded yet. Upload your first file above.
                  </div>
                ) : (
                  files.map((file) => (
                    <div key={file.id} className="px-6 py-4 flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <span className="text-blue-600 font-medium text-sm">
                              {file.file_type.toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">{file.name}</h4>
                          <p className="text-sm text-gray-500">{file.description}</p>
                          <div className="flex items-center space-x-4 mt-1">
                            <span className="text-xs text-gray-400">
                              {formatFileSize(file.file_size)}
                            </span>
                            <span className="text-xs text-gray-400">
                              {formatDate(file.created_at)}
                            </span>
                            {file.is_public && (
                              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                Public
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <a
                          href={file.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          View
                        </a>
                        <button
                          onClick={() => handleDeleteFile(file.id)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'links' && (
          <div className="space-y-6">
            {/* Add Link Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Add Link</h2>
              <form onSubmit={handleAddLink} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Title
                    </label>
                    <input
                      type="text"
                      required
                      value={linkForm.title}
                      onChange={(e) => setLinkForm({...linkForm, title: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter link title"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      URL
                    </label>
                    <input
                      type="url"
                      required
                      value={linkForm.url}
                      onChange={(e) => setLinkForm({...linkForm, url: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://example.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <input
                      type="text"
                      value={linkForm.description}
                      onChange={(e) => setLinkForm({...linkForm, description: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter description"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tags (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={linkForm.tags}
                      onChange={(e) => setLinkForm({...linkForm, tags: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="tag1, tag2, tag3"
                    />
                  </div>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="link-public"
                    checked={linkForm.is_public}
                    onChange={(e) => setLinkForm({...linkForm, is_public: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="link-public" className="ml-2 block text-sm text-gray-900">
                    Make public
                  </label>
                </div>
                <button
                  type="submit"
                  disabled={isAddingLink}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {isAddingLink ? 'Adding...' : 'Add Link'}
                </button>
              </form>
            </div>

            {/* Links List */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Your Links</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {links.length === 0 ? (
                  <div className="px-6 py-8 text-center text-gray-500">
                    No links added yet. Add your first link above.
                  </div>
                ) : (
                  links.map((link) => (
                    <div key={link.id} className="px-6 py-4 flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                            <span className="text-green-600 font-medium text-sm">
                              {link.link_type.toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">{link.title}</h4>
                          <p className="text-sm text-gray-500">{link.description}</p>
                          <a
                            href={link.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800 block mt-1"
                          >
                            {link.url}
                          </a>
                          <div className="flex items-center space-x-4 mt-1">
                            <span className="text-xs text-gray-400">
                              {formatDate(link.created_at)}
                            </span>
                            {link.is_public && (
                              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                Public
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteLink(link.id)}
                        className="text-red-600 hover:text-red-800 text-sm font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
