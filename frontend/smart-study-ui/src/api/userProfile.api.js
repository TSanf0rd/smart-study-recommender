import api from "./client"

export const getUserProfile = async (userId) => {
    const res = await api.get(`/api/cqrs/users/${userId}`);
    return res.data;
  };
  