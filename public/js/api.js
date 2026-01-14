/**
 * Cliente API para comunicación con el backend
 * Maneja autenticación, tokens y peticiones HTTP
 */
class ApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        // Mantener compatibilidad con tokens guardados como "token" en versiones anteriores
        this.token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    }

    /**
     * Guarda el token de autenticación
     */
    setToken(token) {
        this.token = token;
        if (token) {
            // Guardar en ambas claves para compatibilidad con WS y peticiones HTTP
            localStorage.setItem('auth_token', token);
            localStorage.setItem('token', token);
        } else {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('token');
        }
    }

    /**
     * Obtiene el token actual
     */
    getToken() {
        // Usar cualquiera de las dos claves disponibles
        return this.token || localStorage.getItem('auth_token') || localStorage.getItem('token');
    }

    /**
     * Verifica si hay un usuario autenticado
     */
    isAuthenticated() {
        return !!this.getToken();
    }

    /**
     * Realiza una petición HTTP
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Agregar token si existe
        const token = this.getToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `Error ${response.status}`);
            }

            return data;
        } catch (error) {
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // ==================== Métodos de Autenticación ====================

    /**
     * Registra un nuevo usuario
     */
    async register(username, email, password, nombreCompleto = null) {
        const response = await this.post('/api/auth/register', {
            username,
            email,
            password,
            nombre_completo: nombreCompleto
        });

        if (response.success && response.data.token) {
            this.setToken(response.data.token);
        }

        return response;
    }

    /**
     * Inicia sesión
     */
    async login(username, password) {
        const response = await this.post('/api/auth/login', {
            username,
            password
        });

        if (response.success && response.data.token) {
            this.setToken(response.data.token);
        }

        return response;
    }

    /**
     * Cierra sesión
     */
    logout() {
        this.setToken(null);
    }

    /**
     * Obtiene información del usuario actual
     */
    async getCurrentUser() {
        return this.get('/api/auth/me');
    }

    // ==================== Métodos de Cartas ====================

    /**
     * Obtiene todas las cartas
     */
    async getCards(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.get(`/api/cards?${params.toString()}`);
    }

    /**
     * Obtiene una carta por ID
     */
    async getCard(id) {
        return this.get(`/api/cards/${id}`);
    }

    // ==================== Métodos de Usuarios ====================

    /**
     * Obtiene el perfil de un usuario
     */
    async getUserProfile(userId) {
        return this.get(`/api/users/${userId}`);
    }

    /**
     * Actualiza el perfil del usuario actual
     */
    async updateProfile(userId, data) {
        return this.put(`/api/users/${userId}`, data);
    }

    /**
     * Obtiene las estadísticas de un usuario
     */
    async getUserStats(userId) {
        return this.get(`/api/users/${userId}/stats`);
    }

    // ==================== Métodos de Mazos ====================

    /**
     * Lista los mazos del usuario actual
     */
    async getDecks() {
        return this.get('/api/decks');
    }

    /**
     * Obtiene un mazo específico
     */
    async getDeck(deckId) {
        return this.get(`/api/decks/${deckId}`);
    }

    /**
     * Crea un nuevo mazo
     */
    async createDeck(deckData) {
        return this.post('/api/decks', deckData);
    }

    /**
     * Actualiza un mazo
     */
    async updateDeck(deckId, deckData) {
        return this.put(`/api/decks/${deckId}`, deckData);
    }

    /**
     * Elimina un mazo
     */
    async deleteDeck(deckId) {
        return this.delete(`/api/decks/${deckId}`);
    }

    /**
     * Valida un mazo sin guardarlo
     */
    async validateDeck(deckData) {
        return this.post('/api/decks/validate', deckData);
    }

    // ==================== Métodos de Partidas ====================

    /**
     * Crea una nueva partida
     */
    async createGame(mazo1Id, mazo2Id = null, jugador2Id = null) {
        return this.post('/api/games', {
            mazo1_id: mazo1Id,
            mazo2_id: mazo2Id,
            jugador2_id: jugador2Id
        });
    }

    /**
     * Obtiene el estado de una partida
     */
    async getGame(gameId) {
        return this.get(`/api/games/${gameId}`);
    }

    /**
     * Realiza una acción en la partida
     */
    async performGameAction(gameId, accion, datos = {}) {
        return this.post(`/api/games/${gameId}/actions`, {
            accion,
            datos
        });
    }

    /**
     * Finaliza una partida
     */
    async endGame(gameId) {
        return this.post(`/api/games/${gameId}/end`);
    }

    /**
     * Lista las partidas del usuario
     */
    async listGames(filtros = {}) {
        const params = new URLSearchParams(filtros);
        return this.get(`/api/games?${params.toString()}`);
    }

    // ==================== Métodos de Administrador ====================

    /**
     * Lista todos los usuarios (solo administradores)
     */
    async getAllUsers() {
        return this.get('/api/users');
    }

    /**
     * Actualiza un usuario como administrador
     */
    async updateUserAsAdmin(userId, data) {
        return this.put(`/api/users/${userId}/admin`, data);
    }
}

// Crear instancia global
const api = new ApiClient();

