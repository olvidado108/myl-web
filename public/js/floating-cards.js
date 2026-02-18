/**
 * Módulo para cargar y mostrar cartas flotantes de fondo
 * Reutilizable en todas las páginas
 */

// Función para cargar cartas flotantes de fondo
async function loadFloatingCards() {
    try {
        console.log('Cargando cartas flotantes...');
        
        // Verificar que la API esté disponible
        if (!api) {
            console.error('API no está disponible');
            return;
        }
        
        // 80 cartas para mejor efecto visual (todas diferentes)
        let response;
        try {
            response = await api.getCards({ limite: 80 });
        } catch (apiError) {
            console.error('Error en la llamada a la API:', apiError);
            console.warn('No se pudieron cargar cartas de la API, continuando sin cartas de fondo');
            return;
        }
        
        console.log('Respuesta de API:', response);
        
        if (response.success && response.data && response.data.length > 0) {
            const cards = response.data;
            const container = document.getElementById('floatingCardsBackground');
            
            if (!container) {
                console.error('No se encontró el contenedor de cartas flotantes');
                return;
            }
            
            console.log(`Se encontraron ${cards.length} cartas`);
            
            // Tamaños disponibles
            const sizes = ['small', 'medium', 'large'];
            
            // Filtrar solo cartas con imagen
            const cardsWithImages = cards.filter(card => card.imagenUrl);
            console.log(`Cartas con imagen: ${cardsWithImages.length}`);
            
            // Limitar a máximo 80 cartas (todas diferentes)
            // Usar un Map para asegurar que no haya duplicados por ID
            const uniqueCards = new Map();
            const allCards = cardsWithImages.length > 0 ? cardsWithImages : cards;
            
            for (const card of allCards) {
                if (!uniqueCards.has(card.id)) {
                    uniqueCards.set(card.id, card);
                    if (uniqueCards.size >= 80) break;
                }
            }
            
            const cardsToShow = Array.from(uniqueCards.values());
            
            console.log(`Mostrando ${cardsToShow.length} cartas`);
            
            // Array para almacenar posiciones de cartas ya colocadas (para evitar superposiciones)
            const placedCards = [];
            const minDistance = 12; // Distancia mínima en porcentaje entre cartas
            
            // Función mejorada para verificar si una posición está demasiado cerca de otras cartas
            function isPositionValid(x, y, width, height, placedCards) {
                for (const placed of placedCards) {
                    // Calcular distancia entre centros
                    const centerX1 = x + width / 2;
                    const centerY1 = y + height / 2;
                    const centerX2 = placed.x + placed.width / 2;
                    const centerY2 = placed.y + placed.height / 2;
                    
                    const distanceX = Math.abs(centerX1 - centerX2);
                    const distanceY = Math.abs(centerY1 - centerY2);
                    
                    // Distancia mínima requerida (mitad del ancho + mitad del alto + espacio mínimo)
                    const minDistX = (width / 2) + (placed.width / 2) + minDistance;
                    const minDistY = (height / 2) + (placed.height / 2) + minDistance;
                    
                    if (distanceX < minDistX && distanceY < minDistY) {
                        return false;
                    }
                }
                return true;
            }
            
            // Función mejorada para encontrar una posición válida
            function findValidPosition(width, height, placedCards, maxAttempts = 100) {
                for (let attempt = 0; attempt < maxAttempts; attempt++) {
                    let left, top;
                    
                    // Dividir la pantalla en más zonas para mejor distribución
                    const zone = Math.floor(Math.random() * 8);
                    switch(zone) {
                        case 0: // Esquina superior izquierda
                            left = 3 + Math.random() * 20;
                            top = 3 + Math.random() * 20;
                            break;
                        case 1: // Borde superior izquierdo
                            left = 3 + Math.random() * 20;
                            top = 25 + Math.random() * 15;
                            break;
                        case 2: // Esquina superior derecha
                            left = 77 + Math.random() * 20;
                            top = 3 + Math.random() * 20;
                            break;
                        case 3: // Borde superior derecho
                            left = 77 + Math.random() * 20;
                            top = 25 + Math.random() * 15;
                            break;
                        case 4: // Esquina inferior izquierda
                            left = 3 + Math.random() * 20;
                            top = 77 + Math.random() * 20;
                            break;
                        case 5: // Borde inferior izquierdo
                            left = 3 + Math.random() * 20;
                            top = 60 + Math.random() * 15;
                            break;
                        case 6: // Esquina inferior derecha
                            left = 77 + Math.random() * 20;
                            top = 77 + Math.random() * 20;
                            break;
                        case 7: // Borde inferior derecho
                            left = 77 + Math.random() * 20;
                            top = 60 + Math.random() * 15;
                            break;
                    }
                    
                    // Asegurar que no esté en el área central (donde está el contenido)
                    if (left > 25 && left < 75 && top > 20 && top < 80) {
                        // Si está en el área central, moverla a los bordes
                        if (Math.random() > 0.5) {
                            left = left < 50 ? 3 + Math.random() * 20 : 77 + Math.random() * 20;
                        } else {
                            top = top < 50 ? 3 + Math.random() * 20 : 77 + Math.random() * 20;
                        }
                    }
                    
                    if (isPositionValid(left, top, width, height, placedCards)) {
                        return { left, top };
                    }
                }
                // Si no se encuentra posición válida, usar posición aleatoria en los bordes
                const edge = Math.floor(Math.random() * 4);
                switch(edge) {
                    case 0: return { left: 3 + Math.random() * 20, top: 10 + Math.random() * 80 };
                    case 1: return { left: 77 + Math.random() * 20, top: 10 + Math.random() * 80 };
                    case 2: return { left: 10 + Math.random() * 80, top: 3 + Math.random() * 20 };
                    default: return { left: 10 + Math.random() * 80, top: 77 + Math.random() * 20 };
                }
            }
            
            cardsToShow.forEach((card, index) => {
                const cardElement = document.createElement('div');
                const sizeClass = sizes[index % sizes.length];
                cardElement.className = `floating-card ${sizeClass}`;
                
                // Obtener dimensiones según el tamaño (en porcentaje del viewport)
                let cardWidth, cardHeight;
                if (sizeClass === 'small') {
                    cardWidth = 4.2; // ~80px en viewport de 1920px
                    cardHeight = 5.8; // ~112px en viewport de 1920px
                } else if (sizeClass === 'medium') {
                    cardWidth = 6.25; // ~120px
                    cardHeight = 8.75; // ~168px
                } else {
                    cardWidth = 8.3; // ~160px
                    cardHeight = 11.7; // ~224px
                }
                
                // Encontrar posición válida ANTES de agregar la carta
                const position = findValidPosition(cardWidth, cardHeight, placedCards);
                
                // Guardar posición INMEDIATAMENTE para evitar que otras cartas se superpongan
                placedCards.push({
                    x: position.left,
                    y: position.top,
                    width: cardWidth,
                    height: cardHeight
                });
                
                // Aplicar posición
                cardElement.style.left = `${position.left}%`;
                cardElement.style.top = `${position.top}%`;
                
                // Rotación aleatoria inicial
                const rotation = (Math.random() - 0.5) * 30;
                cardElement.style.transform = `rotate(${rotation}deg)`;
                
                const img = document.createElement('img');
                if (card.imagenUrl) {
                    img.src = card.imagenUrl;
                    img.loading = 'lazy';
                    img.decoding = 'async';
                    // Optimización: reducir calidad de imagen para mejor rendimiento
                    img.style.imageRendering = 'optimizeQuality';
                    console.log(`Cargando imagen ${index + 1}: ${card.imagenUrl}`);
                } else {
                    // Si no hay imagen, crear un placeholder visual
                    cardElement.style.backgroundColor = 'rgba(102, 126, 234, 0.3)';
                    cardElement.style.border = '2px solid rgba(255, 255, 255, 0.4)';
                    cardElement.style.borderRadius = '8px';
                    cardElement.style.display = 'flex';
                    cardElement.style.alignItems = 'center';
                    cardElement.style.justifyContent = 'center';
                    cardElement.innerHTML = '<span style="color: rgba(255,255,255,0.6); font-size: 0.8em;">🃏</span>';
                }
                img.alt = card.nombre || 'Carta';
                img.onload = function() {
                    console.log(`✓ Imagen ${index + 1} cargada: ${card.nombre || 'Sin nombre'}`);
                };
                img.onerror = function() {
                    console.error(`✗ Error al cargar imagen ${index + 1}: ${card.imagenUrl}`);
                    // Si la imagen falla, crear placeholder
                    cardElement.style.backgroundColor = 'rgba(102, 126, 234, 0.3)';
                    cardElement.style.border = '2px solid rgba(255, 255, 255, 0.4)';
                    cardElement.innerHTML = '<span style="color: rgba(255,255,255,0.6); font-size: 0.8em;">🃏</span>';
                };
                
                if (card.imagenUrl) {
                    cardElement.appendChild(img);
                }
                container.appendChild(cardElement);
            });
            
            console.log(`Se agregaron ${cardsToShow.length} cartas al fondo`);
        } else {
            console.warn('No se recibieron cartas de la API o la respuesta no tiene el formato esperado');
        }
    } catch (error) {
        console.error('Error al cargar cartas para el fondo:', error);
        // No hacer nada más, simplemente no mostrar cartas de fondo
        // La página seguirá funcionando normalmente
    }
}

// Auto-inicializar cuando el DOM esté listo (si el contenedor existe)
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('floatingCardsBackground')) {
        loadFloatingCards();
    }
});








