from flask import Flask, jsonify
import os
import socket
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db_connection():
    """Crear conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'flaskdb'),
            user=os.getenv('POSTGRES_USER', 'flaskuser'),
            password=os.getenv('POSTGRES_PASSWORD', 'flaskpass123'),
            port=int(os.getenv('DB_PORT', '5432'))
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def init_db():
    """Inicializar la base de datos con tabla de ejemplo"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    hostname VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            print("Base de datos inicializada correctamente")
        except Exception as e:
            print(f"Error inicializando base de datos: {e}")

# Inicializar DB al arrancar
init_db()

@app.route('/')
def home():
    hostname = socket.gethostname()
    
    # Registrar visita
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('INSERT INTO visits (hostname) VALUES (%s)', (hostname,))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error registrando visita: {e}")
    
    return jsonify({
        "message": "Flask con PostgreSQL en Kubernetes",
        "version": "2.0.0",
        "hostname": hostname
    })

@app.route('/health')
def health():
    # Verificar conexión a la base de datos
    conn = get_db_connection()
    db_status = "connected" if conn else "disconnected"
    if conn:
        conn.close()
    
    return jsonify({
        "status": "healthy",
        "database": db_status
    }), 200

@app.route('/visits')
def visits():
    """Mostrar todas las visitas registradas"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 50')
        visits = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            "total_visits": len(visits),
            "visits": visits
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats')
def stats():
    """Estadísticas de visitas por hostname"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT hostname, COUNT(*) as count 
            FROM visits 
            GROUP BY hostname 
            ORDER BY count DESC
        ''')
        stats = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({"stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    app.run(host='0.0.0.0', port=port)