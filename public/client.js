// Cliente principal del juego
console.log('🎮 Cliente cargado correctamente');

// Esperar a que el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ DOM cargado');
    
    // Aquí se integrará Phaser en la Fase 2
    const canvas = document.getElementById('game-canvas');
    if (canvas) {
        canvas.width = 1200;
        canvas.height = 800;
        const ctx = canvas.getContext('2d');
        
        // Dibujo de prueba
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#ffffff';
        ctx.font = '24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Fase 0: Preparación completada', canvas.width / 2, canvas.height / 2);
    }
});

