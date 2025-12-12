# 📜 Reglas del Juego - Mitos y Leyendas

Este documento contiene las reglas oficiales de "Mitos y Leyendas" que deben seguirse en la implementación del juego.

## 🎯 Objetivo del Juego

El objetivo es **reducir el mazo del oponente a cero cartas**, lo que simboliza la destrucción de su Castillo. Cada jugador representa un reino que debe proteger su Castillo (mazo de 50 cartas).

**Condición de Victoria:** El jugador gana cuando el mazo del oponente queda vacío (0 cartas).

## 🏰 Construcción del Mazo (Castillo)

- El mazo, llamado **"Castillo"**, debe contener **exactamente 50 cartas**.
- Se permite hasta **3 copias de cada carta**, excepto las cartas únicas, de las cuales solo se puede incluir **1 copia**.
- El mazo debe estar barajado antes de comenzar la partida.

### ⚠️ Reglas Obligatorias de Construcción

1. **Oro Inicial Obligatorio:**
   - **OBLIGATORIO:** El mazo debe incluir **exactamente 1 carta de "Oro Inicial"**.
   - Este Oro Inicial es una carta especial que debe estar en el mazo.
   - Al inicio de la partida, **el Oro Inicial ya se encuentra en la Reserva de Oro** (no se roba, ya está desplegado).
   - Esto garantiza que el jugador tenga recursos desde el primer turno.

2. **Número Mínimo de Aliados:**
   - El mazo debe contener un **número mínimo de Aliados** (cantidad específica según formato).
   - Esta regla asegura que el jugador tenga suficientes unidades para combatir.

3. **Restricciones por Formato:**
   - Dependiendo del formato elegido, pueden aplicarse restricciones adicionales sobre razas, ediciones permitidas, etc.

## 🃏 Tipos de Cartas

### 1. **Aliados**
- Criaturas que luchan por el jugador.
- Se despliegan en la **Línea de Defensa**.
- Tienen **Ataque** y **Defensa**.
- Pueden atacar al oponente o defender.

### 2. **Talismanes** (Hechizos)
- Hechizos de un solo uso con efectos inmediatos.
- Se juegan y se resuelven sus efectos, luego van al cementerio.
- No permanecen en el campo.

### 3. **Oros** (Recursos)
- Cartas que proporcionan recursos para jugar otras cartas.
- Se colocan en la **Reserva de Oro**.
- Generan recursos (equivalente al "maná" en otros juegos).
- Permiten jugar cartas con mayor coste.

### 4. **Tótems** (Permanentes)
- Permanentes que otorgan efectos continuos.
- Se despliegan en la **Línea de Apoyo**.
- Permanecen en el campo hasta ser destruidos.

### 5. **Armas** (Equipamientos)
- Equipamientos que mejoran las habilidades de los Aliados.
- Se colocan en la **Línea de Apoyo**.
- Se equipan a Aliados para mejorar sus estadísticas.
- **Regla de Equipamiento:** Un Aliado solo puede tener **1 Arma equipada** a la vez.
- **Excepción:** Si un Aliado tiene una habilidad especial que indique lo contrario (ej: "Puede equipar múltiples armas"), entonces puede equipar más de una.

## 📍 Áreas de Juego

### **Mazo Castillo**
- El mazo principal de 50 cartas.
- Se roba una carta al inicio de cada turno.
- Si se queda sin cartas, el jugador pierde.

### **Cementerio**
- Zona donde se colocan las cartas descartadas o destruidas.
- Las cartas van al cementerio cuando:
  - Un Aliado es destruido (defensa <= 0)
  - Un Talismán se resuelve
  - Una carta es descartada

### **Línea de Defensa**
- Área donde se despliegan los **Aliados** para defender el Castillo.
- Los Aliados pueden atacar o defender desde aquí.

### **Línea de Apoyo**
- Zona para **Tótems** y **Armas** que brindan soporte a los Aliados.
- Los Tótems otorgan efectos continuos.
- Las Armas se equipan a Aliados.

### **Reserva de Oro**
- Lugar donde se colocan las cartas de **Oro** para generar recursos.
- Los Oros generan recursos que permiten jugar cartas.

