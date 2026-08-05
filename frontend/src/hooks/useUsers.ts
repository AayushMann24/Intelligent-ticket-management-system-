import { useEffect, useState } from "react";

import {
  getUsers,
  type User,
} from "../services/userService";

export default function useUsers() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    async function loadUsers() {
      try {
        const data = await getUsers();
        setUsers(data);
      } catch (err) {
        console.error(err);
      }
    }

    loadUsers();
  }, []);

  return users;
}