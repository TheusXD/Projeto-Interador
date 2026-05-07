import datetime

class DashboardController:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_estatisticas(self):
        # Total de Pacientes
        q_pacientes = "SELECT COUNT(*) as total FROM pacientes"
        res_p = self.db.fetch_one(q_pacientes)
        total_pacientes = res_p['total'] if res_p else 0

        # Consultas do Mês
        hoje = datetime.date.today()
        mes_atual = f"{hoje.month:02d}/{hoje.year}"
        q_consultas = "SELECT COUNT(*) as total FROM consultas WHERE data_consulta LIKE ?"
        res_c = self.db.fetch_one(q_consultas, (f"%/{mes_atual}",))
        consultas_mes = res_c['total'] if res_c else 0

        # Vacinas Pendentes
        q_vacinas = "SELECT COUNT(*) as total FROM vacinas WHERE pendente = 1"
        res_v = self.db.fetch_one(q_vacinas)
        vacinas_pendentes = res_v['total'] if res_v else 0

        # Vacinas Atrasadas (data_aplicada é guardada no formato dd/mm/yyyy. Isso é difícil comparar via SQL direto. 
        # Vamos puxar as pendentes e contar em Python para maior precisão de conversão).
        q_pendentes = "SELECT data_aplicada FROM vacinas WHERE pendente = 1"
        pendentes_raw = self.db.fetch_all(q_pendentes)
        vacinas_atrasadas = 0
        for v in pendentes_raw:
            try:
                dt_obj = datetime.datetime.strptime(v['data_aplicada'], "%d/%m/%Y").date()
                if dt_obj < hoje:
                    vacinas_atrasadas += 1
            except:
                pass # Ignora datas em branco ou mal formatadas

        # Próximo Agendamento
        # Data/Hora está salva como 'dd/mm/yyyy HH:mm' ou similar. O SQL order by string pode falhar, 
        # então pegamos os agendamentos futuros no Python ou adaptamos o format no banco.
        q_agenda = "SELECT a.*, p.nome as paciente_nome FROM agendamentos a LEFT JOIN pacientes p ON a.paciente_id = p.id"
        agendamentos = self.db.fetch_all(q_agenda)
        proximo = None
        min_delta = None
        agora = datetime.datetime.now()
        for a in agendamentos:
            try:
                dt_ag = datetime.datetime.strptime(a['data_hora'], "%d/%m/%Y %H:%M")
                if dt_ag >= agora:
                    delta = dt_ag - agora
                    if min_delta is None or delta < min_delta:
                        min_delta = delta
                        proximo = f"{a['paciente_nome']} ({a['data_hora']})"
            except:
                pass
        
        # Banners (Alertas do Dia)
        alertas = []
        agendamentos_hoje = []
        for a in agendamentos:
            try:
                dt_ag = datetime.datetime.strptime(a['data_hora'], "%d/%m/%Y %H:%M").date()
                if dt_ag == hoje:
                    agendamentos_hoje.append(f"{a['data_hora'].split(' ')[1]} - {a['paciente_nome']}")
            except:
                pass
        
        if agendamentos_hoje:
            alertas.append(f"Você tem {len(agendamentos_hoje)} agendamento(s) para hoje!")
            
        if vacinas_atrasadas > 0:
            alertas.append(f"Atenção: Há {vacinas_atrasadas} vacina(s) com aplicação atrasada!")

        # Consultas há mais de 6 meses sem retorno
        seis_meses_atras = hoje - datetime.timedelta(days=180)
        q_ultimas_consultas = '''
            SELECT paciente_id, MAX(data_consulta) as ultima 
            FROM consultas GROUP BY paciente_id
        '''
        ultimas = self.db.fetch_all(q_ultimas_consultas)
        pacientes_sem_retorno = 0
        for u in ultimas:
            try:
                dt_ult = datetime.datetime.strptime(u['ultima'], "%d/%m/%Y").date()
                if dt_ult < seis_meses_atras:
                    pacientes_sem_retorno += 1
            except:
                pass
                
        if pacientes_sem_retorno > 0:
            alertas.append(f"Há {pacientes_sem_retorno} paciente(s) sem retorno há mais de 6 meses.")

        return {
            'total_pacientes': total_pacientes,
            'consultas_mes': consultas_mes,
            'vacinas_pendentes': vacinas_pendentes,
            'vacinas_atrasadas': vacinas_atrasadas,
            'proximo_agendamento': proximo or "Nenhum",
            'alertas': alertas
        }
