"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface User {
  id: string;
  username?: string;
  email?: string;
  avatar_url?: string;
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
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

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    router.push("/login");
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
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to pukr</h1>
        {user && (
          <div className="mb-6">
            <p className="text-lg mb-2">Hello, {user.username || user.email}!</p>
            {user.avatar_url && (
              <img 
                src={user.avatar_url} 
                alt="Avatar" 
                className="w-16 h-16 rounded-full mx-auto"
              />
            )}
          </div>
        )}
        <p className="text-lg">This is the home page of the pukr app. Explore features and enjoy your stay!</p>
      </div>
      <button
        onClick={handleLogout}
        className="mt-8 bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      >
        Logout
      </button>
    </main>
  );
}
