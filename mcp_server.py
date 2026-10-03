from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).parent
QUESTION_BANK_FILE = BASE_DIR / "data" / "question_bank.json"
DATABASE_FILE = BASE_DIR / "data" / "question_bank.db"


def initialize_database():
    """Create a small SQLite database for connector access."""
    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connector_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def read_file_data():
    """Read the existing question-bank JSON file."""
    try:
        with open(QUESTION_BANK_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Question bank file not found."
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Invalid JSON in question bank."
        }


def access_sqlite():
    """Read connector information from SQLite."""
    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO connector_log (action, status)
        VALUES (?, ?)
    """, ("sqlite_access", "success"))

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*) FROM connector_log
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return {
        "status": "success",
        "database": "question_bank.db",
        "connector_log_entries": count
    }


def mock_api_response():
    """Simulate an external API response."""
    return {
        "status": "success",
        "source": "mock-api",
        "message": "External question-paper service connected.",
        "service": "Question Paper OBE API"
    }


class MCPStyleConnector(BaseHTTPRequestHandler):

    def send_json(self, data):
        """Send a JSON response."""
        response = json.dumps(data, indent=2)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(response.encode("utf-8"))

    def do_GET(self):

        if self.path == "/file":
            self.send_json({
                "connector": "file",
                "data": read_file_data()
            })

        elif self.path == "/sqlite":
            self.send_json({
                "connector": "sqlite",
                "data": access_sqlite()
            })

        elif self.path == "/api":
            self.send_json({
                "connector": "api",
                "data": mock_api_response()
            })

        elif self.path == "/":
            self.send_json({
                "server": "Question Paper MCP-Style Connector",
                "status": "running",
                "available_connectors": [
                    "/file",
                    "/sqlite",
                    "/api"
                ]
            })

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":

    initialize_database()

    server = HTTPServer(
        ("localhost", 8000),
        MCPStyleConnector
    )

    print("===== MCP-STYLE CONNECTOR =====")
    print("Server running at http://localhost:8000")
    print("Available connectors:")
    print("1. File   -> http://localhost:8000/file")
    print("2. SQLite -> http://localhost:8000/sqlite")
    print("3. API    -> http://localhost:8000/api")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    finally:
        server.server_close()