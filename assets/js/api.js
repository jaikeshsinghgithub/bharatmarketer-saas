// api.js - Handles all frontend-to-backend communication
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api/v1'
    : 'https://bharatmarketer-api.onrender.com/api/v1';

class ApiClient {
    static getToken() {
        return localStorage.getItem('bm_token');
    }

    static setToken(token) {
        localStorage.setItem('bm_token', token);
    }

    static removeToken() {
        localStorage.removeItem('bm_token');
    }

    static isAuthenticated() {
        return !!this.getToken();
    }

    static async register(userData) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Registration failed');
            }

            return data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    static async login(email, password) {
        try {
            // OAuth2 expects form data
            const formData = new URLSearchParams();
            formData.append('username', email); // OAuth2 spec uses 'username'
            formData.append('password', password);

            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            // Save token
            if (data.access_token) {
                this.setToken(data.access_token);
            }

            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    static async getProfile() {
        const token = this.getToken();
        if (!token) throw new Error('No token found');

        try {
            const response = await fetch(`${API_BASE_URL}/auth/test-token`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch profile');
            }

            return data;
        } catch (error) {
            if (error.message.includes('token') || error.message.includes('auth')) {
                this.removeToken();
            }
            throw error;
        }
    }
}

window.ApiClient = ApiClient;
