import random
from flask import Flask, render_template

app = Flask(__name__)

# Generate 400 tile items with sample data
TILES = []
COLORS = ["Red", "Blue", "Green", "Yellow", "White", "Black", "Gray", "Beige"]
SIZES = ["10x10", "15x15", "20x20", "30x30", "60x60"]

for i in range(1, 401):
    tile = {
        "id": i,
        "name": f"Tile {i}",
        "color": random.choice(COLORS),
        "size": random.choice(SIZES)
    }
    TILES.append(tile)

@app.route('/')
def catalog():
    return render_template('catalog.html', tiles=TILES)

if __name__ == '__main__':
    app.run(debug=True)
