import { useEffect, useState } from "react";

import {
  getUsers,
  updateUserRole,
} from "../services/userService";

import type {
  User,
  UpdateRoleRequest,
} from "../types/user";

export default function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");

  // ======================================
  // Load Users
  // ======================================
  const loadUsers = async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (error) {
      console.error("Failed to load users:", error);
    } finally {
      setLoading(false);
    }
  };

  // ======================================
  // Update User Role
  // ======================================
  const changeRole = async (
    userId: number,
    roleData: UpdateRoleRequest
  ) => {
    try {
      await updateUserRole(userId, roleData);
      await loadUsers();
    } catch (error) {
      console.error("Failed to update role:", error);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  // ======================================
  // Search & Filter
  // ======================================
  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.name.toLowerCase().includes(search.toLowerCase()) ||
      user.email.toLowerCase().includes(search.toLowerCase());

    const matchesRole =
      role === "" || user.role === role;

    return matchesSearch && matchesRole;
  });

  return {
    users: filteredUsers,
    loading,

    reloadUsers: loadUsers,

    changeRole,

    search,
    setSearch,

    role,
    setRole,
  };
}
