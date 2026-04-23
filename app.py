from flask import Flask
from controllers.battle_controller import battle_bp

app = Flask(__name__)
app.register_blueprint(battle_bp)

if __name__ == "__main__":
    app.run(debug=True)