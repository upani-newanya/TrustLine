import apiFetch from './api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface CurrentUser {
  id: number;
  full_name: string;
  email: string;
  phone_number: string | null;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
}

export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
}

export function getStoredRole(): 'user' | 'admin' | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('user_role') as 'user' | 'admin' | null;
}

export function getCurrentUserRole(): 'user' | 'admin' | null {
  return getStoredRole();
}

export function isAdmin(): boolean {
  return getStoredRole() === 'admin';
}

export function isUser(): boolean {
  return getStoredRole() === 'user';
}

export async function login(email: string, password: string): Promise<{ success: boolean; message: string; role?: string }> {
  try {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });

    if (!res.ok) {
      const errText = await res.text();
      let msg = 'Invalid email or password';
      try {
        const parsed = JSON.parse(errText);
        if (typeof parsed.detail === 'string') {
          msg = parsed.detail;
        } else if (Array.isArray(parsed.detail)) {
          msg = parsed.detail.map((e: any) => e.msg ?? JSON.stringify(e)).join('; ');
        }
      } catch {}
      return { success: false, message: msg };
    }

    const data = await res.json();
    localStorage.setItem('access_token', data.access_token);

    // Fetch user profile to get role
    const user = await fetchCurrentUser();
    if (user) {
      localStorage.setItem('user_role', user.role);
      return { success: true, message: 'Login successful', role: user.role };
    }

    return { success: true, message: 'Login successful' };
  } catch (err: any) {
    return { success: false, message: err.message || 'Login failed' };
  }
}

export async function register(data: {
  full_name: string;
  email: string;
  password: string;
  phone_number?: string | null;
}): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const errText = await res.text();
      let msg = 'Registration failed';
      try {
        const parsed = JSON.parse(errText);
        if (typeof parsed.detail === 'string') {
          msg = parsed.detail;
        } else if (Array.isArray(parsed.detail)) {
          msg = parsed.detail.map((e: any) => e.msg ?? JSON.stringify(e)).join('; ');
        }
      } catch {}
      return { success: false, message: msg };
    }

    const result = await res.json();
    localStorage.setItem('access_token', result.access_token);

    // Fetch user profile
    const user = await fetchCurrentUser();
    if (user) {
      localStorage.setItem('user_role', user.role);
    }

    return { success: true, message: 'Account created successfully' };
  } catch (err: any) {
    return { success: false, message: err.message || 'Registration failed' };
  }
}

export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  try {
    const user = await apiFetch<CurrentUser>('/users/me');
    return user;
  } catch {
    return null;
  }
}

export function logout() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');
}
