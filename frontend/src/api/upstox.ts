import { apiClient } from "./client";

export interface UpstoxStatusResponse {
  authenticated: boolean;
  user_id: string;
  user_name: string;
}

export async function getUpstoxStatus(): Promise<UpstoxStatusResponse> {
  const response = await apiClient.get<UpstoxStatusResponse>(
    "/broker/upstox/status",
  );

  return response.data;
}

export function getUpstoxLoginUrl(): string {
  return `${apiClient.defaults.baseURL}/broker/upstox/login`;
}

export async function logoutUpstox(): Promise<void> {
  await apiClient.post("/broker/upstox/logout");
}
