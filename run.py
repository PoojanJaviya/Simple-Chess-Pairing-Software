from chess_tournament import create_app

# Create the application instance using our factory
app = create_app()

if __name__ == '__main__':
    # Run the app in debug mode for development.
    # This gives you helpful error pages and auto-reloads the server on code changes.
    app.run(debug=True)

