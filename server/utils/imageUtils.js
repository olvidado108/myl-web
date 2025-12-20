/**
 * Utilidades para buscar y mapear imágenes de cartas
 */

const fs = require('fs');
const path = require('path');

// Intentar usar la nueva carpeta primero, luego la antigua como fallback
const CARDS_NEW_DIR = path.join(__dirname, '../../public/images/cards_new');
const CARDS_ORGANIZED_DIR = path.join(__dirname, '../../public/images/cards_organized');
const CARD_PLACEHOLDER = process.env.CARD_PLACEHOLDER || '/images/cards_new/placeholder.svg';

/**
 * Normaliza el nombre de edición para coincidir con la estructura de carpetas
 */
function normalizarEdicion(edicion) {
    if (!edicion) return null;
    
    const mapeo = {
        'espada sagrada': 'espada_sagrada',
        'dominios de ra': 'dominios_de_ra',
        'hijos de daana': 'hijos_de_daana',
        'es': 'es',
        'helenica': 'helenica'
    };
    
    const edicionLower = edicion.toLowerCase();
    return mapeo[edicionLower] || edicionLower.replace(/\s+/g, '_');
}

/**
 * Normaliza el nombre de raza para coincidir con la estructura de carpetas
 */
function normalizarRaza(raza) {
    if (!raza) return 'sin_raza';
    
    const mapeo = {
        'caballero': 'caballero',
        'dragon': 'dragon',
        'dragón': 'dragon', // Normalizar con tilde
        'faerie': 'faerie',
        'heroe': 'heroe',
        'héroe': 'heroe', // Normalizar con tilde
        'olimpico': 'olimpico',
        'olímpico': 'olimpico', // Normalizar con tilde
        'titan': 'titan',
        'titán': 'titan', // Normalizar con tilde
        'eterno': 'eterno',
        'faraon': 'faraon',
        'faraón': 'faraon', // Normalizar con tilde
        'sacerdote': 'sacerdote',
        'defensor': 'defensor',
        'desafiante': 'desafiante',
        'sombra': 'sombra'
    };
    
    // Normalizar tildes y convertir a minúsculas
    const razaLower = raza.toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, ''); // Eliminar tildes
    
    return mapeo[razaLower] || 'sin_raza';
}

/**
 * Normaliza el tipo para coincidir con la estructura de carpetas
 */
function normalizarTipo(tipo) {
    if (!tipo) return null;
    
    const tipoLower = tipo.toLowerCase();
    const mapeo = {
        'aliado': 'aliado',
        'talisman': 'talisman',
        'oro': 'oro',
        'totem': 'totem',
        'arma': 'arma'
    };
    
    return mapeo[tipoLower] || tipoLower;
}

/**
 * Extrae números del ID de la carta para buscar imágenes
 */
function extraerNumerosDelId(id) {
    if (!id) return [];
    const numeros = id.match(/\d+/g);
    return numeros ? numeros.map(n => parseInt(n)) : [];
}

/**
 * Extrae el nombre del archivo del campo imagen de la carta
 */
function extraerNombreArchivo(campoImagen) {
    if (!campoImagen) return null;
    
    // Si tiene una ruta completa, extraer solo el nombre del archivo
    const nombre = path.basename(campoImagen);
    
    // Si tiene extensión, devolverlo
    if (nombre.includes('.')) {
        return nombre.toLowerCase();
    }
    
    return null;
}

/**
 * Busca imágenes que puedan coincidir con el ID de la carta
 */
