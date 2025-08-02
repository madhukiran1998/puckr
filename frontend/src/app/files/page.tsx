"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

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

interface FileSummary {
  file_id: string;
  summary: string;
  key_points: string[];
  document_type: string;
  word_count: number;
  created_at: string;
  service?: string;
  model?: string;
  content_type?: string;
  original_prompt?: string;
}

interface AIResponse {
  success: boolean;
  processing_results: string;
  error?: string;
  service?: string;
  model?: string;
  user_id?: string;
  content_type?: string;
  original_prompt?: string;
}

export default function FilesPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [links, setLinks] = useState<Link[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [fileSummary, setFileSummary] = useState<FileSummary | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [selectedLink, setSelectedLink] = useState<Link | null>(null);
  const [showLinkSummaryModal, setShowLinkSummaryModal] = useState(false);
  const [linkSummaryLoading, setLinkSummaryLoading] = useState(false);
  const [linkSummary, setLinkSummary] = useState<FileSummary | null>(null);
  const [linkSummaryError, setLinkSummaryError] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    // Check authentication
    const checkAuth = async () => {
      const token = localStorage.getItem("jwt_token");
      if (!token) {
        setIsLoading(false);
        router.push("/login");
        return;
      }

      try {
        const response = await fetch("http://localhost:8000/api/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          setIsAuthenticated(true);
          await loadFiles();
          await loadLinks();
        } else {
          localStorage.removeItem("jwt_token");
          router.push("/login");
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        localStorage.removeItem("jwt_token");
        router.push("/login");
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const getAuthHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
  });

  const loadFiles = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/files/", {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data: FileListResponse = await response.json();
        setFiles(data.files);
      } else {
        console.error("Failed to load files");
      }
    } catch (error) {
      console.error("Error loading files:", error);
    }
  };

  const loadLinks = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/links/", {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data: LinkListResponse = await response.json();
        setLinks(data.links);
      } else {
        console.error("Failed to load links");
      }
    } catch (error) {
      console.error("Error loading links:", error);
    }
  };

  const handleGetSummary = async (file: File) => {
    setSelectedFile(file);
    setShowSummaryModal(true);
    setSummaryLoading(true);
    setFileSummary(null);
    setSummaryError(null);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutes timeout
      
      const response = await fetch("http://localhost:8000/ai/process-file", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
        },
        body: JSON.stringify({
          file_id: file.id,
          prompt: `Summarize this document: ${file.name}`,
        }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        const data: AIResponse = await response.json();
        if (data.success) {
          setFileSummary({
            file_id: file.id,
            summary: data.processing_results,
            key_points: [], // Mock key points for now
            document_type: file.file_type.toUpperCase(),
            word_count: 0, // Mock word count for now
            created_at: new Date().toISOString(),
            service: data.service,
            model: data.model,
            content_type: data.content_type,
            original_prompt: data.original_prompt,
          });
        } else {
          console.error("AI summarization failed:", data.error || "Unknown error");
          setSummaryError(data.error || "Failed to generate summary. Please try again.");
          setFileSummary({
            file_id: file.id,
            summary: "Failed to generate summary.",
            key_points: [],
            document_type: file.file_type.toUpperCase(),
            word_count: 0,
            created_at: new Date().toISOString(),
          });
        }
      } else {
        const errorData = await response.json();
        console.error("AI summarization failed with status:", response.status, errorData);
        setSummaryError("Failed to connect to AI service. Please try again.");
        setFileSummary({
          file_id: file.id,
          summary: "Failed to generate summary.",
          key_points: [],
          document_type: file.file_type.toUpperCase(),
          word_count: 0,
          created_at: new Date().toISOString(),
        });
      }
    } catch (error: unknown) {
      console.error("Error getting file summary:", error);
      
      let errorMessage = "An unexpected error occurred. Please try again.";
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = "The request took too long to complete. Please try again with a smaller file or try later.";
        } else if (error.message) {
          errorMessage = error.message;
        }
      }
      
      setSummaryError(errorMessage);
      setFileSummary({
        file_id: file.id,
        summary: "Failed to generate summary.",
        key_points: [],
        document_type: file.file_type.toUpperCase(),
        word_count: 0,
        created_at: new Date().toISOString(),
      });
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleGetLinkSummary = async (link: Link) => {
    setSelectedLink(link);
    setShowLinkSummaryModal(true);
    setLinkSummaryLoading(true);
    setLinkSummary(null);
    setLinkSummaryError(null);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutes timeout
      
      const response = await fetch("http://localhost:8000/ai/process-link", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
        },
        body: JSON.stringify({
          link_id: link.id,
          prompt: `Summarize this link: ${link.title}`,
        }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        const data: AIResponse = await response.json();
        if (data.success) {
          setLinkSummary({
            file_id: link.id,
            summary: data.processing_results,
            key_points: [], // Mock key points for now
            document_type: "LINK",
            word_count: 0, // Mock word count for now
            created_at: new Date().toISOString(),
            service: data.service,
            model: data.model,
            content_type: data.content_type,
            original_prompt: data.original_prompt,
          });
        } else {
          console.error("AI summarization failed:", data.error || "Unknown error");
          setLinkSummaryError(data.error || "Failed to generate summary. Please try again.");
          setLinkSummary({
            file_id: link.id,
            summary: "Failed to generate summary.",
            key_points: [],
            document_type: "LINK",
            word_count: 0,
            created_at: new Date().toISOString(),
          });
        }
      } else {
        const errorData = await response.json();
        console.error("AI summarization failed with status:", response.status, errorData);
        setLinkSummaryError("Failed to connect to AI service. Please try again.");
        setLinkSummary({
          file_id: link.id,
          summary: "Failed to generate summary.",
          key_points: [],
          document_type: "LINK",
          word_count: 0,
          created_at: new Date().toISOString(),
        });
      }
    } catch (error: unknown) {
      console.error("Error getting link summary:", error);
      
      let errorMessage = "An unexpected error occurred. Please try again.";
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = "The request took too long to complete. Please try again with a smaller file or try later.";
        } else if (error.message) {
          errorMessage = error.message;
        }
      }
      
      setLinkSummaryError(errorMessage);
      setLinkSummary({
        file_id: link.id,
        summary: "Failed to generate summary.",
        key_points: [],
        document_type: "LINK",
        word_count: 0,
        created_at: new Date().toISOString(),
      });
    } finally {
      setLinkSummaryLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    router.push("/login");
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "Unknown size";
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
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push("/")}
                className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Back to Dashboard
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Files & Links</h2>
          <p className="text-gray-600">View and analyze all your stored files and links</p>
        </div>

        {/* Files Section */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Your Files ({files.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {files.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                No files found. Upload some files from the dashboard to get started.
              </div>
            ) : (
              files.map((file) => (
                <div key={file.id} className="px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-blue-600 font-medium text-sm">
                          {file.file_type.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-medium text-gray-900">{file.name}</h4>
                      <p className="text-sm text-gray-500">{file.description}</p>
                      <div className="flex items-center space-x-4 mt-2">
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
                        {file.tags && file.tags.length > 0 && (
                          <div className="flex space-x-1">
                            {file.tags.slice(0, 3).map((tag, index) => (
                              <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                                {tag}
                              </span>
                            ))}
                            {file.tags.length > 3 && (
                              <span className="text-xs text-gray-400">+{file.tags.length - 3} more</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <a
                      href={file.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      View
                    </a>
                    <button
                      onClick={() => handleGetSummary(file)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      Get Summary
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Links Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Your Links ({links.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {links.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                No links found. Add some links from the dashboard to get started.
              </div>
            ) : (
              links.map((link) => (
                <div key={link.id} className="px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-green-600 font-medium text-sm">
                          {link.link_type.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-medium text-gray-900">{link.title}</h4>
                      <p className="text-sm text-gray-500">{link.description}</p>
                      <div className="flex items-center space-x-4 mt-2">
                        <span className="text-xs text-gray-400">
                          {formatDate(link.created_at)}
                        </span>
                        {link.is_public && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                            Public
                          </span>
                        )}
                        {link.tags && link.tags.length > 0 && (
                          <div className="flex space-x-1">
                            {link.tags.slice(0, 3).map((tag, index) => (
                              <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                                {tag}
                              </span>
                            ))}
                            {link.tags.length > 3 && (
                              <span className="text-xs text-gray-400">+{link.tags.length - 3} more</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-600 hover:text-green-800 text-sm font-medium"
                    >
                      Visit Link
                    </a>
                    <button
                      onClick={() => handleGetLinkSummary(link)}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      Get Summary
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Summary Modal */}
      {showSummaryModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  File Summary: {selectedFile?.name}
                </h3>
                <button
                  onClick={() => setShowSummaryModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {summaryLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">Generating summary...</span>
                </div>
              ) : fileSummary ? (
                <div className="space-y-4">
                  {/* Error Message */}
                  {summaryError && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center">
                        <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm text-red-700">{summaryError}</span>
                      </div>
                    </div>
                  )}

                  {/* AI Service Info */}
                  {fileSummary.service && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-sm font-medium text-blue-700">AI Service</span>
                          <p className="text-sm text-blue-600">{fileSummary.service.toUpperCase()}</p>
                        </div>
                        {fileSummary.model && (
                          <div>
                            <span className="text-sm font-medium text-blue-700">Model</span>
                            <p className="text-sm text-blue-600">{fileSummary.model}</p>
                          </div>
                        )}
                        {fileSummary.content_type && (
                          <div>
                            <span className="text-sm font-medium text-blue-700">Content Type</span>
                            <p className="text-sm text-blue-600">{fileSummary.content_type.toUpperCase()}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Summary Stats */}
                  <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <span className="text-sm font-medium text-gray-500">Document Type</span>
                      <p className="text-sm text-gray-900">{fileSummary.document_type}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Word Count</span>
                      <p className="text-sm text-gray-900">{fileSummary.word_count.toLocaleString()}</p>
                    </div>
                  </div>

                  {/* Summary Text */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Summary</h4>
                    <div className="bg-white border rounded-lg p-4">
                      <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">
                        {fileSummary.summary}
                      </p>
                    </div>
                  </div>

                  {/* Key Points - Only show if we have them */}
                  {fileSummary.key_points && fileSummary.key_points.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Key Points</h4>
                      <ul className="space-y-2">
                        {fileSummary.key_points.map((point, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-blue-600 mr-2">•</span>
                            <span className="text-sm text-gray-900">{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Generated Info */}
                  <div className="text-xs text-gray-500 pt-4 border-t">
                    Summary generated on {formatDate(fileSummary.created_at)}
                    {fileSummary.original_prompt && (
                      <div className="mt-1">
                        <span className="font-medium">Original prompt:</span> {fileSummary.original_prompt}
                      </div>
                    )}
                  </div>

                  {/* Retry Button for Failed Summaries */}
                  {summaryError && (
                    <div className="pt-4">
                      <button
                        onClick={() => selectedFile && handleGetSummary(selectedFile)}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                      >
                        Retry Summary Generation
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  Failed to generate summary. Please try again.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Link Summary Modal */}
      {showLinkSummaryModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Link Summary: {selectedLink?.title}
                </h3>
                <button
                  onClick={() => setShowLinkSummaryModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {linkSummaryLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">Generating summary...</span>
                </div>
              ) : linkSummary ? (
                <div className="space-y-4">
                  {/* Error Message */}
                  {linkSummaryError && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center">
                        <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm text-red-700">{linkSummaryError}</span>
                      </div>
                    </div>
                  )}

                  {/* AI Service Info */}
                  {linkSummary.service && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-sm font-medium text-blue-700">AI Service</span>
                          <p className="text-sm text-blue-600">{linkSummary.service.toUpperCase()}</p>
                        </div>
                        {linkSummary.model && (
                          <div>
                            <span className="text-sm font-medium text-blue-700">Model</span>
                            <p className="text-sm text-blue-600">{linkSummary.model}</p>
                          </div>
                        )}
                        {linkSummary.content_type && (
                          <div>
                            <span className="text-sm font-medium text-blue-700">Content Type</span>
                            <p className="text-sm text-blue-600">{linkSummary.content_type.toUpperCase()}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Summary Stats */}
                  <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <span className="text-sm font-medium text-gray-500">Document Type</span>
                      <p className="text-sm text-gray-900">{linkSummary.document_type}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Word Count</span>
                      <p className="text-sm text-gray-900">{linkSummary.word_count.toLocaleString()}</p>
                    </div>
                  </div>

                  {/* Summary Text */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Summary</h4>
                    <div className="bg-white border rounded-lg p-4">
                      <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">
                        {linkSummary.summary}
                      </p>
                    </div>
                  </div>

                  {/* Key Points - Only show if we have them */}
                  {linkSummary.key_points && linkSummary.key_points.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Key Points</h4>
                      <ul className="space-y-2">
                        {linkSummary.key_points.map((point, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-blue-600 mr-2">•</span>
                            <span className="text-sm text-gray-900">{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Generated Info */}
                  <div className="text-xs text-gray-500 pt-4 border-t">
                    Summary generated on {formatDate(linkSummary.created_at)}
                    {linkSummary.original_prompt && (
                      <div className="mt-1">
                        <span className="font-medium">Original prompt:</span> {linkSummary.original_prompt}
                      </div>
                    )}
                  </div>

                  {/* Retry Button for Failed Summaries */}
                  {linkSummaryError && (
                    <div className="pt-4">
                      <button
                        onClick={() => selectedLink && handleGetLinkSummary(selectedLink)}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                      >
                        Retry Summary Generation
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  Failed to generate summary. Please try again.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
} 