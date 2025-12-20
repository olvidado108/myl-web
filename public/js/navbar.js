/**
 * Componente de barra de navegación
 */

let currentUser = null;
let navbarInitialized = false;

// Inicializar la barra de navegación
async function initNavbar() {
    if (navbarInitialized) return;
    
    try {
        // Verificar si el usuario está autenticado
        if (api.isAuthenticated()) {
            const userResponse = await api.getCurrentUser();
            if (userResponse.success && userResponse.data) {
                currentUser = userResponse.data;
                renderNavbar(true);
            } else {
                renderNavbar(false);
            }
        } else {
            renderNavbar(false);
        }
    } catch (error) {
        console.error('Error al inicializar navbar:', error);
        renderNavbar(false);
    }
    
    navbarInitialized = true;
}

// Renderizar la barra de navegación
function renderNavbar(isAuthenticated) {
    const navbarContainer = document.getElementById('navbar-container');
    if (!navbarContainer) return;

    if (isAuthenticated && currentUser) {
        navbarContainer.innerHTML = `
        <nav class="navbar">
            <div class="navbar-container">
            <div class="navbar-brand">
                <a href="home.html">
                    <img src="images/logo.webp" alt="Mitos y Leyendas Logo">
                    Mitos y Leyendas
                </a>
            </div>
            <button class="navbar-toggle" onclick="toggleMobileMenu()">☰</button>
            <ul class="navbar-menu" id="navbar-menu">
                <li class="navbar-item">
                    <a href="cards.html" class="navbar-link ${isCurrentPage('cards.html') ? 'active' : ''}">
                        📚 Cartas
                    </a>
                </li>
                <li class="navbar-item">
                    <a href="decks.html" class="navbar-link ${isCurrentPage('decks.html') ? 'active' : ''}">
                        🎴 Mazos
                    </a>
                </li>
                <li class="navbar-item">
                    <a href="game.html" class="navbar-link ${isCurrentPage('game.html') ? 'active' : ''}">
                        🎮 Jugar
                    </a>
                </li>
                <li class="navbar-item">
                    <a href="deck-builder.html" class="navbar-link ${isCurrentPage('deck-builder.html') ? 'active' : ''}">
                        🔨 Constructor
                    </a>
                </li>
                <li class="navbar-item">
                    <a href="profile.html" class="navbar-link ${isCurrentPage('profile.html') ? 'active' : ''}">
                        👤 Perfil
                    </a>
                </li>
                ${currentUser.isAdmin ? `
                <li class="navbar-item">
                    <a href="admin-users.html" class="navbar-link ${isCurrentPage('admin-users.html') ? 'active' : ''}">
                        🔐 Admin
                    </a>
                </li>
                ` : ''}
            </ul>
            <div class="navbar-user-section">
                <div class="navbar-user-info" onclick="toggleUserDropdown()">
                    <div class="navbar-user-avatar" id="navbar-avatar">
                        ${getAvatarContent()}
                    </div>
                    <div class="navbar-user-text">
                        <div class="navbar-username">${escapeHtml(currentUser.username || 'Usuario')}</div>
                        <div class="navbar-user-role">
                            <span class="navbar-badge ${currentUser.isAdmin ? 'navbar-badge-admin' : 'navbar-badge-user'}">
                                ${currentUser.isAdmin ? 'Administrador' : 'Usuario'}
                            </span>
                        </div>
                    </div>
                </div>
                <div class="navbar-dropdown" id="navbar-dropdown">
                    <a href="profile.html" class="navbar-dropdown-item">
                        <span>👤</span>
                        <span>Mi Perfil</span>
                    </a>
                    ${currentUser.isAdmin ? `
                    <a href="admin-users.html" class="navbar-dropdown-item">
                        <span>🔐</span>
                        <span>Administración</span>
                    </a>
                    ` : ''}
                    <a href="#" class="navbar-dropdown-item danger" onclick="handleLogout(); return false;">
                        <span>🚪</span>
                        <span>Cerrar Sesión</span>
                    </a>
                </div>
            </div>
            </div>
        </nav>
        `;
        
        // Establecer imagen de avatar si existe
        if (currentUser.avatar_url) {
            const avatar = document.getElementById('navbar-avatar');
            if (avatar) {
                avatar.style.backgroundImage = `url(${currentUser.avatar_url})`;
                avatar.textContent = '';
            }
        }
    } else {
        navbarContainer.innerHTML = `
        <nav class="navbar">
            <div class="navbar-container">
            <div class="navbar-brand">
                <a href="home.html">
                    <img src="images/logo.webp" alt="Mitos y Leyendas Logo">
                    Mitos y Leyendas
                </a>
            </div>
            <button class="navbar-toggle" onclick="toggleMobileMenu()">☰</button>
            <ul class="navbar-menu" id="navbar-menu">
                <li class="navbar-item">
                    <a href="cards.html" class="navbar-link ${isCurrentPage('cards.html') ? 'active' : ''}">
                        📚 Cartas
                    </a>
                </li>
            </ul>
            <div class="navbar-user-section">
                <div class="navbar-auth-buttons">
                    <a href="login.html" class="navbar-btn navbar-btn-primary">Iniciar Sesión</a>
                    <a href="register.html" class="navbar-btn navbar-btn-secondary">Registrarse</a>
                </div>
            </div>
            </div>
        </nav>
        `;
    }
}

// Obtener contenido del avatar
function getAvatarContent() {
    if (currentUser && currentUser.avatar_url) {
        return '';
    }
    const username = currentUser?.username || 'U';
    return username.charAt(0).toUpperCase();
}

// Verificar si es la página actual
function isCurrentPage(pageName) {
    const currentPath = window.location.pathname;
    return currentPath.includes(pageName) || (pageName === 'home.html' && (currentPath === '/' || currentPath.includes('index.html')));
}

// Toggle del menú móvil
function toggleMobileMenu() {
    const menu = document.getElementById('navbar-menu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// Toggle del dropdown de usuario
function toggleUserDropdown() {
    const dropdown = document.getElementById('navbar-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Cerrar dropdown al hacer click fuera
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('navbar-dropdown');
    const userInfo = document.querySelector('.navbar-user-info');
    
    if (dropdown && userInfo && !dropdown.contains(event.target) && !userInfo.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

// Manejar cierre de sesión
function handleLogout() {
    if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
        logout();
    }
}

// Función de escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavbar);
} else {
    initNavbar();
}

