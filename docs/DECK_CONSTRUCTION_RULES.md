# 🏗️ Reglas de Construcción de Mazos

Este documento detalla las reglas específicas para construir mazos válidos en "Mitos y Leyendas".

## 📏 Reglas Básicas de Construcción

### Tamaño del Mazo
- **Exactamente 50 cartas** en el mazo (Castillo).
- No más, no menos.

### Límites de Copias
- **Cartas normales:** Máximo **3 copias** de cada carta.
- **Cartas únicas:** Máximo **1 copia** de cada carta única.

## ⚠️ Reglas Obligatorias

### 1. Oro Inicial Obligatorio

**REQUISITO OBLIGATORIO:**
- El mazo **DEBE** incluir exactamente **1 carta de "Oro Inicial"**.
- El Oro Inicial es una carta especial que no cuenta como una de las 50 cartas normales del mazo.
- **Al inicio de la partida**, el Oro Inicial **ya está desplegado en la Reserva de Oro** del jugador.
- El jugador **NO roba** el Oro Inicial, ya está en juego desde el comienzo.

**Propósito:**
- Garantiza que el jugador tenga recursos desde el primer turno.
- Permite jugar cartas de coste 1 en el primer turno.

**Ejemplo:**
```
Mazo del Jugador: 50 cartas
Oro Inicial: 1 carta (ya en Reserva de Oro al inicio)
Total: 51 cartas relacionadas con el jugador
```

### 2. Número Mínimo de Aliados

**REQUISITO OBLIGATORIO:**
- El mazo debe contener un **número mínimo de Aliados**.
- El número exacto puede variar según el formato, pero típicamente es:
  - **Mínimo 15-20 Aliados** (dependiendo del formato y reglas específicas).
- Esta regla asegura que el jugador tenga suficientes unidades para combatir.

**Validación:**
- Al construir el mazo, el sistema debe verificar que se cumple este mínimo.
- Si no se cumple, el mazo no es válido.

## 🎭 Formatos de Construcción

### Formato 1: **Racial Edición**

**Descripción:**
Debes elegir una de las razas disponibles en una edición del formato elegido y complementarla **solo con cartas de soporte de su edición original**.

**Reglas:**
1. **Elegir una raza** de las disponibles en el formato.
2. **Aliados:** Solo puedes usar Aliados de la raza elegida.
3. **Cartas de Soporte:** Solo puedes usar cartas de soporte (Talismanes, Oros, Tótems, Armas) de:
   - La **edición original** de esa raza.
   - **Productos derivados** de esa edición.

**Ejemplo:**
```
Formato: Primer Bloque Extendido
Raza elegida: Olímpico
Edición original: Helénica

✅ Permitido:
- Aliados: Solo Olímpicos
- Soporte: Solo de edición Helénica o productos derivados

❌ No permitido:
- Aliados de otras razas
- Soporte de otras ediciones
```

### Formato 2: **Racial o Racial Soporte Libre**

**Descripción:**
Debes elegir una de las razas disponibles en una edición del formato elegido y complementarla con cartas de **cualquier edición del formato**.

**Reglas:**
1. **Elegir una raza** de las disponibles en el formato.
2. **Aliados:** Solo puedes usar Aliados de la raza elegida.
3. **Cartas de Soporte:** Puedes usar cartas de soporte de **cualquier edición** que esté permitida en el formato.

**Ejemplo:**
```
Formato: Primer Bloque Extendido
Raza elegida: Olímpico

✅ Permitido:
- Aliados: Solo Olímpicos
- Soporte: De cualquier edición del Primer Bloque Extendido

❌ No permitido:
- Aliados de otras razas
```

**Diferencia con Racial Edición:**
- En **Racial Edición**: Soporte solo de la edición original de la raza.
- En **Racial Soporte Libre**: Soporte de cualquier edición del formato.

## 🛡️ Reglas de Equipamiento

### Armas y Aliados

**Regla General:**
- Un Aliado solo puede tener **1 Arma equipada** a la vez.

**Excepción:**
- Si un Aliado tiene una **habilidad especial** que indique lo contrario, puede equipar múltiples armas.
- Ejemplos de habilidades que permiten múltiples armas:
  - "Puede equipar múltiples armas"
  - "No tiene límite de armas"
  - "Puede tener hasta X armas"

**Validación:**
- Al intentar equipar un Arma a un Aliado que ya tiene una:
  - Si el Aliado NO tiene habilidad especial → **Bloquear** la acción.
  - Si el Aliado SÍ tiene habilidad especial → **Permitir** la acción.

## ✅ Checklist de Validación de Mazo

Un mazo es válido si cumple TODOS estos requisitos:

- [ ] Tiene exactamente **50 cartas** en el mazo.
- [ ] Incluye exactamente **1 Oro Inicial** (obligatorio).
- [ ] Tiene al menos el **número mínimo de Aliados** requerido.
- [ ] No excede **3 copias** de cartas normales.
- [ ] No excede **1 copia** de cartas únicas.
- [ ] Si es formato **Racial Edición**:
  - [ ] Todos los Aliados son de la misma raza.
  - [ ] Todas las cartas de soporte son de la edición original de la raza.
- [ ] Si es formato **Racial Soporte Libre**:
  - [ ] Todos los Aliados son de la misma raza.
  - [ ] Las cartas de soporte son de ediciones permitidas en el formato.
- [ ] Todas las cartas están permitidas en el formato elegido.
- [ ] No incluye cartas prohibidas o restringidas del formato.

## 🔧 Implementación Técnica

### Estructura de Datos para Validación

```javascript
{
  formato: "Racial Edición" | "Racial Soporte Libre",
  raza: "Olímpico" | "Nórdico" | ...,
  edicionOriginal: "Helénica" | ...,
  cartas: [
    { id, nombre, tipo, raza, edicion, ... }
  ],
  oroInicial: { id, nombre, tipo: "Oro Inicial" },
  tieneOroInicial: true,
  numeroAliados: 20,
  minimoAliados: 15,
  esValido: true
}
```

### Funciones de Validación Necesarias

1. `validarTamañoMazo(mazo)` - Verifica que tenga 50 cartas
2. `validarOroInicial(mazo)` - Verifica que tenga 1 Oro Inicial
3. `validarMinimoAliados(mazo, minimo)` - Verifica número mínimo de Aliados
4. `validarCopias(mazo)` - Verifica límites de copias
5. `validarRaza(mazo, formato, raza)` - Valida restricciones de raza
6. `validarEdiciones(mazo, formato, raza)` - Valida restricciones de ediciones
7. `validarCartasProhibidas(mazo, formato)` - Verifica cartas prohibidas

---

**Última actualización:** 2025-01-27






