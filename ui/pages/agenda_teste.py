from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QHeaderView, QComboBox
)
from controllers.tudo_junto_controllers import ControladorAgenda
from controllers.paciente_dao_controller import ControladorDoPaciente

class AgendaApp(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.controller = ControladorAgenda(db_manager)
        self.paciente_controller = ControladorDoPaciente(db_manager)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Agendamentos e Lembretes")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Formulário de Agendamento
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.combo_pacientes = QComboBox()
        self.input_data = QLineEdit()
        self.input_data.setPlaceholderText("DD/MM/AAAA HH:MM")
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Consulta", "Vacina", "Retorno", "Outro"])
        self.input_desc = QLineEdit()

        form_layout.addRow("Paciente:", self.combo_pacientes)
        form_layout.addRow("Data e Hora:", self.input_data)
        form_layout.addRow("Tipo:", self.combo_tipo)
        form_layout.addRow("Descrição:", self.input_desc)
        
        self.layout.addWidget(form_widget)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Agendar")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.clicked.connect(self.salvar_agendamento)
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Data/Hora", "Paciente", "Tipo", "Descrição"])
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.tabela)

        self.btn_excluir = QPushButton("Excluir Agendamento")
        self.btn_excluir.setProperty("class", "DangerButton")
        self.btn_excluir.clicked.connect(self.excluir_agendamento)
        self.layout.addWidget(self.btn_excluir)

    def load_data(self):
        # Carregar combo
        self.combo_pacientes.blockSignals(True)
        self.combo_pacientes.clear()
        pacientes = self.paciente_controller.listar_pacientes()
        self.combo_pacientes.addItem("Selecione um paciente...", None)
        for p in pacientes:
            self.combo_pacientes.addItem(p['nome'], p['id'])
        self.combo_pacientes.blockSignals(False)

        # Carregar Tabela
        self.tabela.setRowCount(0)
        agendamentos = self.controller.listar_agendamentos()
        for row_idx, a in enumerate(agendamentos):
            self.tabela.insertRow(row_idx)
            self.tabela.setItem(row_idx, 0, QTableWidgetItem(str(a['id'])))
            self.tabela.setItem(row_idx, 1, QTableWidgetItem(a['data_hora']))
            self.tabela.setItem(row_idx, 2, QTableWidgetItem(a['paciente_nome'] or "Desconhecido"))
            self.tabela.setItem(row_idx, 3, QTableWidgetItem(a['tipo']))
            self.tabela.setItem(row_idx, 4, QTableWidgetItem(a['descricao']))

    def salvar_agendamento(self):
        paciente_id = self.combo_pacientes.currentData()
        if not paciente_id:
            QMessageBox.warning(self, "Aviso", "Selecione um paciente.")
            return

        data_hora = self.input_data.text()
        tipo = self.combo_tipo.currentText()
        desc = self.input_desc.text()

        if not data_hora:
            QMessageBox.warning(self, "Aviso", "A data/hora é obrigatória.")
            return

        self.controller.criar_agendamento(paciente_id, data_hora, tipo, desc)
        QMessageBox.information(self, "Sucesso", "Agendamento registrado.")
        self.input_data.clear()
        self.input_desc.clear()
        self.load_data()

    def excluir_agendamento(self):
        selected = self.tabela.currentRow()
        if selected >= 0:
            a_id = self.tabela.item(selected, 0).text()
            confirm = QMessageBox.question(self, "Confirmar", "Deseja excluir este agendamento?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.controller.excluir_agendamento(a_id)
                self.load_data()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um agendamento para excluir.")