function buscarImagenPorId(carta, archivos) {
    if (!carta.id) return null;
    
    const numerosId = extraerNumerosDelId(carta.id);
    const idLower = carta.id.toLowerCase();
    
    // Buscar archivos que contengan números del ID (con padding de ceros)
    for (const numero of numerosId) {
        // Buscar con diferentes formatos: 559, 0559, 00559, etc.
        const formatos = [
            numero.toString(),
            numero.toString().padStart(3, '0'),
            numero.toString().padStart(4, '0'),
            numero.toString().padStart(5, '0')
        ];
        
        for (const formato of formatos) {
            const imagenEncontrada = archivos.find(archivo => {
                const archivoLower = archivo.toLowerCase();
                // Buscar el número en el nombre del archivo
                return archivoLower.includes(`_${formato}.`) || 
                       archivoLower.includes(`_${formato}_`) ||
                       archivoLower.includes(`${formato}.png`) ||
                       archivoLower.includes(`${formato}.jpg`);
            });
            
            if (imagenEncontrada) {
                return imagenEncontrada;
            }
        }
    }
    
    return null;
}

/**
 * Busca imágenes usando el nombre del archivo del campo "imagen"
 */
function buscarImagenPorCampoImagen(carta, archivos) {
    if (!carta.imagen) return null;
    
    const nombreArchivo = extraerNombreArchivo(carta.imagen);
    if (!nombreArchivo) return null;
    
    // Buscar archivo exacto
    const imagenExacta = archivos.find(archivo => 
        archivo.toLowerCase() === nombreArchivo
    );
    if (imagenExacta) return imagenExacta;
    
    // Buscar archivo que contenga el nombre (sin extensión)
    const nombreSinExt = nombreArchivo.replace(/\.(png|jpg|jpeg)$/, '');
    const imagenParcial = archivos.find(archivo => {
        const archivoSinExt = archivo.toLowerCase().replace(/\.(png|jpg|jpeg)$/, '');
        return archivoSinExt.includes(nombreSinExt) || nombreSinExt.includes(archivoSinExt);
    });
    if (imagenParcial) return imagenParcial;
    
    // Buscar por partes del nombre (separado por guiones bajos o guiones)
    const partes = nombreSinExt.split(/[_\-\s]+/).filter(p => p.length > 2);
    for (const parte of partes) {
        const imagenEncontrada = archivos.find(archivo => 
            archivo.toLowerCase().includes(parte)
        );
        if (imagenEncontrada) return imagenEncontrada;
    }
    
    return null;
}

/**
 * Extrae el kit/expansión del campo imagen de la carta
 * Ejemplo: "kit-raciales-2024/27.png" -> "kit_raciales_2024"
 */
function extraerKitExpansion(carta) {
    if (!carta.imagen) return null;
    
    // El campo imagen puede tener formato: "kit-raciales-2024/27.png" o "edicion/raza/tipo/kit/archivo.png"
    const partes = carta.imagen.split('/');
    
    // Si tiene formato antiguo (solo kit/archivo), extraer el kit
    if (partes.length === 2 && !partes[0].includes('_')) {
        return partes[0].toLowerCase().replace(/-/g, '_').replace(/\s+/g, '_');
    }
    
    // Si tiene formato nuevo (edicion/raza/tipo/kit/archivo), extraer el kit (penúltimo elemento)
    if (partes.length >= 4) {
        const kit = partes[partes.length - 2];
        return kit.toLowerCase().replace(/-/g, '_').replace(/\s+/g, '_');
    }
    
    // Si no se puede extraer, usar el campo kit de la carta
    if (carta.kit) {
        return carta.kit.toLowerCase().replace(/-/g, '_').replace(/\s+/g, '_');
    }
    
    return null;
}

/**
 * Busca la ruta de imagen para una carta basándose en edición/raza/tipo/kit
 */
