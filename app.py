import os

from e16_app import create_app
from e16_app import models  # noqa: F401

app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug, port=port)
