import { useEffect, useState } from "react";

import {
  getProfile,
  type Profile,
} from "../services/profileService";

export default function useProfile() {
  const [user, setUser] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await getProfile();
        setUser(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  return {
    user,
    loading,
  };
}