from app import create_app
from application.config import Config

app = create_app(Config)
from application.routes import *

if __name__ == "__main__":
    app.run(debug=True)
