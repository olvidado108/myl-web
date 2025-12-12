# Mitos y Leyendas - Clon Web

Juego de cartas coleccionable (TCG) para navegador web, inspirado en "Mitos y Leyendas".

## Estado del Proyecto

**Fase 0: Preparación y Arquitectura** ✅ Completada

## Estructura del Proyecto

```
myl/
├── public/          # Cliente web (HTML, CSS, JS)
│   ├── index.html
│   └── client.js
├── server/          # Servidor Node.js
│   ├── server.js
│   ├── models/      # Modelos de datos
│   │   ├── Card.js
│   │   └── GameState.js
│   └── data/        # Datos del juego
│       └── deck.json
├── package.json
└── README.md
```

## Instalación

1. Instalar dependencias:
```bash
npm install
```

2. Iniciar el servidor:
```bash
npm start
```

3. Abrir en el navegador:
```
http://localhost:3000
```

## Próximos Pasos (Fase 1)

- Implementar lógica básica del juego en consola
- Sistema de barajar y repartir cartas
- Bucle de juego por turnos
- IA básica para oponente automático

## Nota Legal

Este es un proyecto personal/educativo. Para uso comercial se requeriría licencia de Fenix Entertainment.

