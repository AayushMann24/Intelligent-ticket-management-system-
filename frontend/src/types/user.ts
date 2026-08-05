export interface User {
  id: number;

  name: string;
  email: string;

  role: string;

  created_at?: string;
}

export interface UpdateRoleRequest {
  role: string;
}