class ControladorDasConsultas:
    def __init__(self, db_manager):
        self.db = db_manager

    def criar_consulta(self, paciente_id, data_consulta, observacoes, diagnostico, prescricao):
        query = '''
            INSERT INTO consultas (paciente_id, data_consulta, observacoes, diagnostico, prescricao)
            VALUES (?, ?, ?, ?, ?)
        '''
        cursor = self.db.execute_query(query, (paciente_id, data_consulta, observacoes, diagnostico, prescricao))
        return cursor.lastrowid

    def listar_consultas_paciente(self, paciente_id):
        query = 'SELECT * FROM consultas WHERE paciente_id = ? ORDER BY data_consulta DESC'
        return self.db.fetch_all(query, (paciente_id,))

    def excluir_consulta(self, consulta_id):
        query = 'DELETE FROM consultas WHERE id = ?'
        self.db.execute_query(query, (consulta_id,))

class ControlaAsVacinas:
    def __init__(self, db_manager):
        self.db = db_manager

    def registrar_vacina(self, paciente_id, nome_vacina, data_aplicada=None, pendente=True):
        query = '''
            INSERT INTO vacinas (paciente_id, nome_vacina, data_aplicada, pendente)
            VALUES (?, ?, ?, ?)
        '''
        cursor = self.db.execute_query(query, (paciente_id, nome_vacina, data_aplicada, int(pendente)))
        return cursor.lastrowid

    def listar_vacinas_paciente(self, paciente_id):
        query = 'SELECT * FROM vacinas WHERE paciente_id = ? ORDER BY pendente DESC, data_aplicada DESC'
        return self.db.fetch_all(query, (paciente_id,))

    def atualizar_status_vacina(self, vacina_id, data_aplicada, pendente):
        query = '''
            UPDATE vacinas 
            SET data_aplicada = ?, pendente = ?
            WHERE id = ?
        '''
        self.db.execute_query(query, (data_aplicada, int(pendente), vacina_id))

    def excluir_vacina(self, vacina_id):
        query = 'DELETE FROM vacinas WHERE id = ?'
        self.db.execute_query(query, (vacina_id,))

class Crescimento_Grafico:
    def __init__(self, db_manager):
        self.db = db_manager

    def registrar_medida(self, paciente_id, peso, altura, data_medicao):
        query = '''
            INSERT INTO crescimento (paciente_id, peso, altura, data_medicao)
            VALUES (?, ?, ?, ?)
        '''
        cursor = self.db.execute_query(query, (paciente_id, peso, altura, data_medicao))
        return cursor.lastrowid

    def listar_medidas_paciente(self, paciente_id):
        query = 'SELECT * FROM crescimento WHERE paciente_id = ? ORDER BY data_medicao ASC'
        return self.db.fetch_all(query, (paciente_id,))

    def excluir_medida(self, medida_id):
        query = 'DELETE FROM crescimento WHERE id = ?'
        self.db.execute_query(query, (medida_id,))

class ControladorAgenda:
    def __init__(self, db_manager):
        self.db = db_manager

    def criar_agendamento(self, paciente_id, data_hora, tipo, descricao=""):
        query = '''
            INSERT INTO agendamentos (paciente_id, data_hora, tipo, descricao)
            VALUES (?, ?, ?, ?)
        '''
        cursor = self.db.execute_query(query, (paciente_id, data_hora, tipo, descricao))
        return cursor.lastrowid

    def listar_agendamentos(self, limite_dias=None):
        if limite_dias:
            query = '''
                SELECT a.*, p.nome as paciente_nome 
                FROM agendamentos a
                LEFT JOIN pacientes p ON a.paciente_id = p.id
                WHERE date(a.data_hora) <= date('now', '+' || ? || ' days')
                AND date(a.data_hora) >= date('now')
                ORDER BY a.data_hora ASC
            '''
            return self.db.fetch_all(query, (limite_dias,))
        else:
            query = '''
                SELECT a.*, p.nome as paciente_nome 
                FROM agendamentos a
                LEFT JOIN pacientes p ON a.paciente_id = p.id
                ORDER BY a.data_hora ASC
            '''
            return self.db.fetch_all(query)

    def excluir_agendamento(self, agendamento_id):
        query = 'DELETE FROM agendamentos WHERE id = ?'
        self.db.execute_query(query, (agendamento_id,))