### **Mano**
- Cartas que el jugador tiene disponibles para jugar.
- Máximo de cartas en mano: **8 cartas** (si tienes más después de robar, debes descartar hasta tener 8).

## 🔄 Fases del Turno

Cada turno se divide en las siguientes fases:

### 1. **Fase de Inicio**
- Se enderezan las cartas giradas (si las hay).
- Se resuelven efectos que ocurren al inicio del turno.
- **IMPORTANTE:** Al inicio de la partida (primer turno del primer jugador), el **Oro Inicial ya está en la Reserva de Oro** (no se roba, ya está desplegado).
- Se prepara el turno.

### 2. **Fase de Robo**
- El jugador **roba una carta** del Mazo Castillo.
- Si el mazo está vacío, el jugador pierde inmediatamente.
- **Al final de esta fase**, si el jugador tiene **más de 8 cartas en mano**, debe **descartar cartas hasta tener exactamente 8 cartas**.

### 3. **Fase de Preparación**
- Se pueden jugar cartas de **Oro** para generar recursos.
- Se pueden jugar cartas de **Tótems** y **Armas** en la Línea de Apoyo.
- Se pueden jugar **Aliados** en la Línea de Defensa.
- Se pueden jugar **Talismanes** (hechizos) con efectos inmediatos.
- El jugador puede jugar tantas cartas como pueda pagar.

### 4. **Fase de Batalla**
- Los **Aliados** pueden atacar:
  - A otros Aliados del oponente en la Línea de Defensa.
  - Directamente al Castillo del oponente (si no hay Aliados defendiendo).
- Los Aliados pueden defender bloqueando ataques.
- Se resuelven los combates:
  - Si un Aliado ataca a otro, ambos reciben daño igual al ataque del otro.
  - Si un Aliado ataca directamente al Castillo, el oponente descarta cartas del mazo.
- Los Aliados con defensa <= 0 son destruidos y van al cementerio.

### 5. **Fase Final**
- Se resuelven efectos que ocurren al final del turno.
- Se cambia al turno del oponente.

## ⚔️ Mecánicas de Combate

### Ataque entre Aliados
- Cuando un Aliado ataca a otro:
  - Ambos reciben daño igual al **ataque** del oponente.
  - Se resta el daño de la **defensa** de cada Aliado.
  - Si la defensa llega a 0 o menos, el Aliado es destruido.

### Ataque al Castillo
- Si un Aliado ataca directamente al Castillo (sin Aliados defendiendo):
  - El oponente debe **descartar cartas del mazo** (equivalente al daño recibido).
  - Por ejemplo: Si un Aliado con 3 de ataque ataca al Castillo, el oponente descarta 3 cartas de su mazo.

### Defensa
- Los Aliados pueden **bloquear** ataques dirigidos al Castillo.
- Si hay Aliados en la Línea de Defensa, el atacante debe elegir:
  - Atacar a un Aliado específico.
  - O intentar atacar al Castillo (si las reglas lo permiten).

## 💰 Sistema de Recursos (Oros)

- Las cartas de **Oro** se juegan en la **Reserva de Oro**.
- Cada Oro genera recursos que permiten jugar cartas.
- El coste de las cartas se paga con recursos de los Oros.
- Los recursos se acumulan y se pueden usar en el mismo turno.

### 🟡 Oro Inicial

- **Obligatorio:** Cada mazo debe incluir **1 Oro Inicial**.
- **Inicio de Partida:** El Oro Inicial **ya está desplegado en la Reserva de Oro** al comenzar la partida.
- **No se roba:** El Oro Inicial no forma parte de las 50 cartas que se roban del mazo, ya está en juego desde el inicio.
- **Primer Recurso:** Esto garantiza que el jugador tenga al menos 1 recurso disponible desde su primer turno.

## 🎴 Habilidades de las Cartas

Muchas cartas poseen **habilidades especiales** que pueden activarse bajo ciertas condiciones:

