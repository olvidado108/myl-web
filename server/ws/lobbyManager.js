/**
 * LobbyManager - Gestiona jugadores en lobby y emparejamiento
 * Usa socketId como clave para soportar múltiples sesiones por usuario.
 */
class LobbyManager {
    constructor() {
        this.players = new Map(); // socketId -> { userId, ... }
        this.matchmakingQueue = []; // [{ socketId, userId, deckId, gameMode, startedAt }]
        this.availableGames = new Map(); // gameId -> GameInfo
    }

    addPlayer(userId, socketId, playerInfo = {}) {
        this.players.set(socketId, {
            socketId,
            userId,
            gameId: null,
            lookingForGame: false,
            ...playerInfo,
            joinedAt: Date.now()
        });
        return this.getLobbyStats();
    }

    removePlayer(userId, socketId = null) {
        if (socketId) {
            this.players.delete(socketId);
            this.removeFromMatchmakingBySocket(socketId);
        } else {
            // eliminar todas las sesiones de ese user
            for (const [sid, player] of this.players.entries()) {
                if (player.userId === userId) {
                    this.players.delete(sid);
                    this.removeFromMatchmakingBySocket(sid);
                }
            }
        }
        return this.getLobbyStats();
    }

    addToMatchmaking(userId, socketId, matchmakingInfo) {
        if (!this.players.has(socketId)) {
            this.addPlayer(userId, socketId);
        }
        // limpiar si ya estaba en cola
        this.matchmakingQueue = this.matchmakingQueue.filter(e => e.socketId !== socketId);

        this.matchmakingQueue.push({
            socketId,
            userId,
            deckId: matchmakingInfo.deckId,
            gameMode: matchmakingInfo.gameMode || 'ranked',
            startedAt: Date.now()
        });

        const player = this.players.get(socketId);
        if (player) player.lookingForGame = true;

        return null; // matching se ejecuta externamente
    }

    tryMatchmaking() {
        if (this.matchmakingQueue.length < 2) return null;

        for (let i = 0; i < this.matchmakingQueue.length; i++) {
            for (let j = i + 1; j < this.matchmakingQueue.length; j++) {
                const a = this.matchmakingQueue[i];
                const b = this.matchmakingQueue[j];
                if (a.userId === b.userId) continue; // evitar misma persona
                if (a.gameMode !== b.gameMode) continue; // respetar competitivo/casual

                this.matchmakingQueue.splice(j, 1);
                this.matchmakingQueue.splice(i, 1);

                const pa = this.players.get(a.socketId);
                const pb = this.players.get(b.socketId);
                if (pa) pa.lookingForGame = false;
                if (pb) pb.lookingForGame = false;

                return {
                    player1: { userId: a.userId, socketId: a.socketId, deckId: a.deckId },
                    player2: { userId: b.userId, socketId: b.socketId, deckId: b.deckId }
                };
            }
        }
        return null;
    }

    removeFromMatchmakingBySocket(socketId) {
        this.matchmakingQueue = this.matchmakingQueue.filter(e => e.socketId !== socketId);
        const player = this.players.get(socketId);
        if (player) {
            player.lookingForGame = false;
        }
    }

    getLobbyStats() {
        return {
            playersOnline: this.players.size,
            playersInQueue: this.matchmakingQueue.length,
            availableGames: Array.from(this.availableGames.values())
        };
    }

    registerGame(gameId, gameInfo) {
        this.availableGames.set(gameId, {
            gameId,
            ...gameInfo,
            createdAt: Date.now()
        });
    }

    unregisterGame(gameId) {
        this.availableGames.delete(gameId);
    }

    getPlayerBySocket(socketId) {
        return this.players.get(socketId);
    }

    /**
     * Obtiene un jugador por userId (busca entre sockets activos)
     */
    getPlayer(userId) {
        for (const player of this.players.values()) {
            if (player.userId === userId) {
                return player;
            }
        }
        return null;
    }

    getGame(gameId) {
        return this.availableGames.get(gameId);
    }

    findGameByInviteCode(inviteCode) {
        for (const game of this.availableGames.values()) {
            if (game.inviteCode === inviteCode) {
                return game;
            }
        }
        return null;
    }
}

module.exports = new LobbyManager();

