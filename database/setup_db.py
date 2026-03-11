import sys, os
import bcrypt
from sqlalchemy import create_engine, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DEFAULT_DB_CONFIG

def setup_database():
    db_url = f"postgresql+psycopg2://{DEFAULT_DB_CONFIG['user']}:{DEFAULT_DB_CONFIG['password']}@{DEFAULT_DB_CONFIG['host']}:{DEFAULT_DB_CONFIG['port']}/{DEFAULT_DB_CONFIG['dbname']}"
    engine = create_engine(db_url)
    
    with engine.begin() as conn:
        print("Criando tabela de usuários...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        result = conn.execute(text("SELECT * FROM public.usuarios WHERE username = 'admin'")).fetchone()
        if not result:
            hashed_pw = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            conn.execute(text(f"INSERT INTO public.usuarios (username, password_hash, role) VALUES ('admin', '{hashed_pw}', 'admin')"))
            print("Admin criado! (User: admin / Pass: admin)")
        else:
            print("Usuário admin já existe.")

if __name__ == "__main__":
    setup_database()