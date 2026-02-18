/**
 * AbilityExecutor - Ejecuta habilidades de cartas
 * 
 * Este módulo se encarga de ejecutar las habilidades de las cartas
 * durante el juego, respetando las reglas y el estado del juego.
 */

class AbilityExecutor {
    constructor(gameState) {
        this.gameState = gameState;
        this.effectHandlers = this._initializeEffectHandlers();
    }

    /**
     * Inicializa los manejadores de efectos
     */
    _initializeEffectHandlers() {
        return {
            modify_force: this._handleModifyForce.bind(this),
            draw_cards: this._handleDrawCards.bind(this),
            search: this._handleSearch.bind(this),
            destroy: this._handleDestroy.bind(this),
            exile: this._handleExile.bind(this),
            discard: this._handleDiscard.bind(this),
            shuffle: this._handleShuffle.bind(this),
            put_in_hand: this._handlePutInHand.bind(this),
            put_in_play: this._handlePutInPlay.bind(this),
            lose_ability: this._handleLoseAbility.bind(this),
            gain_ability: this._handleGainAbility.bind(this),
            counter: this._handleCounter.bind(this),
            damage: this._handleDamage.bind(this),
            prevent_damage: this._handlePreventDamage.bind(this)
        };
    }

    /**
     * Ejecuta una habilidad
     * @param {Object} ability - Habilidad a ejecutar (en formato JSON)
     * @param {Object} context - Contexto de ejecución (carta, jugador, etc.)
     * @returns {Object} Resultado de la ejecución
     */
    execute(ability, context) {
        const { card, player, target, triggeredBy } = context;

        // Validar condiciones
        if (!this._checkConditions(ability, context)) {
            return {
                success: false,
                reason: "Condiciones no cumplidas"
            };
        }

        // Validar costo (para habilidades activated)
        if (ability.type === "activated" && ability.cost) {
            if (!this._canPayCost(ability.cost, context)) {
                return {
                    success: false,
                    reason: "No se puede pagar el costo"
                };
            }
            this._payCost(ability.cost, context);
        }

        // Ejecutar efecto
        const result = this._executeEffect(ability.effect, context);

        return {
            success: true,
            result: result
        };
    }

    /**
     * Verifica si se cumplen las condiciones de la habilidad
     */
    _checkConditions(ability, context) {
        if (!ability.condition) {
            return true;
        }

        // TODO: Implementar lógica de condiciones
        // Por ahora, retornamos true
        return true;
    }

    /**
     * Verifica si se puede pagar el costo
     */
    _canPayCost(cost, context) {
        const { player } = context;

        switch (cost.type) {
            case "pay_resources":
                return this.gameState.getResources(player) >= cost.amount;
            
            case "discard":
                return this.gameState.getHandSize(player) >= cost.amount;
            
            case "destroy":
            case "exile":
                // Verificar que el objetivo existe y puede ser destruido/exiliado
                return true;
            
            default:
                return true;
        }
    }

    /**
     * Paga el costo de la habilidad
     */
    _payCost(cost, context) {
        const { player, card } = context;

        switch (cost.type) {
            case "pay_resources":
                this.gameState.spendResources(player, cost.amount);
                break;
            
            case "discard":
                this.gameState.discardCards(player, cost.amount);
                break;
            
            case "destroy":
                this.gameState.destroyCard(cost.target || card);
                break;
            
            case "exile":
                this.gameState.exileCard(cost.target || card);
                break;
        }
    }

    /**
     * Ejecuta un efecto
     */
    _executeEffect(effect, context) {
        const handler = this.effectHandlers[effect.type];
        if (!handler) {
            console.warn(`Efecto desconocido: ${effect.type}`);
            return { success: false, error: "Efecto desconocido" };
        }

        return handler(effect, context);
    }

    /**
     * Manejador: Modificar fuerza
     */
    _handleModifyForce(effect, context) {
        const targets = this._resolveTargets(effect.target, context);
        
        for (const target of targets) {
            if (target && target.fuerza !== undefined) {
                const modifier = effect.modifier;
                let newValue;

                switch (modifier.type) {
                    case "add":
                        newValue = target.fuerza + modifier.value;
                        break;
                    case "subtract":
                        newValue = target.fuerza - modifier.value;
                        break;
                    case "set":
                        newValue = modifier.value;
                        break;
                    default:
                        newValue = target.fuerza;
                }

                target.fuerza = Math.max(0, newValue);
            }
        }

        return { success: true, targets: targets.length };
    }

