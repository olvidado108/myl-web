# Verificación de Imágenes de Cartas con OCR

Este script permite verificar que las imágenes de las cartas correspondan con el nombre correcto de la carta usando OCR (Optical Character Recognition).

## 📋 Requisitos

### 1. Instalar Tesseract OCR

**Windows:**
- Descargar e instalar desde: https://github.com/UB-Mannheim/tesseract/wiki
- Durante la instalación, asegúrate de instalar también el paquete de idioma español
- Nota la ruta de instalación (normalmente `C:\Program Files\Tesseract-OCR`)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-spa  # Para español
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Para idiomas adicionales
```

### 2. Instalar dependencias de Python

```bash
cd scripts
pip install -r requirements.txt
```

Esto instalará:
- `pytesseract` - Wrapper de Python para Tesseract
- `Pillow` - Para procesamiento de imágenes

### 3. Configurar Tesseract (solo si es necesario)

Si Tesseract no está en el PATH, puedes configurar la ruta manualmente editando el script y agregando:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# o
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux
```

## 🚀 Uso

### Verificar todas las cartas

```bash
python scripts/verify_card_images_ocr.py
```

### Verificar un número limitado de cartas

```bash
python scripts/verify_card_images_ocr.py --limite 50
```

### Verificar solo una edición específica

```bash
python scripts/verify_card_images_ocr.py --edicion "Dominios De Ra"
```

### Combinar opciones

```bash
python scripts/verify_card_images_ocr.py --limite 100 --edicion "Espada Sagrada"
```

## 📊 Resultados

El script mostrará:

1. **Coincidencias** ✅ - Imágenes que coinciden con el nombre de la carta
2. **Discrepancias** ❌ - Imágenes que NO coinciden con el nombre
3. **Sin imagen** ⚠️ - Cartas que no tienen imagen asociada
4. **Errores** 🔴 - Errores al procesar las imágenes

Para cada carta se muestra:
- El nombre de la carta
- La imagen encontrada
- El texto extraído por OCR
- El porcentaje de similitud con el nombre esperado

## ⚙️ Configuración

El script usa un umbral de similitud del 60% por defecto. Si quieres ajustarlo, edita la función `comparar_nombres()` en el script.

## 🔍 Notas

- El OCR puede no ser 100% preciso, especialmente con imágenes de baja calidad o fuentes decorativas
- El script normaliza los textos (minúsculas, sin acentos) para mejorar la comparación
- Si una carta no tiene imagen asociada, se reporta pero no se procesa
- El proceso puede ser lento dependiendo del número de cartas (aproximadamente 1-2 segundos por carta)

## 🐛 Solución de Problemas

### Error: "tesseract is not installed"

Asegúrate de que Tesseract esté instalado y en el PATH, o configura la ruta manualmente en el script.

### Error: "No module named 'pytesseract'"

Ejecuta: `pip install pytesseract pillow`

### OCR no detecta texto correctamente

- Verifica que las imágenes sean de buena calidad
- Asegúrate de tener instalado el paquete de idioma español para Tesseract
- Algunas fuentes decorativas pueden ser difíciles de reconocer




