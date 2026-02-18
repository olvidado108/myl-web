/**
 * Funciones de autenticación para el frontend
 */

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.classList.add('error');
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

/**
 * Muestra un mensaje de éxito
 */
function showSuccess(message) {
    const successDiv = document.getElementById('successMessage');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        successDiv.classList.add('success');
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }
}

/**
 * Maneja el registro de usuario
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const username = form.username.value.trim();
    const email = form.email.value.trim();
    const password = form.password.value;
    const confirmPassword = form.confirmPassword?.value || '';
    const nombreCompleto = form.nombreCompleto?.value.trim() || '';

    // Validaciones básicas
    if (!username || !email || !password) {
        showError('Por favor completa todos los campos requeridos');
        return;
    }

    if (username.length < 3) {
        showError('El nombre de usuario debe tener al menos 3 caracteres');
        return;
    }

    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        showError('El nombre de usuario solo puede contener letras, números y guiones bajos');
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('Por favor ingresa un email válido');
        return;
    }

    if (password.length < 8) {
        showError('La contraseña debe tener al menos 8 caracteres');
        return;
    }

    if (confirmPassword && password !== confirmPassword) {
        showError('Las contraseñas no coinciden');
        return;
    }

    // Deshabilitar botón durante la petición
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registrando...';

    try {
        const response = await api.register(username, email, password, nombreCompleto);
        
        if (response.success) {
            showSuccess('¡Registro exitoso! Redirigiendo...');
            
            // Redirigir después de un breve delay
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        }
    } catch (error) {
        showError(error.message || 'Error al registrar usuario');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

/**
 * Maneja el inicio de sesión
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const username = form.username.value.trim();
    const password = form.password.value;

    if (!username || !password) {
        showError('Por favor completa todos los campos');
        return;
    }

    // Deshabilitar botón durante la petición
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Iniciando sesión...';

    try {
        const response = await api.login(username, password);
        
        if (response.success) {
            showSuccess('¡Bienvenido! Redirigiendo...');
            
            // Redirigir después de un breve delay
            setTimeout(() => {
                const redirectTo = new URLSearchParams(window.location.search).get('redirect') || '/';
                window.location.href = redirectTo;
            }, 1500);
        }
    } catch (error) {
        showError(error.message || 'Credenciales inválidas');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

/**
 * Verifica si el usuario está autenticado y redirige si es necesario
 */
async function checkAuth(redirectIfNotAuth = false) {
    try {
        if (api.isAuthenticated()) {
            const user = await api.getCurrentUser();
            return user.data;
        } else if (redirectIfNotAuth) {
            window.location.href = '/login.html';
            return null;
        }
        return null;
    } catch (error) {
        if (redirectIfNotAuth) {
            window.location.href = '/login.html';
        }
        return null;
    }
}

/**
 * Cierra sesión
 */
function logout() {
    api.logout();
    window.location.href = '/login.html';
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Registrar formulario de registro
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Registrar formulario de login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});











