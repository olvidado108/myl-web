// Estado global
let allCards = [];
let currentEditId = null;

// Elementos del DOM
const cardsGrid = document.getElementById('cardsGrid');
const statsBar = document.getElementById('statsBar');
const statsText = document.getElementById('statsText');
const counterNumber = document.getElementById('counterNumber');

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    loadMissingAbilities();
});

// Cargar cartas sin habilidad
async function loadMissingAbilities() {
    try {
        cardsGrid.innerHTML = '<div class="loading">Cargando cartas sin habilidad...</div>';
        
        const response = await fetch('/api/cards/missing-abilities');
        const result = await response.json();

        if (result.success) {
            allCards = result.data;
            displayCards(allCards);
            updateStats(allCards.length);
        } else {
            showError('Error al cargar las cartas: ' + result.error);
            cardsGrid.innerHTML = '<div class="empty-state"><h3>Error al cargar las cartas</h3><p>Por favor, recarga la página</p></div>';
        }
    } catch (error) {
        showError('Error al conectar con el servidor: ' + error.message);
        cardsGrid.innerHTML = '<div class="empty-state"><h3>Error al cargar las cartas</h3><p>Por favor, recarga la página</p></div>';
    }
}

// Actualizar estadísticas
function updateStats(count) {
    statsText.textContent = `Total de cartas sin habilidad: ${count}`;
    // Actualizar contador destacado
    if (counterNumber) {
        counterNumber.textContent = count;
    }
}

// Mostrar cartas en el grid
function displayCards(cards) {
    if (cards.length === 0) {
        cardsGrid.innerHTML = '<div class="empty-state"><h3>¡Excelente! 🎉</h3><p>Todas las cartas tienen habilidad completada</p></div>';
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
    
    // Agregar event listeners a los botones de guardar
    const saveButtons = cardsGrid.querySelectorAll('.btn-save-ability');
    saveButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const cardId = btn.getAttribute('data-card-id');
            const card = allCards.find(c => c.id === cardId);
            if (card) {
                saveAbility(card);
            }
        });
    });
}

// Crear HTML para una carta
function createCardHTML(card) {
    const tipoClass = card.tipo || 'desconocido';
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
        <div class="card-item quick-edit-card">
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
            </div>
            <div class="quick-edit-form">
                <label for="ability-${card.id}" style="display: block; margin-bottom: 8px; font-weight: 600; color: #495057;">
                    Texto de Habilidad:
                </label>
                <textarea 
                    id="ability-${card.id}" 
                    placeholder="Escribe la habilidad de la carta aquí..."
                    data-card-id="${card.id}">${escapeHtml(card.textoHabilidad || '')}</textarea>
                <div class="quick-edit-actions">
                    <button class="btn-save-ability" data-card-id="${card.id}">💾 Guardar Habilidad</button>
                </div>
            </div>
        </div>
    `;
}

// Guardar habilidad
async function saveAbility(card) {
    const textarea = document.getElementById(`ability-${card.id}`);
    const nuevaHabilidad = textarea.value.trim();
    
    if (!nuevaHabilidad) {
        showError('Por favor, ingresa una habilidad');
        return;
    }
    
    try {
        // Actualizar la carta con la nueva habilidad
        const cartaActualizada = {
            ...card,
            textoHabilidad: nuevaHabilidad
        };
        
        const response = await fetch(`/api/cards/${card.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cartaActualizada)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Habilidad guardada correctamente');
            // Remover la carta de la lista
            allCards = allCards.filter(c => c.id !== card.id);
            displayCards(allCards);
            updateStats(allCards.length);
        } else {
            showError('Error al guardar: ' + result.error);
        }
    } catch (error) {
        showError('Error al guardar la habilidad: ' + error.message);
    }
}

