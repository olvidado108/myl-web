#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que las imágenes de las cartas correspondan con el nombre correcto
usando OCR (Optical Character Recognition)
"""

import sqlite3
import sys
from pathlib import Path
import re
from difflib import SequenceMatcher

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Intentar importar las librerías de OCR
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  Advertencia: pytesseract o Pillow no están instalados.")
    print("   Instala las dependencias con: pip install pytesseract pillow")
    print("   También necesitas instalar Tesseract OCR:")
    print("   - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   - Linux: sudo apt-get install tesseract-ocr")
    print("   - macOS: brew install tesseract")

# Configuración
BASE_DIR = Path(__file__).parent.parent
CARDS_DATA_DIR = BASE_DIR / "server" / "data"
IMAGES_NEW_DIR = BASE_DIR / "public" / "images" / "cards_new"
DB_NEW_PATH = CARDS_DATA_DIR / "game.db"

def normalizar_texto(texto):
    """Normaliza el texto para comparación (minúsculas, sin acentos, sin espacios extra)"""
    if not texto:
        return ""
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Eliminar caracteres especiales y espacios múltiples
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

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
    # Normalizar tildes
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

def extraer_texto_imagen(ruta_imagen, recortar_region=True):
    """Extrae el texto de una imagen usando OCR
    
    Args:
        ruta_imagen: Ruta a la imagen
        recortar_region: Si True, recorta la región izquierda donde está el nombre (vertical)
    """
    if not OCR_AVAILABLE:
        return None
    
    try:
        # Abrir la imagen
        imagen = Image.open(ruta_imagen)
        ancho, alto = imagen.size
        
        # Recortar la región IZQUIERDA donde está el nombre (escrito verticalmente)
        # El nombre está en el lado izquierdo, ocupa aproximadamente 10-20% del ancho
        # y se extiende a lo largo de la altura de la carta
        # Ajustar para capturar mejor solo el nombre y evitar otros textos
        if recortar_region:
            x_inicio = int(ancho * 0.03)   # 3% desde izquierda (margen mínimo)
            x_fin = int(ancho * 0.22)      # 22% desde izquierda (cubre solo el nombre)
            y_inicio = int(alto * 0.15)    # 15% desde arriba (evitar coste y tipo superior)
            y_fin = int(alto * 0.75)       # 75% desde arriba (evitar texto inferior y habilidades)
            
            # Recortar la región izquierda
            region_nombre = imagen.crop((x_inicio, y_inicio, x_fin, y_fin))
            
            # Convertir a RGB si tiene transparencia o paleta
            if region_nombre.mode in ('RGBA', 'LA', 'P'):
                # Crear fondo blanco
                fondo = Image.new('RGB', region_nombre.size, (255, 255, 255))
                if region_nombre.mode == 'P':
                    region_nombre = region_nombre.convert('RGBA')
                fondo.paste(region_nombre, mask=region_nombre.split()[-1] if region_nombre.mode in ('RGBA', 'LA') else None)
                region_nombre = fondo
            
            # Convertir a escala de grises para mejor OCR
            if region_nombre.mode != 'L':
                region_nombre = region_nombre.convert('L')
            
            # Aumentar el tamaño para mejorar la precisión del OCR (texto más grande = mejor reconocimiento)
            factor_escala = 3
            nuevo_ancho = region_nombre.width * factor_escala
            nuevo_alto = region_nombre.height * factor_escala
            region_nombre = region_nombre.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
            
            # Rotar la imagen 90 grados en sentido antihorario para que el texto vertical sea horizontal
            # Esto mejora la precisión del OCR
            region_nombre = region_nombre.rotate(-90, expand=True)
            imagen_procesar = region_nombre
        else:
            imagen_procesar = imagen
        
        # Configurar Tesseract para español con configuración optimizada
        # Configuración para mejorar la precisión
        config_tesseract = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóúÑñ0123456789 '
        
        # Intentar con español primero, luego inglés
        texto = None
        for lang in ['spa', 'eng', 'spa+eng']:
            try:
                texto = pytesseract.image_to_string(imagen_procesar, lang=lang, config=config_tesseract)
                if texto and texto.strip():
                    break
            except:
                try:
                    # Si falla con la configuración, intentar sin whitelist
                    texto = pytesseract.image_to_string(imagen_procesar, lang=lang, config='--psm 6')
                    if texto and texto.strip():
                        break
                except:
                    continue
        
        if not texto or not texto.strip():
            # Si no funciona con idiomas específicos, intentar sin especificar
            try:
                texto = pytesseract.image_to_string(imagen_procesar, config='--psm 6')
            except:
                texto = pytesseract.image_to_string(imagen_procesar)
        
        return texto.strip() if texto else None
        
    except Exception as e:
        print(f"   ⚠️  Error al procesar imagen {ruta_imagen.name}: {e}")
        return None

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
    
    # Buscar archivos de imagen
    archivos_imagen = list(ruta_base.glob('*.png')) + list(ruta_base.glob('*.jpg'))
    
    if not archivos_imagen:
        return None
    
    # Intentar encontrar por ID o nombre de archivo
    id_carta = carta.get('id', '').lower()
    nombre_imagen = carta.get('imagen', '').lower()
    
    # Buscar por nombre de archivo del campo imagen
    if nombre_imagen:
        nombre_archivo = Path(nombre_imagen).name
        for archivo in archivos_imagen:
            if archivo.name.lower() == nombre_archivo.lower():
                return archivo
    
    # Buscar por números del ID
    numeros_id = re.findall(r'\d+', id_carta)
    for numero in numeros_id:
        for formato in [numero, numero.zfill(3), numero.zfill(4)]:
            for archivo in archivos_imagen:
                if formato in archivo.stem:
                    return archivo
    
    # Si no se encuentra, devolver el primer archivo (puede no ser correcto)
    return archivos_imagen[0] if archivos_imagen else None

def normalizar_texto_ocr(texto):
    """Normaliza texto de OCR, removiendo caracteres comunes de error"""
    if not texto:
        return ""
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Remover caracteres que OCR suele confundir
    # Reemplazar caracteres similares que OCR confunde
    reemplazos = {
        '0': 'o',  # Cero confundido con O
        '1': 'i',  # Uno confundido con I
        '5': 's',  # Cinco confundido con S
        '8': 'b',  # Ocho confundido con B
    }
    
    for old, new in reemplazos.items():
        texto = texto.replace(old, new)
    
    # Remover caracteres especiales y espacios múltiples
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def comparar_nombres(nombre_db, texto_ocr, umbral=0.5):
    """Compara el nombre de la BD con el texto extraído por OCR"""
    nombre_normalizado = normalizar_texto(nombre_db)
    texto_normalizado = normalizar_texto_ocr(texto_ocr)
    
    if not nombre_normalizado or not texto_normalizado:
        return False, 0.0
    
    # Verificar si el nombre está contenido en el texto OCR (sin espacios)
    nombre_sin_espacios = nombre_normalizado.replace(' ', '')
    texto_sin_espacios = texto_normalizado.replace(' ', '')
    
    if nombre_sin_espacios in texto_sin_espacios:
        return True, 1.0
    
    # Verificar si el nombre está contenido en el texto OCR (con espacios)
    if nombre_normalizado in texto_normalizado:
        return True, 1.0
    
    # Calcular similitud usando SequenceMatcher
    similitud = SequenceMatcher(None, nombre_normalizado, texto_normalizado).ratio()
    
    # También calcular similitud sin espacios
    similitud_sin_espacios = SequenceMatcher(None, nombre_sin_espacios, texto_sin_espacios).ratio()
    
    # Verificar si palabras clave del nombre están en el OCR
    palabras_nombre = [p for p in nombre_normalizado.split() if len(p) > 2]  # Solo palabras de más de 2 letras
    palabras_ocr = texto_normalizado.split()
    
    # Buscar coincidencias parciales de palabras (para manejar errores de OCR)
    palabras_coincidentes = 0
    for palabra_nombre in palabras_nombre:
        for palabra_ocr in palabras_ocr:
            # Si la palabra del nombre está contenida en la palabra OCR o viceversa
            if palabra_nombre in palabra_ocr or palabra_ocr in palabra_nombre:
                # Calcular similitud de la palabra
                sim_palabra = SequenceMatcher(None, palabra_nombre, palabra_ocr).ratio()
                if sim_palabra > 0.7:  # Si la similitud es alta
                    palabras_coincidentes += 1
                    break
    
    if len(palabras_nombre) > 0:
        ratio_palabras = palabras_coincidentes / len(palabras_nombre)
    else:
        ratio_palabras = 0.0
    
    # Combinar todas las métricas
    similitud_final = max(similitud, similitud_sin_espacios * 0.9, ratio_palabras * 0.85)
    
    return similitud_final >= umbral, similitud_final

def verificar_cartas(limite=None, edicion_filtro=None):
    """Verifica las cartas comparando imágenes con nombres"""
    if not OCR_AVAILABLE:
        print("❌ No se puede ejecutar sin las dependencias de OCR instaladas.")
        return
    
    # Conectar a la base de datos
    if not DB_NEW_PATH.exists():
        print(f"❌ No se encontró la base de datos en: {DB_NEW_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_NEW_PATH))
    cursor = conn.cursor()
    
    # Obtener cartas
    query = "SELECT id, nombre, edicion, raza, tipo, imagen FROM cartas WHERE 1=1"
    params = []
    
    if edicion_filtro:
        query += " AND edicion LIKE ?"
        params.append(f"%{edicion_filtro}%")
    
    query += " ORDER BY edicion, raza, tipo, nombre LIMIT ?"
    params.append(limite if limite else 10000)
    
    cursor.execute(query, params)
    cartas = cursor.fetchall()
    
    print(f"📋 Verificando {len(cartas)} cartas...")
    print("=" * 80)
    
    resultados = {
        'coincidencias': [],
        'discrepancias': [],
        'sin_imagen': [],
        'errores': []
    }
    
    for idx, (id_carta, nombre, edicion, raza, tipo, imagen) in enumerate(cartas, 1):
        carta = {
            'id': id_carta,
            'nombre': nombre,
            'edicion': edicion,
            'raza': raza,
            'tipo': tipo,
            'imagen': imagen
        }
        
        print(f"\n[{idx}/{len(cartas)}] {nombre} ({edicion})")
        
        # Buscar imagen
        ruta_imagen = encontrar_imagen_carta(carta)
        
        if not ruta_imagen:
            print(f"   ⚠️  No se encontró imagen")
            resultados['sin_imagen'].append(carta)
            continue
        
        print(f"   📷 Imagen: {ruta_imagen.name}")
        
        # Extraer texto de la imagen
        texto_ocr = extraer_texto_imagen(ruta_imagen)
        
        if not texto_ocr:
            print(f"   ⚠️  No se pudo extraer texto de la imagen")
            resultados['errores'].append({**carta, 'error': 'No se pudo extraer texto'})
            continue
        
        # Comparar nombres
        coincide, similitud = comparar_nombres(nombre, texto_ocr)
        
        resultado = {
            'carta': carta,
            'ruta_imagen': str(ruta_imagen),
            'texto_ocr': texto_ocr[:100],  # Primeros 100 caracteres
            'similitud': similitud
        }
        
        if coincide:
            print(f"   ✅ Coincide (similitud: {similitud:.2%})")
            print(f"   📝 Texto OCR: {texto_ocr[:80]}...")
            resultados['coincidencias'].append(resultado)
        else:
            print(f"   ❌ NO coincide (similitud: {similitud:.2%})")
            print(f"   📝 Texto OCR: {texto_ocr[:80]}...")
            resultados['discrepancias'].append(resultado)
    
    conn.close()
    
    # Mostrar resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)
    print(f"✅ Coincidencias: {len(resultados['coincidencias'])}")
    print(f"❌ Discrepancias: {len(resultados['discrepancias'])}")
    print(f"⚠️  Sin imagen: {len(resultados['sin_imagen'])}")
    print(f"🔴 Errores: {len(resultados['errores'])}")
    
    # Mostrar algunas discrepancias
    if resultados['discrepancias']:
        print("\n" + "=" * 80)
        print("❌ PRIMERAS 10 DISCREPANCIAS:")
        print("=" * 80)
        for disc in resultados['discrepancias'][:10]:
            carta = disc['carta']
            print(f"\n📇 {carta['nombre']} ({carta['edicion']})")
            print(f"   Similitud: {disc['similitud']:.2%}")
            print(f"   Texto OCR: {disc['texto_ocr']}")
    
    return resultados

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Verifica que las imágenes de cartas correspondan con sus nombres usando OCR')
    parser.add_argument('--limite', type=int, help='Número máximo de cartas a verificar')
    parser.add_argument('--edicion', type=str, help='Filtrar por edición específica')
    
    args = parser.parse_args()
    
    verificar_cartas(limite=args.limite, edicion_filtro=args.edicion)

