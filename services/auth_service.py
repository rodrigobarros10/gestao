import bcrypt
from sqlalchemy import text

class AuthService:
    def __init__(self, db_loader):
        self.db = db_loader

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def authenticate_user(self, username, password):
        query = text("SELECT username, password_hash, role FROM public.usuarios WHERE username = :username")
        try:
            with self.db.get_engine().connect() as conn:
                result = conn.execute(query, {"username": username}).fetchone()
            if result and self.verify_password(password, result[1]):
                return {"username": result[0], "role": result[2]}
        except Exception as e:
            return None
        return None

    def create_user(self, username, password, role):
        hashed_pw = self.hash_password(password)
        query = text("INSERT INTO public.usuarios (username, password_hash, role) VALUES (:username, :password_hash, :role)")
        try:
            with self.db.get_engine().begin() as conn:
                conn.execute(query, {"username": username, "password_hash": hashed_pw, "role": role})
            return True, "Usuário criado com sucesso!"
        except Exception as e:
            return False, "Erro ao criar usuário. O nome de usuário pode já existir."