// Abrir modal de imagen grande con formulario de edición
function openImageModal(imageUrl, cardName) {
    // Buscar la carta correspondiente
    const card = allCards.find(c => c.nombre === cardName);
    if (!card) {
        // Si no encontramos la carta, mostrar solo la imagen
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content modal-image">
                <div class="modal-header">
                    <h2>${escapeHtml(cardName || 'Imagen de Carta')}</h2>
                    <span class="close" onclick="this.closest('.modal').remove()">&times;</span>
                </div>
                <div class="modal-image-body">
                    <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(cardName || 'Carta')}" />
                </div>
            </div>
        `;
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        document.body.appendChild(modal);
        return;
    }
    
    // Crear modal con imagen y formulario
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content modal-image-with-form">
            <div class="modal-image-section">
                <div style="width: 100%; margin-bottom: 20px; position: relative; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; color: white;">
                    <h2 style="margin: 0; font-size: 1.3em;">${escapeHtml(card.nombre || 'Imagen de Carta')}</h2>
                    <span class="close" onclick="this.closest('.modal').remove()" style="position: absolute; top: 10px; right: 15px; cursor: pointer; font-size: 1.8em;">&times;</span>
                </div>
                <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(card.nombre || 'Carta')}" />
            </div>
            <div class="modal-form-section">
                <h3>Editar Habilidad</h3>
                <div class="card-info-modal">
                    <div class="card-info-modal-item"><strong>Nombre:</strong> ${escapeHtml(card.nombre || 'Sin nombre')}</div>
                    <div class="card-info-modal-item"><strong>Tipo:</strong> ${escapeHtml(card.tipo || 'Desconocido')}</div>
                    ${card.coste !== undefined ? `<div class="card-info-modal-item"><strong>Coste:</strong> ${card.coste}</div>` : ''}
                    ${card.raza ? `<div class="card-info-modal-item"><strong>Raza:</strong> ${escapeHtml(card.raza)}</div>` : ''}
                    ${card.edicion ? `<div class="card-info-modal-item"><strong>Edición:</strong> ${escapeHtml(card.edicion)}</div>` : ''}
                </div>
                <label for="modal-ability-${card.id}">Texto de Habilidad:</label>
                <textarea 
                    id="modal-ability-${card.id}" 
                    placeholder="Escribe la habilidad de la carta aquí..."
                    data-card-id="${card.id}">${escapeHtml(card.textoHabilidad || '')}</textarea>
                <div class="modal-form-actions">
                    <button class="btn-save-ability" onclick="saveAbilityFromModal('${card.id}')" style="flex: 1;">
                        💾 Guardar Habilidad
                    </button>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()" style="flex: 0; padding: 8px 20px;">
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    // Cerrar con Escape
    const closeOnEscape = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', closeOnEscape);
        }
    };
    document.addEventListener('keydown', closeOnEscape);
    
    document.body.appendChild(modal);
    
    // Enfocar el textarea
    setTimeout(() => {
        const textarea = document.getElementById(`modal-ability-${card.id}`);
        if (textarea) {
            textarea.focus();
        }
    }, 100);
}

// Guardar habilidad desde el modal
async function saveAbilityFromModal(cardId) {
    const card = allCards.find(c => c.id === cardId);
    if (!card) return;
    
    const textarea = document.getElementById(`modal-ability-${cardId}`);
    if (!textarea) return;
    
    const nuevaHabilidad = textarea.value.trim();
    
    if (!nuevaHabilidad) {
        showError('Por favor, ingresa una habilidad');
        return;
    }
    
    try {
        // Actualizar la carta con la nueva habilidad
        const cartaActualizada = {
            ...card,
            textoHabilidad: nuevaHabilidad
        };
        
        const response = await fetch(`/api/cards/${card.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cartaActualizada)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Habilidad guardada correctamente');
            // Cerrar el modal
            const modal = document.querySelector('.modal.show');
            if (modal) {
                modal.remove();
            }
            // Remover la carta de la lista
            allCards = allCards.filter(c => c.id !== card.id);
            displayCards(allCards);
            updateStats(allCards.length);
        } else {
            showError('Error al guardar: ' + result.error);
        }
    } catch (error) {
        showError('Error al guardar la habilidad: ' + error.message);
    }
}

// Hacer la función global para que pueda ser llamada desde onclick
window.saveAbilityFromModal = saveAbilityFromModal;

// Utilidades
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccess(message) {
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

// Agregar estilos de animación
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

