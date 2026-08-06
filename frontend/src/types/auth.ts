export interface LoginData {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;

  id: number;
  name: string;
  email: string;
  role: string;
}