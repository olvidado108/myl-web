// Estado global
let allCards = [];
let currentEditId = null;
let currentDeleteId = null;
let isAdmin = false;

// Elementos del DOM
const cardsGrid = document.getElementById('cardsGrid');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const filterTipo = document.getElementById('filterTipo');
const filterEdicion = document.getElementById('filterEdicion');
const filterRaza = document.getElementById('filterRaza');
const newCardBtn = document.getElementById('newCardBtn');
const cardModal = document.getElementById('cardModal');
const deleteModal = document.getElementById('deleteModal');
const imageModal = document.getElementById('imageModal');
const cardForm = document.getElementById('cardForm');
const statsBar = document.getElementById('statsBar');
const cardTipo = document.getElementById('cardTipo');
const combatStats = document.getElementById('combatStats');
const modalLargeImage = document.getElementById('modalLargeImage');
const imageModalTitle = document.getElementById('imageModalTitle');

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
    // Verificar si el usuario es administrador
    await checkAdminStatus();
    
    // Ocultar botones de admin si no lo es
    updateAdminButtonsVisibility();
    
    loadCards();
    loadStats();
    setupEventListeners();
    loadEdiciones();
    loadRazas();
});

// Verificar si el usuario es administrador
async function checkAdminStatus() {
    try {
        if (api.isAuthenticated()) {
            const userResponse = await api.getCurrentUser();
            if (userResponse.success && userResponse.data) {
                isAdmin = userResponse.data.isAdmin === true || userResponse.data.isAdmin === 1;
            }
        }
    } catch (error) {
        console.log('No se pudo verificar el estado de administrador:', error);
        isAdmin = false;
    }
}

// Actualizar visibilidad de botones de administrador
function updateAdminButtonsVisibility() {
    const newCardBtn = document.getElementById('newCardBtn');
    if (newCardBtn) {
        newCardBtn.style.display = isAdmin ? 'inline-block' : 'none';
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Búsqueda
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        filterTipo.value = '';
        filterEdicion.value = '';
        filterRaza.value = '';
        // Recargar todas las opciones de filtros
        filterEdicion.innerHTML = '<option value="">Todas las ediciones</option>';
        filterRaza.innerHTML = '<option value="">Todas las razas</option>';
        loadEdiciones();
        loadRazas();
        loadCards();
    });

    // Filtros
    filterTipo.addEventListener('change', () => {
        updateFilterOptions();
        handleSearch();
    });
    filterEdicion.addEventListener('change', () => {
        // Cuando cambia la edición, actualizar solo las razas disponibles
        updateRazasBasedOnFilters();
        handleSearch();
    });
    filterRaza.addEventListener('change', () => {
        // Cuando cambia la raza, actualizar solo las ediciones disponibles
        updateEdicionesBasedOnFilters();
        handleSearch();
    });

    // Modal de carta
    newCardBtn.addEventListener('click', () => openCardModal());
    document.getElementById('closeModal').addEventListener('click', closeCardModal);
    document.getElementById('cancelBtn').addEventListener('click', closeCardModal);
    cardForm.addEventListener('submit', handleSubmitCard);

    // Mostrar/ocultar estadísticas de combate según el tipo
    cardTipo.addEventListener('change', (e) => {
        if (e.target.value === 'Aliado') {
            combatStats.style.display = 'flex';
        } else {
            combatStats.style.display = 'none';
        }
    });

    // Modal de eliminación
    document.getElementById('cancelDeleteBtn').addEventListener('click', closeDeleteModal);
    document.getElementById('confirmDeleteBtn').addEventListener('click', confirmDelete);

    // Cerrar modales al hacer clic fuera
    cardModal.addEventListener('click', (e) => {
        if (e.target === cardModal) closeCardModal();
    });
    deleteModal.addEventListener('click', (e) => {
        if (e.target === deleteModal) closeDeleteModal();
    });
    imageModal.addEventListener('click', (e) => {
        if (e.target === imageModal) closeImageModal();
    });
    
    // Cerrar modal de imagen
    document.getElementById('closeImageModal').addEventListener('click', closeImageModal);
    
    // Cerrar modal de imagen con tecla Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && imageModal.classList.contains('show')) {
            closeImageModal();
        }
    });
}

