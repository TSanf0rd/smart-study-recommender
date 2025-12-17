import api from "./client";

export const generateRecommendations = async (payload) => {
  const res = await api.post(
    "/api/cqrs/recommendations/generate",
    payload
  );
  return res.data;
};

const res = await generateRecommendations({
    user_id: userId,
    limit: 10,
  });
  setRecommendations(res.data.recommendations);