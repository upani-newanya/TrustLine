const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function apiFetch<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  if (typeof window === "undefined") throw new Error("apiFetch is client-only");

  const token = localStorage.getItem("access_token");
  const headers: Record<string, string> = {};

  // Copy existing headers
  if (options.headers) {
    const h = options.headers as Record<string, string>;
    Object.keys(h).forEach((k) => {
      headers[k] = h[k];
    });
  }

  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }

  // Handle 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json();
}

export default apiFetch;