- **Efectos Dirigidos:** Afectan a cartas específicas.
- **Efectos Universales:** Afectan a todas las cartas de un tipo o a todos los jugadores.
- **Efectos Continuos:** Permanecen activos mientras la carta esté en el campo.
- **Efectos de Activación:** Se activan cuando se cumplen ciertas condiciones.

## 📋 Reglas Adicionales

### Límite de Cartas en Mano
- Máximo **8 cartas** en mano al final de la Fase de Robo.
- **IMPORTANTE:** El descarte ocurre **al final de la Fase de Robo**, después de haber robado la carta.
- Si al final de la Fase de Robo tienes más de 8 cartas, debes descartar hasta tener exactamente 8 cartas.
- Durante el resto del turno y el turno del oponente, puedes tener temporalmente más de 8 cartas en mano (no hay descarte obligatorio fuera de la Fase de Robo).

### Robo de Cartas
- Se roba **1 carta** al inicio de cada turno (Fase de Robo).
- Si el mazo está vacío al intentar robar, el jugador pierde.

### Condición de Derrota
- El jugador pierde cuando su **mazo queda vacío** (0 cartas).
- Esto puede ocurrir por:
  - Robar cartas normalmente.
  - Ataques directos al Castillo que descartan cartas del mazo.

## 🎭 Formatos de Juego

Existen diferentes formatos que determinan qué cartas pueden usarse y cómo construir el mazo. Los formatos principales son:

### 1. **Formato Racial Edición**
- **Regla Principal:** Debes elegir **una raza** disponible en una edición del formato elegido.
- **Restricción de Cartas:** Solo puedes usar:
  - **Aliados** de la raza elegida.
  - **Cartas de soporte** (Talismanes, Oros, Tótems, Armas) **únicamente de la edición original** de esa raza o de sus productos derivados.
- **Ejemplo:** Si eliges jugar formato "Primer Bloque Extendido" y seleccionas la raza **Olímpico**, entonces:
  - Solo puedes usar Aliados de raza Olímpico.
  - Solo puedes usar cartas de soporte de la edición **Helénica** (edición original de Olímpico) o de sus productos derivados.

### 2. **Formato Racial o Racial Soporte Libre**
- **Regla Principal:** Debes elegir **una raza** disponible en una edición del formato elegido.
- **Restricción de Cartas:** Puedes usar:
  - **Aliados** de la raza elegida.
  - **Cartas de soporte** (Talismanes, Oros, Tótems, Armas) de **cualquier edición** que esté permitida en el formato.
- **Diferencia con Racial Edición:** En este formato, las cartas de soporte pueden venir de cualquier edición del formato, no solo de la edición original de la raza.

### 📋 Razas Comunes en Mitos y Leyendas

Algunas razas disponibles (pueden variar según formato):
- **Olímpico** (edición Helénica)
- **Nórdico** (edición Nórdica)
- **Egipcio** (edición Egipcia)
- **Celta** (edición Celta)
- **Oriental** (edición Oriental)
- **Maya** (edición Maya)
- Y muchas más según las ediciones disponibles.

### ⚙️ Validación de Mazos por Formato

Al construir un mazo, el sistema debe validar:
1. ✅ Tiene exactamente 50 cartas.
2. ✅ Incluye 1 Oro Inicial obligatorio.
3. ✅ Cumple con el número mínimo de Aliados requerido.
4. ✅ Respeta las restricciones de raza del formato elegido.
5. ✅ Las cartas de soporte cumplen con las restricciones del formato (Racial Edición vs Racial Soporte Libre).
6. ✅ No excede el límite de copias (3 copias normales, 1 copia única).

## 🔗 Referencias

- [Manual de Mitos y Leyendas](https://casamyl.cl/blogs/myl/manual-de-hijos-de-daana-guia-completa-para-jugar-mitos-y-leyendas)
- [Reglas del Juego - Wiki](https://myl.fandom.com/es/wiki/Reglas_del_Juego)
- [Video: Reglas Completas](https://www.youtube.com/watch?v=HX2gD6gXRIw)

---

**Nota:** Estas reglas están basadas en la versión oficial de "Mitos y Leyendas". Para este proyecto educativo, algunas mecánicas pueden simplificarse inicialmente y expandirse en fases posteriores.

