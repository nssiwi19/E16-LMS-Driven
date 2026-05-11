import os
from e16_app import create_app
from e16_app import models  # noqa: F401

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", os.environ.get("PORT", 5000)))
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    debug_mode = os.environ.get("FLASK_DEBUG", "0") in ["1", "true", "True"]
    app.run(host=host, port=port, debug=debug_mode)
