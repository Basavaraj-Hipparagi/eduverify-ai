import os
from app import app

# Ensure application runs in production mode
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # If on Windows, waitress can be used directly; otherwise app.run
    try:
        from waitress import serve
        print(f"Serving EduVerify AI via Waitress production server on port {port}...")
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        app.run(host="0.0.0.0", port=port)