function buscarImagenCarta(carta) {
    // Estrategia 0: Si el campo imagen ya tiene una ruta completa guardada (formato: edicion/raza/tipo/kit/archivo),
    // verificar si existe y usarla directamente
    if (carta.imagen && carta.imagen.includes('/')) {
        const partesImagen = carta.imagen.split('/');
        // Si tiene 5 partes (edicion/raza/tipo/kit/archivo), es una ruta completa
        if (partesImagen.length >= 4) {
            // Intentar primero en cards_new
            const rutaCompletaNew = path.join(CARDS_NEW_DIR, carta.imagen);
            if (fs.existsSync(rutaCompletaNew)) {
                return `/images/cards_new/${carta.imagen}`;
            }
            
            // Intentar en cards_organized
            const rutaCompletaOrg = path.join(CARDS_ORGANIZED_DIR, carta.imagen);
            if (fs.existsSync(rutaCompletaOrg)) {
                return `/images/cards_organized/${carta.imagen}`;
            }
        }
    }
    
    const edicion = normalizarEdicion(carta.edicion);
    const raza = normalizarRaza(carta.raza);
    const tipo = normalizarTipo(carta.tipo);
    
    if (!edicion || !tipo) {
        return CARD_PLACEHOLDER;
    }
    
    // Extraer kit/expansión del campo imagen
    const kitExpansion = extraerKitExpansion(carta);
    
    // Intentar primero en cards_new, luego en cards_organized
    let rutaBase = null;
    let basePath = 'cards_new';
    
    // Estrategia 1: Buscar con kit/expansión (estructura nueva)
    if (kitExpansion) {
        rutaBase = path.join(CARDS_NEW_DIR, edicion, raza, tipo, kitExpansion);
        if (fs.existsSync(rutaBase)) {
            basePath = 'cards_new';
        } else {
            rutaBase = path.join(CARDS_ORGANIZED_DIR, edicion, raza, tipo, kitExpansion);
            if (fs.existsSync(rutaBase)) {
                basePath = 'cards_organized';
            } else {
                rutaBase = null;
            }
        }
    }
    
    // Estrategia 2: Si no se encuentra con kit, buscar sin kit (estructura antigua)
    if (!rutaBase || !fs.existsSync(rutaBase)) {
        rutaBase = path.join(CARDS_NEW_DIR, edicion, raza, tipo);
        if (fs.existsSync(rutaBase)) {
            basePath = 'cards_new';
        } else {
            rutaBase = path.join(CARDS_ORGANIZED_DIR, edicion, raza, tipo);
            basePath = 'cards_organized';
            
            if (!fs.existsSync(rutaBase)) {
                return CARD_PLACEHOLDER;
            }
        }
    }
    
    // Buscar archivos en el directorio
    try {
        // Si estamos en una carpeta con kit, buscar directamente el archivo
        if (kitExpansion && rutaBase.includes(kitExpansion)) {
            const nombreArchivo = extraerNombreArchivo(carta.imagen);
            if (nombreArchivo) {
                const rutaCompleta = path.join(rutaBase, nombreArchivo);
                if (fs.existsSync(rutaCompleta)) {
                    return `/images/${basePath}/${edicion}/${raza}/${tipo}/${kitExpansion}/${nombreArchivo}`;
                }
            }
        }
        
        // Buscar todos los archivos en el directorio
        const archivos = fs.readdirSync(rutaBase).filter(archivo => {
            const stat = fs.statSync(path.join(rutaBase, archivo));
            // Si es un directorio, buscar dentro (para estructura con kit)
            if (stat.isDirectory()) {
                return false;
            }
            return archivo.toLowerCase().endsWith('.png') || 
                   archivo.toLowerCase().endsWith('.jpg');
        });
        
        if (archivos.length === 0) {
            // Si no hay archivos directos, buscar en subdirectorios (estructura con kit)
            const subdirs = fs.readdirSync(rutaBase).filter(archivo => {
                const stat = fs.statSync(path.join(rutaBase, archivo));
                return stat.isDirectory();
            });
            
            for (const subdir of subdirs) {
                const subdirPath = path.join(rutaBase, subdir);
                const archivosSubdir = fs.readdirSync(subdirPath).filter(archivo => 
                    archivo.toLowerCase().endsWith('.png') || 
                    archivo.toLowerCase().endsWith('.jpg')
                );
                
                // Buscar usando el nombre del archivo del campo "imagen"
                const nombreArchivo = extraerNombreArchivo(carta.imagen);
                if (nombreArchivo) {
                    const imagenEncontrada = archivosSubdir.find(archivo => 
                        archivo.toLowerCase() === nombreArchivo.toLowerCase()
                    );
                    if (imagenEncontrada) {
                        return `/images/${basePath}/${edicion}/${raza}/${tipo}/${subdir}/${imagenEncontrada}`;
                    }
                }
            }
            
            return CARD_PLACEHOLDER;
        }
        
        // Estrategia 1: Buscar usando el nombre del archivo del campo "imagen" (más preciso)
        const imagenPorCampo = buscarImagenPorCampoImagen(carta, archivos);
        if (imagenPorCampo) {
            const rutaKit = kitExpansion ? `${kitExpansion}/` : '';
            return `/images/${basePath}/${edicion}/${raza}/${tipo}/${rutaKit}${imagenPorCampo}`;
        }
        
        // Estrategia 2: Buscar por ID de la carta
        const imagenPorId = buscarImagenPorId(carta, archivos);
        if (imagenPorId) {
            const rutaKit = kitExpansion ? `${kitExpansion}/` : '';
            return `/images/${basePath}/${edicion}/${raza}/${tipo}/${rutaKit}${imagenPorId}`;
        }
        
        // Estrategia 3: Buscar por nombre de la carta (parcial) - solo si el nombre es único
        if (carta.nombre) {
            const palabrasNombre = carta.nombre.toLowerCase()
                .split(/\s+/)
                .filter(p => p.length > 4) // Solo palabras de más de 4 caracteres
                .slice(0, 2); // Solo las primeras 2 palabras
            
            for (const palabra of palabrasNombre) {
                const imagenEncontrada = archivos.find(archivo => 
                    archivo.toLowerCase().includes(palabra)
                );
                
                if (imagenEncontrada) {
                    const rutaKit = kitExpansion ? `${kitExpansion}/` : '';
                    return `/images/${basePath}/${edicion}/${raza}/${tipo}/${rutaKit}${imagenEncontrada}`;
                }
            }
        }
        
        // Estrategia 4: Si no se encuentra nada, NO devolver una imagen aleatoria
        // Es mejor no mostrar imagen que mostrar una incorrecta
        return CARD_PLACEHOLDER;
        
    } catch (error) {
        console.error(`Error al buscar imagen para carta ${carta.id}:`, error.message);
    }
    
    return CARD_PLACEHOLDER;
}

