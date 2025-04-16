from app import app
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # This allows Azure to assign the port
    app.run(host="0.0.0.0", port=port)
