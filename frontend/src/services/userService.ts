import axios from "axios";

const API = "http://127.0.0.1:8000";

const getToken = () => localStorage.getItem("token");

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

export async function getUsers(): Promise<User[]> {
  const response = await axios.get(
    `${API}/users`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    }
  );

  return response.data;
}