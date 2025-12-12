# 📝 Notas de Implementación

Este documento contiene notas importantes sobre cómo implementar las reglas del juego en el código.

## 🔄 Cambios Necesarios en los Modelos

### GameState
✅ **Actualizado:**
- Cambiado sistema de "vida" por sistema de "mazo" (Castillo)
- Añadidas áreas: `lineaDefensa`, `lineaApoyo`, `reservaOro`
- Cambiado "mana" por "recursos" (generados por Oros)
- Fases actualizadas: `inicio`, `robo`, `preparacion`, `batalla`, `final`
- Método `verificarGanador()` ahora verifica mazo vacío

### Card
✅ **Actualizado:**
- Tipos: `Aliado`, `Talisman`, `Oro`, `Totem`, `Arma`
- Añadido `defensaMaxima` para restaurar defensa
- Añadido `girada` para estado de Aliados
- Métodos: `esAliado()`, `esOro()`, `recibirDano()`, `estaDestruido()`

## 🎯 Objetivo del Juego (Cambio Importante)

**ANTES (Incorrecto):**
- Victoria cuando vida <= 0

**AHORA (Correcto):**
- Victoria cuando mazo del oponente == 0 cartas
- El mazo se reduce cuando:
  - Se roba una carta (normal)
  - Se recibe daño directo al Castillo (descarta cartas del mazo)

## 📍 Áreas de Juego

Cada jugador tiene:
- `mazo`: Mazo Castillo (50 cartas)
- `mano`: Cartas en mano (máximo 8 después de la Fase de Robo)
- `lineaDefensa`: Aliados desplegados
- `lineaApoyo`: Tótems y Armas
- `reservaOro`: Oros que generan recursos
- `cementerio`: Cartas descartadas/destruidas

## 💰 Sistema de Recursos

**ANTES:**
- Maná que aumenta por turno (1, 2, 3... hasta 10)

**AHORA:**
- Recursos generados por cartas de **Oro**
- Los Oros se juegan en `reservaOro`
- Cada Oro genera recursos (típicamente 1 recurso por Oro)
- Los recursos se usan para jugar cartas

## 🔄 Fases del Turno

1. **inicio**: Enderezar cartas giradas, efectos de inicio
2. **robo**: Robar 1 carta del mazo (si está vacío, pierdes)
3. **preparacion**: Jugar cartas (Oros, Aliados, Tótems, Armas, Talismanes)
4. **batalla**: Aliados atacan o defienden
5. **final**: Efectos de final (el descarte se hace al final de la Fase de Robo, no aquí)

## ⚔️ Combate

### Ataque entre Aliados
```javascript
// Aliado A ataca a Aliado B
aliadoB.recibirDano(aliadoA.ataque);
aliadoA.recibirDano(aliadoB.ataque); // Contraataque

// Si defensa <= 0, va al cementerio
if (aliadoB.estaDestruido()) {
    moverAlCementerio(aliadoB);
}
```

### Ataque al Castillo
```javascript
// Si no hay Aliados defendiendo, ataca al Castillo
if (oponente.lineaDefensa.length === 0) {
    const dano = aliado.ataque;
    // Descartar cartas del mazo del oponente
    for (let i = 0; i < dano; i++) {
        if (oponente.mazo.length > 0) {
            oponente.cementerio.push(oponente.mazo.shift());
        }
    }
}
```

## 🃏 Tipos de Cartas y Dónde Van

- **Aliado** → `lineaDefensa`
- **Oro** → `reservaOro` (genera recursos)
- **Totem** → `lineaApoyo`
- **Arma** → `lineaApoyo` (se equipa a Aliado)
- **Talisman** → Se juega, resuelve efecto, va a `cementerio`

## 📋 Tareas Pendientes para Fase 1

### Actualizar Mazo
- [ ] Cambiar mazo de 30 a 50 cartas (Castillo)
- [ ] Añadir más cartas de tipo "Oro"
- [ ] Añadir cartas de tipo "Totem" y "Arma"
- [ ] **IMPORTANTE:** Implementar sistema de **Oro Inicial** obligatorio
  - [ ] Crear tipo de carta "Oro Inicial"
  - [ ] Validar que el mazo incluya 1 Oro Inicial
  - [ ] Al inicio de partida, colocar Oro Inicial en Reserva de Oro automáticamente
- [ ] Implementar validación de **número mínimo de Aliados**
- [ ] Implementar sistema de **formatos** (Racial Edición, Racial Soporte Libre)
- [ ] Implementar validación de **razas** y **ediciones** según formato

### Actualizar Lógica de Juego
- [ ] Implementar sistema de recursos (Oros)
- [ ] Cambiar condición de victoria (mazo vacío)
- [ ] Implementar descarte de cartas del mazo por daño
- [ ] Implementar límite de 8 cartas en mano (descartar después de robar si hay más de 8)
- [ ] Implementar fases: robo, preparacion, batalla, final

### Actualizar Combate
- [ ] Sistema de ataque entre Aliados
- [ ] Sistema de ataque al Castillo (descarta del mazo)
- [ ] Movimiento de Aliados destruidos al cementerio

### Sistema de Armas
- [ ] Implementar regla: **1 Arma por Aliado** (por defecto)
- [ ] Verificar habilidades especiales que permitan múltiples armas
- [ ] Validar al equipar: si el Aliado ya tiene arma y no tiene habilidad especial → bloquear

## 🎮 Simplificaciones Iniciales

Para la Fase 1 (prototipo en consola), podemos simplificar:

1. **Oros**: Cada Oro genera 1 recurso (sin variaciones)
2. **Oro Inicial**: Implementar como tipo especial de Oro que ya está en Reserva de Oro al inicio
3. **Talismanes**: Efectos básicos (daño, curación, robo)
4. **Tótems**: Efectos continuos simples
5. **Armas**: Aumentan ataque/defensa de Aliados (+1/+1 básico)
6. **Habilidades**: Implementar solo las más básicas
7. **Formatos**: Implementar validación básica (puede simplificarse inicialmente)

**IMPORTANTE - NO Simplificar:**
- ❌ Oro Inicial obligatorio (debe implementarse correctamente)
- ❌ Regla de 1 Arma por Aliado (debe implementarse correctamente)
- ❌ Validación de mazo de 50 cartas (debe implementarse correctamente)

Las mecánicas más complejas se añadirán en fases posteriores.

## 🆕 Reglas Críticas Añadidas

### Oro Inicial
- **OBLIGATORIO** en cada mazo
- Ya está en Reserva de Oro al inicio de la partida
- No se roba del mazo, ya está desplegado

### Número Mínimo de Aliados
- Validar que el mazo tenga suficientes Aliados
- Típicamente 15-20 Aliados mínimo

### Formatos de Juego
- **Racial Edición**: Raza + soporte solo de edición original
- **Racial Soporte Libre**: Raza + soporte de cualquier edición del formato

### Armas
- **1 Arma por Aliado** (regla general)
- Excepción: Aliados con habilidades especiales pueden tener más

---

**Última actualización:** 2025-01-27

