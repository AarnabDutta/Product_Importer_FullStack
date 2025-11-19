// Axios instance & API calls
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const productAPI = {
  getProducts: (params) => api.get('/api/products', { params }),
  getProduct: (id) => api.get(`/api/products/${id}`),
  createProduct: (data) => api.post('/api/products', data),
  updateProduct: (id, data) => api.put(`/api/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/api/products/${id}`),
  deleteAllProducts: () => api.delete('/api/products'),
};

export const uploadAPI = {
  uploadCSV: (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },
};

export const webhookAPI = {
  getWebhooks: () => api.get('/api/webhooks'),
  getWebhook: (id) => api.get(`/api/webhooks/${id}`),
  createWebhook: (data) => api.post('/api/webhooks', data),
  updateWebhook: (id, data) => api.put(`/api/webhooks/${id}`, data),
  deleteWebhook: (id) => api.delete(`/api/webhooks/${id}`),
  testWebhook: (id) => api.post(`/api/webhooks/${id}/test`),
};

export default api;
