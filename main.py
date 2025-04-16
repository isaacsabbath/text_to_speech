from app import app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # This allows Azure to assign the port
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # use Azure-assigned port
    app.run(host="0.0.0.0", port=port)
