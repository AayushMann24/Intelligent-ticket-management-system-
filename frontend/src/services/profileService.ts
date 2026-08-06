import axios from "axios";

const API = "http://127.0.0.1:8000";

const authHeaders = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  },
});

export interface Profile {
  id: number;
  name: string;
  email: string;
  role: string;
}

export async function getProfile(): Promise<Profile> {
  const response = await axios.get<Profile>(
    `${API}/users/me`,
    authHeaders()
  );

  return response.data;
}