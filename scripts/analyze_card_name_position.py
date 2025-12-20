#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar dónde se encuentra el nombre de las cartas en las imágenes
y determinar la posición típica del texto
"""

import sqlite3
import sys
from pathlib import Path
from collections import defaultdict

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Intentar importar las librerías
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  Advertencia: pytesseract o Pillow no están instalados.")
    print("   Instala las dependencias con: pip install pytesseract pillow")

# Configuración
BASE_DIR = Path(__file__).parent.parent
CARDS_DATA_DIR = BASE_DIR / "server" / "data"
IMAGES_NEW_DIR = BASE_DIR / "public" / "images" / "cards_new"
DB_NEW_PATH = CARDS_DATA_DIR / "game.db"

def normalizar_edicion(edicion):
    """Normaliza el nombre de edición para carpetas"""
    if not edicion:
        return None
    
    mapeo = {
        'espada sagrada': 'espada_sagrada',
        'helénica': 'helenica',
        'hijos de daana': 'hijos_de_daana',
        'dominios de ra': 'dominios_de_ra'
    }
    
    edicion_lower = edicion.lower()
    return mapeo.get(edicion_lower, edicion_lower.replace(' ', '_'))

def normalizar_raza(raza):
    """Normaliza el nombre de raza para carpetas"""
    if not raza or raza.strip() == '':
        return 'sin_raza'
    
    raza_lower = raza.lower()
    raza_lower = raza_lower.replace('ó', 'o').replace('é', 'e').replace('í', 'i').replace('á', 'a').replace('ú', 'u')
    
    mapeo = {
        'caballero': 'caballero',
        'dragon': 'dragon',
        'faerie': 'faerie',
        'heroe': 'heroe',
        'olimpico': 'olimpico',
        'titan': 'titan',
        'eterno': 'eterno',
        'faraon': 'faraon',
        'sacerdote': 'sacerdote'
    }
    
    return mapeo.get(raza_lower, 'sin_raza')

def normalizar_tipo(tipo):
    """Normaliza el tipo para carpetas"""
    if not tipo:
        return None
    
    tipo_lower = tipo.lower()
    mapeo = {
        'aliado': 'aliado',
        'talisman': 'talismán',
        'talismán': 'talismán',
        'oro': 'oro',
        'totem': 'tótem',
        'tótem': 'tótem',
        'arma': 'arma'
    }
    
    return mapeo.get(tipo_lower, tipo_lower)

def encontrar_imagen_carta(carta):
    """Encuentra la ruta de la imagen para una carta"""
    edicion = normalizar_edicion(carta.get('edicion'))
    raza = normalizar_raza(carta.get('raza'))
    tipo = normalizar_tipo(carta.get('tipo'))
    
    if not edicion or not tipo:
        return None
    
    ruta_base = IMAGES_NEW_DIR / edicion / raza / tipo
    
    if not ruta_base.exists():
        return None
    
    archivos_imagen = list(ruta_base.glob('*.png')) + list(ruta_base.glob('*.jpg'))
    
    if not archivos_imagen:
        return None
    
    # Buscar por nombre de archivo del campo imagen
    nombre_imagen = carta.get('imagen', '').lower()
    if nombre_imagen:
        nombre_archivo = Path(nombre_imagen).name
        for archivo in archivos_imagen:
            if archivo.name.lower() == nombre_archivo.lower():
                return archivo
    
    # Buscar por números del ID
    import re
    id_carta = carta.get('id', '').lower()
    numeros_id = re.findall(r'\d+', id_carta)
    for numero in numeros_id:
        for formato in [numero, numero.zfill(3), numero.zfill(4)]:
            for archivo in archivos_imagen:
                if formato in archivo.stem:
                    return archivo
    
    return archivos_imagen[0] if archivos_imagen else None

def analizar_posicion_texto(ruta_imagen, nombre_esperado):
    """Analiza la posición del texto en la imagen usando OCR con bounding boxes"""
    if not OCR_AVAILABLE:
        return None
    
    try:
        imagen = Image.open(ruta_imagen)
        ancho, alto = imagen.size
        
        # Obtener datos de OCR con bounding boxes
        datos_ocr = pytesseract.image_to_data(imagen, lang='spa+eng', output_type=pytesseract.Output.DICT)
        
        # Buscar el texto que coincida con el nombre esperado
        nombre_normalizado = nombre_esperado.lower().strip()
        palabras_nombre = set(nombre_normalizado.split())
        
        posiciones = []
        textos_encontrados = []
        
        # Procesar cada palabra detectada
        for i in range(len(datos_ocr['text'])):
            texto = datos_ocr['text'][i].strip()
            if texto and len(texto) > 2:  # Ignorar texto muy corto
                confianza = int(datos_ocr['conf'][i])
                if confianza > 30:  # Filtrar texto con baja confianza
                    x = datos_ocr['left'][i]
                    y = datos_ocr['top'][i]
                    w = datos_ocr['width'][i]
                    h = datos_ocr['height'][i]
                    
                    # Normalizar posiciones como porcentajes
                    x_pct = (x / ancho) * 100
                    y_pct = (y / alto) * 100
                    w_pct = (w / ancho) * 100
                    h_pct = (h / alto) * 100
                    
                    # Verificar si esta palabra podría ser parte del nombre
                    texto_normalizado = texto.lower()
                    es_relevante = any(palabra in texto_normalizado or texto_normalizado in palabra 
                                     for palabra in palabras_nombre if len(palabra) > 3)
                    
                    if es_relevante or confianza > 60:
                        posiciones.append({
                            'texto': texto,
                            'x': x, 'y': y, 'w': w, 'h': h,
                            'x_pct': x_pct, 'y_pct': y_pct,
                            'w_pct': w_pct, 'h_pct': h_pct,
                            'confianza': confianza
                        })
                        textos_encontrados.append(texto)
        
        # Calcular región promedio donde está el texto relevante
        if posiciones:
            # Filtrar posiciones en la parte IZQUIERDA (donde está el nombre escrito verticalmente)
            # El nombre está en el lado izquierdo, aproximadamente 10-20% del ancho
            posiciones_izquierdas = [p for p in posiciones if p['x_pct'] < 25]
            
            if posiciones_izquierdas:
                x_promedio = sum(p['x_pct'] for p in posiciones_izquierdas) / len(posiciones_izquierdas)
                y_min = min(p['y_pct'] for p in posiciones_izquierdas)
                y_max = max(p['y_pct'] + p['h_pct'] for p in posiciones_izquierdas)
                x_max = max(p['x_pct'] + p['w_pct'] for p in posiciones_izquierdas)
                
                return {
                    'ancho_imagen': ancho,
                    'alto_imagen': alto,
                    'x_pct': x_promedio,
                    'y_pct': y_min,
                    'ancho_pct': x_max - x_promedio,
                    'alto_pct': y_max - y_min,
                    'textos': textos_encontrados[:5],  # Primeros 5 textos
                    'posiciones': posiciones_izquierdas[:3]  # Primeras 3 posiciones
                }
        
        return None
        
    except Exception as e:
        print(f"   ⚠️  Error al analizar {ruta_imagen.name}: {e}")
        return None

def analizar_muestras(limite=20):
    """Analiza una muestra de cartas para determinar la posición típica del nombre"""
    if not OCR_AVAILABLE:
        print("❌ No se puede ejecutar sin las dependencias de OCR instaladas.")
        return
    
    if not DB_NEW_PATH.exists():
        print(f"❌ No se encontró la base de datos en: {DB_NEW_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_NEW_PATH))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, nombre, edicion, raza, tipo, imagen 
        FROM cartas 
        WHERE nombre IS NOT NULL AND nombre != ''
        ORDER BY RANDOM()
        LIMIT ?
    """, (limite,))
    
    cartas = cursor.fetchall()
    
    print(f"📋 Analizando {len(cartas)} cartas para determinar posición del nombre...")
    print("=" * 80)
    
    estadisticas = {
        'x_pct': [],
        'y_pct': [],
        'ancho_pct': [],
        'alto_pct': [],
        'anchos': [],
        'altos': []
    }
    
    resultados_exitosos = 0
    
    for idx, (id_carta, nombre, edicion, raza, tipo, imagen) in enumerate(cartas, 1):
        carta = {
            'id': id_carta,
            'nombre': nombre,
            'edicion': edicion,
            'raza': raza,
            'tipo': tipo,
            'imagen': imagen
        }
        
        print(f"\n[{idx}/{len(cartas)}] {nombre}")
        
        ruta_imagen = encontrar_imagen_carta(carta)
        
        if not ruta_imagen:
            print(f"   ⚠️  No se encontró imagen")
            continue
        
        resultado = analizar_posicion_texto(ruta_imagen, nombre)
        
        if resultado:
            resultados_exitosos += 1
            estadisticas['x_pct'].append(resultado['x_pct'])
            estadisticas['y_pct'].append(resultado['y_pct'])
            estadisticas['ancho_pct'].append(resultado['ancho_pct'])
            estadisticas['alto_pct'].append(resultado['alto_pct'])
            estadisticas['anchos'].append(resultado['ancho_imagen'])
            estadisticas['altos'].append(resultado['alto_imagen'])
            
            print(f"   ✅ Texto encontrado en:")
            print(f"      Posición X (izquierda): {resultado['x_pct']:.1f}% - {resultado['x_pct'] + resultado['ancho_pct']:.1f}%")
            print(f"      Posición Y (altura): {resultado['y_pct']:.1f}% - {resultado['y_pct'] + resultado['alto_pct']:.1f}%")
            print(f"      Textos detectados: {', '.join(resultado['textos'][:3])}")
        else:
            print(f"   ⚠️  No se pudo detectar texto relevante")
    
    conn.close()
    
    # Mostrar estadísticas
    if resultados_exitosos > 0:
        print("\n" + "=" * 80)
        print("📊 ESTADÍSTICAS DE POSICIÓN DEL NOMBRE")
        print("=" * 80)
        
        import statistics
        
        print(f"\n✅ Cartas analizadas exitosamente: {resultados_exitosos}/{len(cartas)}")
        print(f"\n📍 Posición promedio del nombre (LADO IZQUIERDO, texto VERTICAL):")
        print(f"   X (desde izquierda): {statistics.mean(estadisticas['x_pct']):.1f}% (rango: {min(estadisticas['x_pct']):.1f}% - {max(estadisticas['x_pct']):.1f}%)")
        print(f"   Y (altura): {statistics.mean(estadisticas['y_pct']):.1f}% (rango: {min(estadisticas['y_pct']):.1f}% - {max(estadisticas['y_pct']):.1f}%)")
        print(f"   Ancho (región): {statistics.mean(estadisticas['ancho_pct']):.1f}%")
        print(f"   Alto (región): {statistics.mean(estadisticas['alto_pct']):.1f}%")
        
        print(f"\n📐 Dimensiones típicas de las imágenes:")
        print(f"   Ancho promedio: {statistics.mean(estadisticas['anchos']):.0f}px")
        print(f"   Alto promedio: {statistics.mean(estadisticas['altos']):.0f}px")
        
        # Calcular región recomendada para recortar (LADO IZQUIERDO)
        x_promedio = statistics.mean(estadisticas['x_pct'])
        x_min = min(estadisticas['x_pct'])
        x_max = max(estadisticas['x_pct']) + statistics.mean(estadisticas['ancho_pct'])
        y_min = min(estadisticas['y_pct'])
        y_max = max(estadisticas['y_pct']) + statistics.mean(estadisticas['alto_pct'])
        
        print(f"\n🎯 REGIÓN RECOMENDADA PARA RECORTAR (LADO IZQUIERDO - porcentajes):")
        print(f"   X desde: {max(0, x_min - 2):.1f}%")
        print(f"   X hasta: {min(100, x_max + 2):.1f}%")
        print(f"   Y desde: {max(0, y_min - 2):.1f}%")
        print(f"   Y hasta: {min(100, y_max + 5):.1f}%")
        print(f"   NOTA: El texto está escrito VERTICALMENTE, se debe rotar -90° después de recortar")
        
        # Para píxeles (asumiendo tamaño promedio)
        ancho_promedio = statistics.mean(estadisticas['anchos'])
        alto_promedio = statistics.mean(estadisticas['altos'])
        
        print(f"\n🎯 REGIÓN RECOMENDADA PARA RECORTAR (píxeles, tamaño {ancho_promedio:.0f}x{alto_promedio:.0f}):")
        print(f"   X desde: {int((max(0, x_min - 2) / 100) * ancho_promedio)}px")
        print(f"   X hasta: {int((min(100, x_max + 2) / 100) * ancho_promedio)}px")
        print(f"   Y desde: {int((max(0, y_min - 2) / 100) * alto_promedio)}px")
        print(f"   Y hasta: {int((min(100, y_max + 5) / 100) * alto_promedio)}px")
    else:
        print("\n⚠️  No se pudieron analizar suficientes cartas para obtener estadísticas.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analiza la posición del nombre en las imágenes de cartas')
    parser.add_argument('--limite', type=int, default=20, help='Número de cartas a analizar (default: 20)')
    
    args = parser.parse_args()
    
    analizar_muestras(limite=args.limite)

