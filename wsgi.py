from app.server import app

if __name__ == '__main__':
    try:
        app.run(port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f'Error while running app: {e}')
else:
    print(f'Running as {__name__}')
