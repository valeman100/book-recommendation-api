from app import create_app, list_routes

app = create_app()
list_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
