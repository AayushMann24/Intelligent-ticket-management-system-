import { useState } from "react";

import MainLayout from "../layouts/MainLayout";

import useUsers from "../hooks/useUsers";

import UserToolbar from "../components/users/UserToolbar";
import UserTable from "../components/users/UserTable";
import UserRoleModal from "../components/users/UserRoleModal";
import UserDetailsModal from "../components/users/UserDetailsModal";

import type { User } from "../types/user";

export default function UsersPage() {
  const {
    users,
    loading,

    search,
    setSearch,

    role,
    setRole,

    changeRole,
  } = useUsers();

  const [selectedUser, setSelectedUser] =
    useState<User | null>(null);

  const [isViewOpen, setIsViewOpen] =
    useState(false);

  const [isRoleOpen, setIsRoleOpen] =
    useState(false);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center">
          <h2 className="text-xl text-white">
            Loading Users...
          </h2>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>

      <h1 className="mb-8 text-3xl font-bold text-white">
        Users
      </h1>

      <UserToolbar
        search={search}
        setSearch={setSearch}
        role={role}
        setRole={setRole}
      />

      <UserTable
        users={users}
        onView={(user) => {
          setSelectedUser(user);
          setIsViewOpen(true);
        }}
        onEdit={(user) => {
          setSelectedUser(user);
          setIsRoleOpen(true);
        }}
      />

      <UserDetailsModal
        open={isViewOpen}
        user={selectedUser}
        onClose={() => setIsViewOpen(false)}
      />

      <UserRoleModal
        open={isRoleOpen}
        user={selectedUser}
        onClose={() => setIsRoleOpen(false)}
        onSave={async (newRole) => {
          if (!selectedUser) return;

          await changeRole(selectedUser.id, {
            role: newRole,
          });

          setIsRoleOpen(false);
        }}
      />

    </MainLayout>
  );
}