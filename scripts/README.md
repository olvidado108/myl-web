# Script de Descarga de Cartas

Este script descarga y procesa cartas de Mitos y Leyendas desde la API pública.

## Características

- ✅ Descarga cartas desde la API
- ✅ Maneja duplicados inteligentemente (mismo nombre, diferentes artes)
- ✅ Limpia valores NaN en habilidades y otros campos
- ✅ Fusiona datos de cartas duplicadas (usa los datos más completos)
- ✅ Marca variantes con diferencias reales
- ✅ Descarga imágenes de las cartas
- ✅ Organiza cartas por edición
- ✅ Genera archivos JSON listos para usar en el proyecto

## Instalación

1. Asegúrate de tener Python 3.7+ instalado
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

```bash
python download_cards.py
```

El script:
1. Descargará todas las cartas de las ediciones configuradas
2. Procesará y limpiará los datos
3. Manejará duplicados automáticamente
4. Guardará todo en `server/data/cards/`

Para descargar imágenes también (puede tardar mucho tiempo):
```bash
python download_cards.py --imagenes
# o
python download_cards.py -i
```

## Configuración

Puedes editar las ediciones a descargar en el script:

```python
EDICIONES = ["edition1", "edition2", ...]  # Agrega más ediciones aquí
```

## Estructura de Salida

Las cartas se guardan en:
- `server/data/cards/edicion_*.json` - Cartas por edición
- `server/data/cards/todas_las_cartas.json` - Todas las cartas juntas

Las imágenes se guardan en:
- `public/images/cards/` - Imágenes descargadas

## Manejo de Duplicados

El script detecta cartas con el mismo nombre pero diferentes artes:

- **Si solo difieren en el arte**: Se guarda una carta principal y se marcan las variantes de arte
- **Si tienen diferencias en datos**: Se marca como variante con diferencias y se incluyen todas
- **Si una tiene datos y otra no**: Se usa la que tiene más datos completos

## Formato de Salida

Cada carta tiene este formato:

```json
{
  "id": "es559",
  "nombre": "Reynard el Zorro",
  "tipo": "Aliado",
  "coste": 2,
  "ataque": 2,
  "defensa": 2,
  "defensaMaxima": 2,
  "textoHabilidad": "...",
  "imagen": "ruta/a/imagen.png",
  "edicion": "es",
  "raza": "Caballero",
  "rareza": "Real",
  "esUnica": false,
  "esOroInicial": false,
  "tieneVariantes": true,
  "variantesArte": [...]
}
```

## Organización de Imágenes

Después de descargar las cartas, puedes organizar las imágenes en una estructura de carpetas jerárquica usando:

```bash
python organize_cards.py
```

Este script organiza las imágenes en la siguiente estructura:
```
public/images/cards_organized/
├── espada_sagrada/
│   ├── caballero/
│   │   ├── aliado/
│   │   └── arma/
│   ├── faerie/
│   │   └── aliado/
│   └── sin_raza/
│       ├── oro/
│       ├── talisman/
│       └── totem/
├── helenica/
├── hijos_de_daana/
└── dominios_de_ra/
```

La estructura es: **edición/raza/tipo/**

- **Edición**: espada_sagrada, helenica, hijos_de_daana, dominios_de_ra
- **Raza**: Caballero, Faerie, Dragón, etc. (o "sin_raza" para cartas sin raza)
- **Tipo**: Aliado, Oro, Talisman, Totem, Arma

El script también genera un archivo `indice_estructura.json` con estadísticas y la lista de todas las carpetas creadas.















