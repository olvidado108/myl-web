/**
 * Ejemplo de uso del CardRepository
 * Ejecutar con: node server/repository/example_usage.js
 */

const CardRepository = require('./CardRepository');
const path = require('path');

async function ejemplo() {
    console.log('='.repeat(60));
    console.log('📚 Ejemplo de Uso - CardRepository');
    console.log('='.repeat(60));

    // Crear instancia del repositorio
    const repo = new CardRepository();

    // Cargar todas las cartas automáticamente
    console.log('\n📥 Cargando cartas desde JSON...');
    const cargadas = repo.cargarTodas();
    console.log(`✅ ${cargadas} cartas cargadas\n`);

    // Ejemplo 1: Buscar por ID
    console.log('1️⃣  Buscar por ID:');
    const carta = repo.buscarPorId('es559');
    if (carta) {
        console.log(`   Encontrada: ${carta.nombre} (${carta.tipo})`);
    } else {
        console.log('   No encontrada');
    }

    // Ejemplo 2: Buscar por nombre
    console.log('\n2️⃣  Buscar por nombre (parcial):');
    const resultados = repo.buscarPorNombre('Arturo', false);
    console.log(`   Encontradas ${resultados.length} cartas:`);
    resultados.slice(0, 5).forEach(c => {
        console.log(`   - ${c.nombre} (${c.tipo})`);
    });

    // Ejemplo 3: Buscar por tipo
    console.log('\n3️⃣  Buscar por tipo (Aliado):');
    const aliados = repo.buscarPorTipo('Aliado');
    console.log(`   Total de Aliados: ${aliados.length}`);

    // Ejemplo 4: Buscar por raza
    console.log('\n4️⃣  Buscar por raza (Caballero):');
    const caballeros = repo.buscarPorRaza('Caballero');
    console.log(`   Total de Caballeros: ${caballeros.length}`);
    caballeros.slice(0, 5).forEach(c => {
        console.log(`   - ${c.nombre} (Ataque: ${c.ataque}, Defensa: ${c.defensa})`);
    });

    // Ejemplo 5: Búsqueda avanzada
    console.log('\n5️⃣  Búsqueda avanzada (Aliados Caballeros de Espada Sagrada):');
    const avanzada = repo.buscar({
        tipo: 'Aliado',
        raza: 'Caballero',
        edicion: 'espada sagrada',
        limite: 10
    });
    console.log(`   Encontradas ${avanzada.length} cartas:`);
    avanzada.forEach(c => {
        console.log(`   - ${c.nombre} (Coste: ${c.coste}, Ataque: ${c.ataque})`);
    });

    // Ejemplo 6: Estadísticas
    console.log('\n6️⃣  Estadísticas:');
    const stats = repo.obtenerEstadisticas();
    console.log(`   Total de cartas: ${stats.total}`);
    console.log(`   Por tipo:`, stats.porTipo);
    console.log(`   Top 5 razas:`, Object.entries(stats.porRaza)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([raza, cantidad]) => `${raza}: ${cantidad}`)
        .join(', '));
    console.log(`   Por edición:`, stats.porEdicion);

    // Ejemplo 7: Obtener todas las cartas (sin variantes)
    console.log('\n7️⃣  Cartas únicas (sin variantes):');
    const unicas = repo.obtenerTodas(true);
    console.log(`   Total: ${unicas.length} cartas únicas`);

    console.log('\n✅ Ejemplo completado!');
}

// Ejecutar ejemplo
ejemplo().catch(console.error);







