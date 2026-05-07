class ControladorDoPaciente:
    def __init__(self, db_manager):
        self.db = db_manager

    def criar_paciente(self, nome, data_nascimento, responsavel, telefone, historico=""):
        query = '''
            INSERT INTO pacientes (nome, data_nascimento, responsavel, telefone, historico)
            VALUES (?, ?, ?, ?, ?)
        '''
        cursor = self.db.execute_query(query, (nome, data_nascimento, responsavel, telefone, historico))
        return cursor.lastrowid

    def listar_pacientes(self):
        query = 'SELECT * FROM pacientes ORDER BY nome'
        return self.db.fetch_all(query)

    def obter_paciente(self, paciente_id):
        query = 'SELECT * FROM pacientes WHERE id = ?'
        return self.db.fetch_one(query, (paciente_id,))

    def atualizar_paciente(self, paciente_id, nome, data_nascimento, responsavel, telefone, historico=""):
        query = '''
            UPDATE pacientes 
            SET nome = ?, data_nascimento = ?, responsavel = ?, telefone = ?, historico = ?
            WHERE id = ?
        '''
        self.db.execute_query(query, (nome, data_nascimento, responsavel, telefone, historico, paciente_id))

    def excluir_paciente(self, paciente_id):
        query = 'DELETE FROM pacientes WHERE id = ?'
        self.db.execute_query(query, (paciente_id,))
