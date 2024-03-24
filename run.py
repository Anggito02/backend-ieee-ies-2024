import ngrok

from flaskr import create_app
from flask_cors import CORS

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

listener = ngrok.forward(5000, authtoken_from_env=True)

print("Inggress URL:", listener.url())

if __name__ == '__main__':
    app.run(debug=True)
