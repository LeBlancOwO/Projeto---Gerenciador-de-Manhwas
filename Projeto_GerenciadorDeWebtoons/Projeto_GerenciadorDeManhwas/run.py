from app import create_app

# Ponto de entrada que inicializa o servidor Flask
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)