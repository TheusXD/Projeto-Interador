from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QHeaderView, QTextEdit, QComboBox
)
from controllers.tudo_junto_controllers import ControladorDasConsultas
from controllers.paciente_dao_controller import ControladorDoPaciente

class FrontConsulta(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.controller = ControladorDasConsultas(db_manager)
        self.paciente_controller = ControladorDoPaciente(db_manager)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Registro de Consultas")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Seleção de Paciente
        paciente_layout = QHBoxLayout()
        paciente_layout.addWidget(QLabel("Paciente:"))
        self.combo_pacientes = QComboBox()
        self.combo_pacientes.currentIndexChanged.connect(self.on_paciente_changed)
        paciente_layout.addWidget(self.combo_pacientes, 1)
        self.layout.addLayout(paciente_layout)

        # Formulário de Consulta
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.input_data = QLineEdit()
        self.input_data.setPlaceholderText("DD/MM/AAAA")
        self.input_obs = QTextEdit()
        self.input_obs.setMaximumHeight(50)
        self.input_diag = QLineEdit()
        self.input_presc = QTextEdit()
        self.input_presc.setMaximumHeight(50)

        form_layout.addRow("Data Consulta:", self.input_data)
        form_layout.addRow("Observações:", self.input_obs)
        form_layout.addRow("Diagnóstico:", self.input_diag)
        form_layout.addRow("Prescrição:", self.input_presc)
        
        self.layout.addWidget(form_widget)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Salvar Consulta")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.clicked.connect(self.salvar_consulta)
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Data", "Diagnóstico", "Prescrição"])
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.tabela)

    def load_data(self):
        # Atualizar combo de pacientes
        self.combo_pacientes.blockSignals(True)
        self.combo_pacientes.clear()
        pacientes = self.paciente_controller.listar_pacientes()
        self.combo_pacientes.addItem("Selecione um paciente...", None)
        for p in pacientes:
            self.combo_pacientes.addItem(p['nome'], p['id'])
        self.combo_pacientes.blockSignals(False)
        self.on_paciente_changed()

    def on_paciente_changed(self):
        paciente_id = self.combo_pacientes.currentData()
        self.tabela.setRowCount(0)
        if paciente_id:
            consultas = self.controller.listar_consultas_paciente(paciente_id)
            for row_idx, c in enumerate(consultas):
                self.tabela.insertRow(row_idx)
                self.tabela.setItem(row_idx, 0, QTableWidgetItem(str(c['id'])))
                self.tabela.setItem(row_idx, 1, QTableWidgetItem(c['data_consulta']))
                self.tabela.setItem(row_idx, 2, QTableWidgetItem(c['diagnostico']))
                self.tabela.setItem(row_idx, 3, QTableWidgetItem(c['prescricao']))

    def salvar_consulta(self):
        paciente_id = self.combo_pacientes.currentData()
        if not paciente_id:
            QMessageBox.warning(self, "Aviso", "Selecione um paciente primeiro.")
            return

        data = self.input_data.text()
        obs = self.input_obs.toPlainText()
        diag = self.input_diag.text()
        presc = self.input_presc.toPlainText()

        if not data:
            QMessageBox.warning(self, "Aviso", "Data da consulta é obrigatória.")
            return

        self.controller.criar_consulta(paciente_id, data, obs, diag, presc)
        QMessageBox.information(self, "Sucesso", "Consulta registrada.")
        self.input_data.clear()
        self.input_obs.clear()
        self.input_diag.clear()
        self.input_presc.clear()
        self.on_paciente_changed()
