import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// API functions
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/auth/login/', { username, password }),
  register: (data: any) => api.post('/auth/register/', data),
  getCurrentUser: () => api.get('/auth/me/'),
};

export const projectsAPI = {
  getAll: (params?: any) => api.get('/projects/', { params }),
  getOne: (id: number) => api.get(`/projects/${id}/`),
  create: (data: any) => api.post('/projects/', data),
  update: (id: number, data: any) => api.patch(`/projects/${id}/`, data),
  delete: (id: number) => api.delete(`/projects/${id}/`),
  getEpics: (id: number) => api.get(`/projects/${id}/epics/`),
};

export const epicsAPI = {
  getAll: (params?: any) => api.get('/epics/', { params }),
  getOne: (id: number) => api.get(`/epics/${id}/`),
  create: (data: any) => api.post('/epics/', data),
  update: (id: number, data: any) => api.patch(`/epics/${id}/`, data),
  delete: (id: number) => api.delete(`/epics/${id}/`),
  getStories: (id: number) => api.get(`/epics/${id}/stories/`),
};

export const storiesAPI = {
  getAll: (params?: any) => api.get('/stories/', { params }),
  getOne: (id: number) => api.get(`/stories/${id}/`),
  create: (data: any) => api.post('/stories/', data),
  update: (id: number, data: any) => api.patch(`/stories/${id}/`, data),
  delete: (id: number) => api.delete(`/stories/${id}/`),
  getTestCases: (id: number) => api.get(`/stories/${id}/testcases/`),
};

export const testCasesAPI = {
  getAll: (params?: any) => api.get('/testcases/', { params }),
  getOne: (id: number) => api.get(`/testcases/${id}/`),
  create: (data: any) => api.post('/testcases/', data),
  update: (id: number, data: any) => api.patch(`/testcases/${id}/`, data),
  delete: (id: number) => api.delete(`/testcases/${id}/`),
  execute: (id: number, executionStatus: string) =>
    api.post(`/testcases/${id}/execute/`, { execution_status: executionStatus }),
};

export const testSuitesAPI = {
  getAll: (params?: any) => api.get('/test-suites/', { params }),
  getOne: (id: number) => api.get(`/test-suites/${id}/`),
  create: (data: any) => api.post('/test-suites/', data),
  update: (id: number, data: any) => api.patch(`/test-suites/${id}/`, data),
  delete: (id: number) => api.delete(`/test-suites/${id}/`),
  createTestRun: (id: number, data: any) =>
    api.post(`/test-suites/${id}/create_test_run/`, data),
};

export const testRunsAPI = {
  getAll: (params?: any) => api.get('/test-runs/', { params }),
  getOne: (id: number) => api.get(`/test-runs/${id}/`),
  create: (data: any) => api.post('/test-runs/', data),
  update: (id: number, data: any) => api.patch(`/test-runs/${id}/`, data),
  delete: (id: number) => api.delete(`/test-runs/${id}/`),
  getExecutions: (id: number) => api.get(`/test-runs/${id}/executions/`),
  getSummary: (id: number) => api.get(`/test-runs/${id}/summary/`),
};

export const testExecutionsAPI = {
  getAll: (params?: any) => api.get('/test-executions/', { params }),
  getOne: (id: number) => api.get(`/test-executions/${id}/`),
  create: (data: any) => api.post('/test-executions/', data),
  update: (id: number, data: any) => api.patch(`/test-executions/${id}/`, data),
  recordResult: (id: number, data: any) =>
    api.post(`/test-executions/${id}/record_result/`, data),
};

export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats/'),
};

export const helpersAPI = {
  getEpicsByProject: (projectId: number) =>
    api.get('/helpers/epics-by-project/', { params: { project_id: projectId } }),
  getStoriesByEpic: (epicId: number) =>
    api.get('/helpers/stories-by-epic/', { params: { epic_id: epicId } }),
  getUsers: () => api.get('/helpers/users/'),
};
