import api from "./client";

export const getResourceDetails = async (resourceId) => {
    const res = await api.get(`/api/cqrs/resources/${resourceId}`);
    return res.data;
  };


export const getResourcesByUploader = async (userId) => {
  const res = await api.get(
    `/api/cqrs/resources/by-uploader/${userId}`
  );
  return res.data;
};


export const uploadResource = async (formData) => {
  const res = await api.post(
    "/api/cqrs/resources/upload",
    formData,
  );
  return res.data;
};


export const logResourceView = async (resourceId, payload) => {
  const res = await api.post(
    `/api/cqrs/resources/${resourceId}/view`,
    payload
  );
  return res.data;
};


export const rateResource = async (resourceId, payload) => {
    const res = await api.post(
      `/api/cqrs/resources/${resourceId}/rate`,
      payload
    );
    return res.data;
  };