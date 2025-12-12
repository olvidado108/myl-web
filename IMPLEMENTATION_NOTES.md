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
- `mano`: Cartas en mano (máximo 7 al final del turno)
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
5. **final**: Efectos de final, descartar si hay más de 7 cartas

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

### Actualizar Lógica de Juego
- [ ] Implementar sistema de recursos (Oros)
- [ ] Cambiar condición de victoria (mazo vacío)
- [ ] Implementar descarte de cartas del mazo por daño
- [ ] Implementar límite de 7 cartas en mano
- [ ] Implementar fases: robo, preparacion, batalla, final

### Actualizar Combate
- [ ] Sistema de ataque entre Aliados
- [ ] Sistema de ataque al Castillo (descarta del mazo)
- [ ] Movimiento de Aliados destruidos al cementerio

## 🎮 Simplificaciones Iniciales

Para la Fase 1 (prototipo en consola), podemos simplificar:

1. **Oros**: Cada Oro genera 1 recurso (sin variaciones)
2. **Talismanes**: Efectos básicos (daño, curación, robo)
3. **Tótems**: Efectos continuos simples
4. **Armas**: Aumentan ataque/defensa de Aliados (+1/+1 básico)
5. **Habilidades**: Implementar solo las más básicas

Las mecánicas más complejas se añadirán en fases posteriores.

---

**Última actualización:** 2025-01-27

