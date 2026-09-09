/**
 * Authentication service for Legal Metrology Portal.
 * Connects frontend to backend /api/auth endpoints.
 */

export async function loginUser(username, password) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Authentication failed. Please check your credentials.");
  }

  return await response.json();
}