// Cargar cartas desde la API
async function loadCards() {
    try {
        cardsGrid.innerHTML = '<div class="loading">Cargando cartas...</div>';
        
        const params = new URLSearchParams();
        if (filterEdicion.value) params.append('edicion', filterEdicion.value);
        if (filterRaza.value) params.append('raza', filterRaza.value);
        if (filterTipo.value) params.append('tipo', filterTipo.value);
        if (searchInput.value.trim()) params.append('nombre', searchInput.value.trim());
        params.append('limite', '100'); // Limitar a 100 para mejor rendimiento

        const response = await fetch(`/api/cards?${params.toString()}`);
        const result = await response.json();

        if (result.success) {
            allCards = result.data;
            displayCards(allCards);
        } else {
            showError('Error al cargar las cartas: ' + result.error);
        }
    } catch (error) {
        showError('Error al conectar con el servidor: ' + error.message);
        cardsGrid.innerHTML = '<div class="empty-state"><h3>Error al cargar las cartas</h3><p>Por favor, recarga la página</p></div>';
    }
}

// Cargar estadísticas
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const result = await response.json();

        if (result.success) {
            const stats = result.data;
            statsBar.innerHTML = `
                <strong>Total:</strong> ${stats.total} cartas | 
                <strong>Por tipo:</strong> ${Object.entries(stats.porTipo).map(([k, v]) => `${k}: ${v}`).join(', ')}
            `;
        }
    } catch (error) {
        statsBar.innerHTML = '<span>No se pudieron cargar las estadísticas</span>';
    }
}

