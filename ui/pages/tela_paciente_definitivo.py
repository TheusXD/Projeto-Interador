from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QHeaderView, QTextEdit
)
from controllers.paciente_dao_controller import ControladorDoPaciente

class TelaPacienteDef(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.controller = ControladorDoPaciente(db_manager)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Gerenciamento de Pacientes")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Formulário de Cadastro
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.input_nome = QLineEdit()
        self.input_nascimento = QLineEdit()
        self.input_nascimento.setPlaceholderText("DD/MM/AAAA")
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

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Nascimento", "Responsável", "Telefone"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.tabela)

        self.btn_excluir = QPushButton("Excluir Selecionado")
        self.btn_excluir.setProperty("class", "DangerButton")
        self.btn_excluir.clicked.connect(self.excluir_paciente)
        self.layout.addWidget(self.btn_excluir)

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

        self.controller.criar_paciente(nome, nasc, resp, tel, hist)
        QMessageBox.information(self, "Sucesso", "Paciente cadastrado com sucesso!")
        self.limpar_form()
        self.load_data()

    def limpar_form(self):
        self.input_nome.clear()
        self.input_nascimento.clear()
        self.input_responsavel.clear()
        self.input_telefone.clear()
        self.input_historico.clear()

    def load_data(self):
        self.tabela.setRowCount(0)
        pacientes = self.controller.listar_pacientes()
        for row_idx, p in enumerate(pacientes):
            self.tabela.insertRow(row_idx)
            self.tabela.setItem(row_idx, 0, QTableWidgetItem(str(p['id'])))
            self.tabela.setItem(row_idx, 1, QTableWidgetItem(p['nome']))
            self.tabela.setItem(row_idx, 2, QTableWidgetItem(p['data_nascimento']))
            self.tabela.setItem(row_idx, 3, QTableWidgetItem(p['responsavel']))
            self.tabela.setItem(row_idx, 4, QTableWidgetItem(p['telefone']))

    def excluir_paciente(self):
        selected = self.tabela.currentRow()
        if selected >= 0:
            p_id = self.tabela.item(selected, 0).text()
            confirm = QMessageBox.question(self, "Confirmar", "Deseja excluir este paciente?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.controller.excluir_paciente(p_id)
                self.load_data()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um paciente na tabela para excluir.")
