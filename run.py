from appContents import app, db, open_browser
from appContents.websocket import WebSocketServerThread
import os;
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Ensure database is created
    with app.app_context():
        db.create_all()
        

    # Start the WebSocket thread
    websocket_thread = WebSocketServerThread()
    websocket_thread.start()

    # Open the browser and run the Flask app
    open_browser()
    app.run(host=os.getenv("FLASK_IP_ADDRESS"), port=os.getenv("FLASK_PORT"), debug=True, use_reloader=False)

    # Wait for threads to finish
    websocket_thread.join()
    
    