    /**
     * Manejador: Robar cartas
     */
    _handleDrawCards(effect, context) {
        const { player } = context;
        const amount = effect.amount || 1;
        
        const drawn = this.gameState.drawCards(player, amount);
        
        return {
            success: true,
            cardsDrawn: drawn.length
        };
    }

    /**
     * Manejador: Buscar en mazo
     */
    _handleSearch(effect, context) {
        const { player } = context;
        const targets = this._resolveTargets(effect.target, context);
        
        if (targets.length === 0) {
            return { success: false, reason: "No se encontraron cartas" };
        }

        // Por ahora, tomamos la primera carta que coincida
        const card = targets[0];
        
        switch (effect.action) {
            case "put_in_hand":
                this.gameState.moveCardToHand(card, player);
                break;
            case "put_in_play":
                this.gameState.putCardInPlay(card, player);
                break;
        }

        return { success: true, card: card };
    }

    /**
     * Manejador: Destruir
     */
    _handleDestroy(effect, context) {
        const targets = this._resolveTargets(effect.target, context);
        
        for (const target of targets) {
            this.gameState.destroyCard(target);
        }

        return { success: true, destroyed: targets.length };
    }

    /**
     * Manejador: Desterrar
     */
    _handleExile(effect, context) {
        const targets = this._resolveTargets(effect.target, context);
        
        for (const target of targets) {
            this.gameState.exileCard(target);
        }

        return { success: true, exiled: targets.length };
    }

    /**
     * Manejador: Descartar
     */
    _handleDiscard(effect, context) {
        const targetPlayer = effect.target === "opponent" 
            ? this.gameState.getOpponent(context.player)
            : context.player;
        
        const amount = effect.amount || 1;
        const location = effect.location || "deck";
        
        const discarded = this.gameState.discardCards(targetPlayer, amount, location);
        
        return { success: true, discarded: discarded.length };
    }

    /**
     * Manejador: Barajar
     */
    _handleShuffle(effect, context) {
        // TODO: Implementar
        return { success: true };
    }

    /**
     * Manejador: Poner en mano
     */
    _handlePutInHand(effect, context) {
        // TODO: Implementar
        return { success: true };
    }

    /**
     * Manejador: Poner en juego
     */
    _handlePutInPlay(effect, context) {
        // TODO: Implementar
        return { success: true };
    }

    /**
     * Manejador: Perder habilidad
     */
    _handleLoseAbility(effect, context) {
        // TODO: Implementar
        return { success: true };
    }

    /**
     * Manejador: Ganar habilidad
     */
    _handleGainAbility(effect, context) {
        // TODO: Implementar
        return { success: true };
    }

    /**
     * Manejador: Anular
     */
    _handleCounter(effect, context) {
        // TODO: Implementar
        return { success: true };
    }

    /**
     * Manejador: Daño
     */
    _handleDamage(effect, context) {
        // TODO: Implementar
        return { success: true };
    }

    /**
     * Manejador: Prevenir daño
     */
    _handlePreventDamage(effect, context) {
        // TODO: Implementar
        return { success: true };
    }

    /**
     * Resuelve los objetivos de un efecto
     */
    _resolveTargets(target, context) {
        if (typeof target === "string") {
            switch (target) {
                case "self":
                    return [context.card];
                case "controller":
                    return [context.player];
                case "opponent":
                    return [this.gameState.getOpponent(context.player)];
                case "triggered_card":
                    return [context.triggeredBy];
                default:
                    return [];
            }
        }

        if (target.type === "filter") {
            return this._resolveFilter(target.filter, context);
        }

        if (target.type === "reference") {
            return this._resolveReference(target.reference, context);
        }

        return [];
    }

    /**
     * Resuelve un filtro de objetivos
     */
    _resolveFilter(filter, context) {
        // TODO: Implementar lógica de filtrado completa
        const { player } = context;
        const cards = this.gameState.getCardsInPlay(player);
        
        return cards.filter(card => {
            if (filter.type && card.tipo !== filter.type) {
                return false;
            }
            if (filter.race && card.raza !== filter.race) {
                return false;
            }
            if (filter.controller === "self" && card.controller !== player) {
                return false;
            }
            if (filter.controller === "opponent" && card.controller === player) {
                return false;
            }
            return true;
        });
    }

    /**
     * Resuelve una referencia
     */
    _resolveReference(reference, context) {
        // TODO: Implementar sistema de referencias
        const parts = reference.split('.');
        let value = context;
        
        for (const part of parts) {
            if (value && value[part]) {
                value = value[part];
            } else {
                return null;
            }
        }
        
        return value;
    }
}

module.exports = AbilityExecutor;











