import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
from game import Game, Character

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the game
game = Game()

# Pre-place characters for debugging
def setup_initial_placements():
    initial_placements = {
        'A': [('A-P1', 0, 0), ('A-P2', 0, 1), ('A-P3', 0, 2), ('A-H1', 0, 3), ('A-H2', 0, 4)],
        'B': [('B-P1', 4, 0), ('B-P2', 4, 1), ('B-P3', 4, 2), ('B-H1', 4, 3), ('B-H2', 4, 4)]
    }

    for player, positions in initial_placements.items():
        for char_name, row, col in positions:
            character = Character(char_name, char_name[2], (row, col), player)
            game.board.place_character(character)

setup_initial_placements()

@app.get("/")
async def get():
    with open("static/index.html", "r") as file:
        return HTMLResponse(content=file.read(), media_type="text/html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"action": "update", "payload": game.board.grid}))

    game_started = False

    while not game.game_over:
        try:
            data = await websocket.receive_text()
            print(f"Received: {data}")  # Debugging
            data = json.loads(data)

            if data["action"] == "start_game":
                game_started = True
                await websocket.send_text(json.dumps({"action": "start", "payload": "A"}))
                await websocket.send_text(json.dumps({"action": "status", "payload": game.get_status()}))

            elif data["action"] == "select_character":
                if game_started:
                    char_name = data["char_name"]
                    character = game.board.get_character_by_name(char_name)
                    if character and character.player == game.turn:
                        possible_moves = character.get_possible_moves(game.board)
                        await websocket.send_text(json.dumps({"action": "show_moves", "payload": possible_moves}))
                    else:
                        await websocket.send_text(json.dumps({"action": "invalid", "payload": "Invalid character selection or not your turn"}))
                else:
                    await websocket.send_text(json.dumps({"action": "invalid", "payload": "Game not started"}))

            elif data["action"] == "move_character":
                if game_started:
                    char_name, move = data["char_name"], tuple(data["move"])  # Convert move to a tuple
                    final_position = game.make_move(char_name, move)
                    if final_position:
                        winner = game.check_game_over()
                        if winner:
                            await websocket.send_text(json.dumps({"action": "gameover", "payload": f"Player {winner} wins!"}))
                        else:
                            await websocket.send_text(json.dumps({"action": "turn", "payload": game.turn}))
                        await websocket.send_text(json.dumps({"action": "update", "payload": game.board.grid}))
                        await websocket.send_text(json.dumps({"action": "status", "payload": game.get_status()}))
                    else:
                        await websocket.send_text(json.dumps({"action": "invalid", "payload": "Invalid move"}))
                else:
                    await websocket.send_text(json.dumps({"action": "invalid", "payload": "Game not started"}))
        except Exception as e:
            print(f"Error: {e}")
            break

    await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
