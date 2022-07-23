from app.server import app

if __name__ == '__main__':
    app.run(port=5000, debug=True)
else:
    print(f'Running as {__name__}')