/**
 * Busca imágenes para múltiples cartas
 */
function buscarImagenesCartas(cartas) {
    return cartas.map(carta => {
        // Primero intentar buscar imagen local
        const imagenUrl = buscarImagenCarta(carta);
        
        // Si encontramos una imagen local, usarla
        if (imagenUrl) {
            return {
                ...carta,
                imagenUrl: imagenUrl
            };
        }
        
        // Si no hay imagen local, verificar si imagenUrl de la BD es local
        const imagenUrlBD = carta.imagenUrl;
        if (imagenUrlBD) {
            // Solo usar si es una ruta local (empieza con /images/ o images/)
            // NO usar URLs externas (http:// o https://)
            const esUrlLocal = imagenUrlBD.startsWith('/images/') || 
                              imagenUrlBD.startsWith('images/') ||
                              (!imagenUrlBD.startsWith('http://') && !imagenUrlBD.startsWith('https://'));
            
            if (esUrlLocal) {
                return {
                    ...carta,
                    imagenUrl: imagenUrlBD.startsWith('/') ? imagenUrlBD : `/images/${imagenUrlBD}`
                };
            }
        }
        
        // Si no hay imagen local ni URL local válida, no devolver imagenUrl
        return {
            ...carta,
            imagenUrl: CARD_PLACEHOLDER
        };
    });
}

module.exports = {
    buscarImagenCarta,
    buscarImagenesCartas,
    normalizarEdicion,
    normalizarRaza,
    normalizarTipo
};

