import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; // FastAPI backend currently runs on this port locally

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const createUser = async (userData) => {
  const response = await api.post('/users', userData);
  return response.data;
};

export const listUserCategories = async (userId) => {
  const response = await api.get(`/users/${userId}/list-categories`);
  return response.data;
};

export const initializeCategories = async (userId) => {
  const response = await api.post(`/users/${userId}/initialize-categories`);
  return response.data;
};

export const addNewCategory = async (userId, customCategory) => {
  const response = await api.post(`/users/${userId}/add-new-category`, customCategory);
  return response.data;
};

export const addProduct = async (userId, productData) => {
  const response = await api.post(`/users/${userId}/products`, productData);
  return response.data;
};

export const scrapeAndAddProduct = async (userId, scrapeData) => {
  const response = await api.post(`/users/${userId}/products/scrape`, scrapeData);
  return response.data;
};

export const getUserProducts = async (userId) => {
  const response = await api.get(`/users/${userId}/products`);
  return response.data;
};

export const updateProduct = async (productId, updateData) => {
  const response = await api.put(`/products/${productId}`, updateData);
  return response.data;
};

export const deleteProduct = async (productId) => {
  const response = await api.delete(`/products/${productId}`);
  return response.data;
};

export const getSupportedPlatforms = async () => {
  const response = await api.get('/supported-platforms');
  return response.data;
};

export const getProductPriceHistory = async (productId) => {
  const response = await api.get(`/products/${productId}/price-history`);
  return response.data;
};


export default api;
