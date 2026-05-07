from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QHeaderView, QTextEdit, QDateEdit
)
from PyQt6.QtCore import QDate
from controllers.paciente_dao_controller import ControladorDoPaciente
from controllers.tudo_junto_controllers import ControlaAsVacinas
from .tela_detalhes_paciente import TelaDetalhesPaciente

class TelaPacienteDef(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.controller = ControladorDoPaciente(db_manager)
        self.vacina_controller = ControlaAsVacinas(db_manager)
        self.id_em_edicao = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Gerenciamento de Pacientes")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Formulário de Cadastro
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.input_nome = QLineEdit()
        self.input_nascimento = QDateEdit()
        self.input_nascimento.setCalendarPopup(True)
        self.input_nascimento.setDisplayFormat("dd/MM/yyyy")
        self.input_nascimento.setDate(QDate.currentDate())
        self.input_responsavel = QLineEdit()
        self.input_telefone = QLineEdit()
        self.input_historico = QTextEdit()
        self.input_historico.setMaximumHeight(60)

        form_layout.addRow("Nome do Paciente:", self.input_nome)
        form_layout.addRow("Data Nascimento:", self.input_nascimento)
        form_layout.addRow("Responsável:", self.input_responsavel)
        form_layout.addRow("Telefone:", self.input_telefone)
        form_layout.addRow("Histórico Básico:", self.input_historico)
        
        self.layout.addWidget(form_widget)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Cadastrar Paciente")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.clicked.connect(self.salvar_paciente)
        
        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.clicked.connect(self.limpar_form)

        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addWidget(self.btn_limpar)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # Busca e Tabela
        busca_layout = QHBoxLayout()
        lbl_busca = QLabel("Buscar Paciente:")
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Digite o nome para filtrar...")
        self.input_busca.textChanged.connect(self.filtrar_tabela)
        busca_layout.addWidget(lbl_busca)
        busca_layout.addWidget(self.input_busca)
        self.layout.addLayout(busca_layout)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Nascimento", "Responsável", "Telefone"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.setSortingEnabled(True)
        self.tabela.itemDoubleClicked.connect(self.carregar_edicao)
        self.layout.addWidget(self.tabela)

        # Botões de Ação da Tabela
        acoes_tabela_layout = QHBoxLayout()
        
        self.btn_prontuario = QPushButton("Ver Prontuário")
        self.btn_prontuario.setProperty("class", "PrimaryButton")
        self.btn_prontuario.clicked.connect(self.abrir_prontuario)
        
        self.btn_excluir = QPushButton("Excluir Selecionado")
        self.btn_excluir.setProperty("class", "DangerButton")
        self.btn_excluir.clicked.connect(self.excluir_paciente)
        
        acoes_tabela_layout.addWidget(self.btn_prontuario)
        acoes_tabela_layout.addStretch()
        acoes_tabela_layout.addWidget(self.btn_excluir)
        
        self.layout.addLayout(acoes_tabela_layout)

        self.load_data()

    def salvar_paciente(self):
        nome = self.input_nome.text()
        nasc = self.input_nascimento.text()
        resp = self.input_responsavel.text()
        tel = self.input_telefone.text()
        hist = self.input_historico.toPlainText()

        if not nome or not nasc or not resp:
            QMessageBox.warning(self, "Erro", "Nome, Nascimento e Responsável são obrigatórios.")
            return

        if self.id_em_edicao:
            self.controller.atualizar_paciente(self.id_em_edicao, nome, nasc, resp, tel, hist)
            QMessageBox.information(self, "Sucesso", "Paciente atualizado com sucesso!")
        else:
            novo_id = self.controller.criar_paciente(nome, nasc, resp, tel, hist)
            
            # Calendário Vacinal do SUS (Iniciais)
            try:
                dt_nasc = QDate.fromString(nasc, "dd/MM/yyyy")
                
                # Ao nascer
                self.vacina_controller.registrar_vacina(novo_id, "BCG", nasc, pendente=True)
                self.vacina_controller.registrar_vacina(novo_id, "Hepatite B", nasc, pendente=True)
                
                # Aos 2 meses
                if dt_nasc.isValid():
                    dt_2m = dt_nasc.addMonths(2).toString("dd/MM/yyyy")
                else:
                    dt_2m = ""
                
                self.vacina_controller.registrar_vacina(novo_id, "Penta (1ª dose)", dt_2m, pendente=True)
                self.vacina_controller.registrar_vacina(novo_id, "VIP (1ª dose)", dt_2m, pendente=True)
                self.vacina_controller.registrar_vacina(novo_id, "Rotavírus (1ª dose)", dt_2m, pendente=True)
            except Exception as e:
                print("Erro ao gerar vacinas:", e)

            QMessageBox.information(self, "Sucesso", "Paciente cadastrado e calendário vacinal inicial gerado!")
            
        self.limpar_form()
        self.load_data()

    def carregar_edicao(self, item):
        row = item.row()
        self.id_em_edicao = self.tabela.item(row, 0).data(0)
        
        # Obter dados completos do banco (pois a tabela pode não ter todos os campos visíveis, ex: histórico)
        paciente = self.controller.obter_paciente(self.id_em_edicao)
        if paciente:
            self.input_nome.setText(paciente['nome'])
            self.input_responsavel.setText(paciente['responsavel'])
            self.input_telefone.setText(paciente['telefone'])
            self.input_historico.setText(paciente['historico'])
            
            # Converter data string para QDate
            try:
                date_obj = QDate.fromString(paciente['data_nascimento'], "dd/MM/yyyy")
                if date_obj.isValid():
                    self.input_nascimento.setDate(date_obj)
            except:
                pass

            self.btn_salvar.setText("Atualizar Registro")
            self.btn_salvar.setProperty("class", "WarningButton")
            self.btn_salvar.style().unpolish(self.btn_salvar)
            self.btn_salvar.style().polish(self.btn_salvar)

    def limpar_form(self):
        self.id_em_edicao = None
        self.btn_salvar.setText("Cadastrar Paciente")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.style().unpolish(self.btn_salvar)
        self.btn_salvar.style().polish(self.btn_salvar)
        
        self.input_nome.clear()
        self.input_nascimento.setDate(QDate.currentDate())
        self.input_responsavel.clear()
        self.input_telefone.clear()
        self.input_historico.clear()

    def load_data(self):
        self.tabela.setSortingEnabled(False)
        self.tabela.setRowCount(0)
        pacientes = self.controller.listar_pacientes()
        for row_idx, p in enumerate(pacientes):
            self.tabela.insertRow(row_idx)
            
            item_id = QTableWidgetItem()
            item_id.setData(0, p['id']) # setData para ordenar como número
            
            self.tabela.setItem(row_idx, 0, item_id)
            self.tabela.setItem(row_idx, 1, QTableWidgetItem(p['nome']))
            self.tabela.setItem(row_idx, 2, QTableWidgetItem(p['data_nascimento']))
            self.tabela.setItem(row_idx, 3, QTableWidgetItem(p['responsavel']))
            self.tabela.setItem(row_idx, 4, QTableWidgetItem(p['telefone']))
        self.tabela.setSortingEnabled(True)

    def filtrar_tabela(self, texto):
        texto = texto.lower()
        for row in range(self.tabela.rowCount()):
            item_nome = self.tabela.item(row, 1)
            if item_nome and texto in item_nome.text().lower():
                self.tabela.setRowHidden(row, False)
            else:
                self.tabela.setRowHidden(row, True)

    def excluir_paciente(self):
        selected = self.tabela.currentRow()
        if selected >= 0:
            p_id = self.tabela.item(selected, 0).text()
            nome = self.tabela.item(selected, 1).text()
            msg = f"A exclusão do paciente '{nome}' apagará todo o seu histórico (consultas, vacinas, medições e agendamentos).\n\nEssa ação é irreversível. Deseja continuar?"
            confirm = QMessageBox.question(self, "Aviso de Exclusão", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.controller.excluir_paciente(p_id)
                self.load_data()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um paciente na tabela para excluir.")

    def abrir_prontuario(self):
        selected = self.tabela.currentRow()
        if selected >= 0:
            p_id = self.tabela.item(selected, 0).text()
            # Precisamos passar o db_manager que guardamos em Controller
            # como não salvamos na classe, vamos usar o self.controller.db
            dialog = TelaDetalhesPaciente(p_id, self.controller.db, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um paciente para ver o prontuário.")
