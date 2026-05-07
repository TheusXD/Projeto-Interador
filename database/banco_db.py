import sqlite3
import os

class GerenciaDB:
    def __init__(self, db_name="pediatria.db"):
        self.db_name = db_name
        self._create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de Pacientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data_nascimento TEXT NOT NULL,
                    responsavel TEXT NOT NULL,
                    telefone TEXT,
                    historico TEXT
                )
            ''')
            
            # Tabela de Consultas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consultas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    data_consulta TEXT NOT NULL,
                    observacoes TEXT,
                    diagnostico TEXT,
                    prescricao TEXT,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de Vacinas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vacinas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    nome_vacina TEXT NOT NULL,
                    data_aplicada TEXT,
                    pendente BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de Crescimento
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crescimento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    peso REAL,
                    altura REAL,
                    data_medicao TEXT NOT NULL,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de Agendamentos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agendamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER,
                    data_hora TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    descricao TEXT,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE SET NULL
                )
            ''')
            
            # Tabela de Comunicação (Anotações/Mensagens)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comunicacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    mensagem TEXT NOT NULL,
                    data TEXT NOT NULL,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()

    def execute_query(self, query, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def fetch_all(self, query, params=()):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row # Retorna resultados como dicionários
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query, params=()):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
