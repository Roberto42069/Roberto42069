from app import app

# Export app for gunicorn
# gunicorn will use: gunicorn main:app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)