// Cargar ediciones únicas para el filtro
async function loadEdiciones() {
    try {
        const response = await fetch('/api/cards');
        const result = await response.json();

        if (result.success) {
            const ediciones = [...new Set(result.data.map(c => c.edicion).filter(Boolean))].sort();
            ediciones.forEach(edicion => {
                const option = document.createElement('option');
                option.value = edicion;
                option.textContent = edicion;
                filterEdicion.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar ediciones:', error);
    }
}

// Cargar razas únicas para el filtro
async function loadRazas() {
    try {
        const response = await fetch('/api/cards');
        const result = await response.json();

        if (result.success) {
            const razas = [...new Set(result.data.map(c => c.raza).filter(Boolean))].sort();
            razas.forEach(raza => {
                const option = document.createElement('option');
                option.value = raza;
                option.textContent = raza;
                filterRaza.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar razas:', error);
    }
}

// Actualizar opciones de filtros basándose en los filtros activos (para cuando cambia el tipo)
async function updateFilterOptions() {
    await updateRazasBasedOnFilters();
    await updateEdicionesBasedOnFilters();
}

// Actualizar razas disponibles basándose en edición y tipo (sin considerar raza)
async function updateRazasBasedOnFilters() {
    try {
        const params = new URLSearchParams();
        if (filterEdicion.value) params.append('edicion', filterEdicion.value);
        if (filterTipo.value) params.append('tipo', filterTipo.value);
        
        const response = await fetch(`/api/cards?${params.toString()}`);
        const result = await response.json();

        if (result.success) {
            const cartasFiltradas = result.data;
            const razasDisponibles = [...new Set(cartasFiltradas.map(c => c.raza).filter(Boolean))].sort();
            const razaActual = filterRaza.value;
            
            // Limpiar y repoblar el select de razas
            filterRaza.innerHTML = '<option value="">Todas las razas</option>';
            razasDisponibles.forEach(raza => {
                const option = document.createElement('option');
                option.value = raza;
                option.textContent = raza;
                filterRaza.appendChild(option);
            });
            
            // Si la raza actual no está disponible, limpiarla
            if (razaActual && !razasDisponibles.includes(razaActual)) {
                filterRaza.value = '';
            } else if (razaActual && razasDisponibles.includes(razaActual)) {
                filterRaza.value = razaActual;
            }
        }
    } catch (error) {
        console.error('Error al actualizar razas:', error);
    }
}

// Actualizar ediciones disponibles basándose en raza y tipo (sin considerar edición)
async function updateEdicionesBasedOnFilters() {
    try {
        const params = new URLSearchParams();
        if (filterRaza.value) params.append('raza', filterRaza.value);
        if (filterTipo.value) params.append('tipo', filterTipo.value);
        
        const response = await fetch(`/api/cards?${params.toString()}`);
        const result = await response.json();
        
        if (result.success) {
            const cartasFiltradas = result.data;
            const edicionesDisponibles = [...new Set(cartasFiltradas.map(c => c.edicion).filter(Boolean))].sort();
            const edicionActual = filterEdicion.value;
            
            // Limpiar y repoblar el select de ediciones
            filterEdicion.innerHTML = '<option value="">Todas las ediciones</option>';
            edicionesDisponibles.forEach(edicion => {
                const option = document.createElement('option');
                option.value = edicion;
                option.textContent = edicion;
                filterEdicion.appendChild(option);
            });
            
            // Si la edición actual no está disponible, limpiarla
            if (edicionActual && !edicionesDisponibles.includes(edicionActual)) {
                filterEdicion.value = '';
            } else if (edicionActual && edicionesDisponibles.includes(edicionActual)) {
                filterEdicion.value = edicionActual;
            }
        }
    } catch (error) {
        console.error('Error al actualizar ediciones:', error);
    }
}

// Mostrar cartas en el grid
function displayCards(cards) {
    if (cards.length === 0) {
        cardsGrid.innerHTML = '<div class="empty-state"><h3>No se encontraron cartas</h3><p>Intenta ajustar los filtros de búsqueda</p></div>';
        return;
    }

    cardsGrid.innerHTML = cards.map(card => createCardHTML(card)).join('');
    
    // Agregar event listeners a las imágenes clickeables
    const clickableImages = cardsGrid.querySelectorAll('.card-image-clickable');
    clickableImages.forEach(img => {
        img.addEventListener('click', () => {
            const imageUrl = img.getAttribute('data-image-url');
            const cardName = img.getAttribute('data-card-name');
            openImageModal(imageUrl, cardName);
        });
    });
}

// Crear HTML para una carta
function createCardHTML(card) {
    const tipoClass = card.tipo || 'desconocido';
    // Compatibilidad: obtener fuerza de card.fuerza, o de card.ataque/defensa
    const fuerza = card.fuerza !== undefined && card.fuerza !== null
        ? card.fuerza
        : (card.ataque || card.defensa || 0);
    
    const statsHTML = card.tipo === 'Aliado' && fuerza ? `
        <div class="card-stats">
            <div class="stat-item">
                <span class="stat-label">Fuerza</span>
                <span class="stat-value">${fuerza}</span>
            </div>
        </div>
    ` : '';

    // Imagen de la carta
    const imagenHTML = card.imagenUrl ? `
        <div class="card-image-container">
            <img src="${escapeHtml(card.imagenUrl)}" alt="${escapeHtml(card.nombre || 'Carta')}" 
                 class="card-image card-image-clickable" 
                 data-image-url="${escapeHtml(card.imagenUrl)}"
                 data-card-name="${escapeHtml(card.nombre || 'Carta')}"
                 onerror="this.style.display='none'" 
                 style="cursor: pointer;" />
        </div>
    ` : '';

    return `
        <div class="card-item">
            ${imagenHTML}
            <div class="card-header">
                <div>
                    <div class="card-title">${escapeHtml(card.nombre || 'Sin nombre')}</div>
                    <span class="card-type ${tipoClass}">${escapeHtml(card.tipo || 'Desconocido')}</span>
                </div>
            </div>
            ${statsHTML}
            <div class="card-info">
                ${card.coste !== undefined ? `<div class="card-info-item"><strong>Coste:</strong> ${card.coste}</div>` : ''}
                ${card.raza ? `<div class="card-info-item"><strong>Raza:</strong> ${escapeHtml(card.raza)}</div>` : ''}
                ${card.edicion ? `<div class="card-info-item"><strong>Edición:</strong> ${escapeHtml(card.edicion)}</div>` : ''}
                ${card.kit ? `<div class="card-info-item"><strong>Expansión:</strong> ${escapeHtml(card.kit.replace(/_/g, ' ').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()))}</div>` : ''}
                ${card.rareza ? `<div class="card-info-item"><strong>Rareza:</strong> ${escapeHtml(card.rareza)}</div>` : ''}
                ${card.esUnica ? `<div class="card-info-item"><strong>⚡ Única</strong></div>` : ''}
            </div>
            ${card.textoHabilidad && card.textoHabilidad !== 'NaN' && card.textoHabilidad.trim() !== '' ? `<div class="card-ability">${escapeHtml(card.textoHabilidad)}</div>` : ''}
            ${isAdmin ? `
            <div class="card-actions">
                <button class="btn btn-edit" onclick="editCard('${card.id}')">✏️ Editar</button>
                <button class="btn btn-delete" onclick="deleteCardPrompt('${card.id}', '${escapeHtml(card.nombre)}')">🗑️ Eliminar</button>
            </div>
            ` : ''}
        </div>
    `;
}

// Manejar búsqueda
function handleSearch() {
    loadCards();
}

// Abrir modal para nueva carta
function openCardModal(card = null) {
    currentEditId = card ? card.id : null;
    document.getElementById('modalTitle').textContent = card ? 'Editar Carta' : 'Nueva Carta';
    cardForm.reset();
    
    if (card) {
        // Llenar formulario con datos de la carta
        // Compatibilidad: obtener fuerza de card.fuerza, o de card.ataque/defensa
        const fuerza = card.fuerza !== undefined && card.fuerza !== null
            ? card.fuerza
            : (card.ataque || card.defensa || 0);
        
        document.getElementById('cardId').value = card.id;
        document.getElementById('cardNombre').value = card.nombre || '';
        document.getElementById('cardTipo').value = card.tipo || '';
        document.getElementById('cardCoste').value = card.coste || 0;
        document.getElementById('cardFuerza').value = fuerza;
        document.getElementById('cardRaza').value = card.raza || '';
        document.getElementById('cardEdicion').value = card.edicion || '';
        document.getElementById('cardRareza').value = card.rareza || '';
        document.getElementById('cardTextoHabilidad').value = card.textoHabilidad || '';
        document.getElementById('cardImagen').value = card.imagen || '';
        document.getElementById('cardEsUnica').checked = card.esUnica || false;
        
        // Mostrar estadísticas de combate si es Aliado
        if (card.tipo === 'Aliado') {
            combatStats.style.display = 'flex';
        } else {
            combatStats.style.display = 'none';
        }
    } else {
        // Nueva carta - generar ID único
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 1000);
        document.getElementById('cardId').value = `carta_${timestamp}_${random}`;
        combatStats.style.display = 'none';
    }
    
    cardModal.classList.add('show');
}

// Cerrar modal de carta
function closeCardModal() {
    cardModal.classList.remove('show');
    currentEditId = null;
    cardForm.reset();
}

// Manejar envío del formulario
async function handleSubmitCard(e) {
    e.preventDefault();
    
    const cardData = {
        id: document.getElementById('cardId').value,
        nombre: document.getElementById('cardNombre').value.trim(),
        tipo: document.getElementById('cardTipo').value,
        coste: parseInt(document.getElementById('cardCoste').value) || 0,
        textoHabilidad: document.getElementById('cardTextoHabilidad').value.trim(),
        imagen: document.getElementById('cardImagen').value.trim(),
        esUnica: document.getElementById('cardEsUnica').checked
    };
    
    // Agregar campos opcionales
    const raza = document.getElementById('cardRaza').value.trim();
    if (raza) cardData.raza = raza;
    
    const edicion = document.getElementById('cardEdicion').value.trim();
    if (edicion) cardData.edicion = edicion;
    
    const rareza = document.getElementById('cardRareza').value;
    if (rareza) cardData.rareza = rareza;
    
    // Agregar estadísticas de combate si es Aliado
    if (cardData.tipo === 'Aliado') {
        cardData.fuerza = parseInt(document.getElementById('cardFuerza').value) || 0;
    }
    
    try {
        const url = currentEditId ? `/api/cards/${currentEditId}` : '/api/cards';
        const method = currentEditId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cardData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess(currentEditId ? 'Carta actualizada correctamente' : 'Carta creada correctamente');
            closeCardModal();
            loadCards();
            loadStats();
        } else {
            showError('Error: ' + result.error);
        }
    } catch (error) {
        showError('Error al guardar la carta: ' + error.message);
    }
}

// Editar carta
function editCard(id) {
    const card = allCards.find(c => c.id === id);
    if (card) {
        openCardModal(card);
    }
}

// Mostrar prompt de eliminación
function deleteCardPrompt(id, nombre) {
    currentDeleteId = id;
    document.getElementById('deleteCardName').textContent = nombre;
    deleteModal.classList.add('show');
}

// Cerrar modal de eliminación
function closeDeleteModal() {
    deleteModal.classList.remove('show');
    currentDeleteId = null;
}

// Confirmar eliminación
async function confirmDelete() {
    if (!currentDeleteId) return;
    
    try {
        const response = await fetch(`/api/cards/${currentDeleteId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Carta eliminada correctamente');
            closeDeleteModal();
            loadCards();
            loadStats();
        } else {
            showError('Error: ' + result.error);
        }
    } catch (error) {
        showError('Error al eliminar la carta: ' + error.message);
    }
}

// Abrir modal de imagen grande
function openImageModal(imageUrl, cardName) {
    modalLargeImage.src = imageUrl;
    imageModalTitle.textContent = cardName || 'Imagen de Carta';
    imageModal.classList.add('show');
}

// Cerrar modal de imagen
function closeImageModal() {
    imageModal.classList.remove('show');
    modalLargeImage.src = '';
}

// Utilidades
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccess(message) {
    // Crear notificación temporal
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 2000;
        animation: slideIn 0.3s;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showError(message) {
    // Crear notificación temporal
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 2000;
        animation: slideIn 0.3s;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Agregar estilos de animación para notificaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);





