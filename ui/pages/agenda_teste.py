from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QHeaderView, QComboBox, QDateTimeEdit
)
from PyQt6.QtCore import pyqtSignal, QDateTime
from controllers.tudo_junto_controllers import ControladorAgenda
from controllers.paciente_dao_controller import ControladorDoPaciente

class AgendaApp(QWidget):
    agendamento_criado = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.controller = ControladorAgenda(db_manager)
        self.paciente_controller = ControladorDoPaciente(db_manager)
        self.id_em_edicao = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Agendamentos e Lembretes")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Formulário de Agendamento
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.combo_pacientes = QComboBox()
        self.input_data = QDateTimeEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.input_data.setDateTime(QDateTime.currentDateTime())
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

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Data/Hora", "Paciente", "Tipo", "Descrição"])
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabela.setSortingEnabled(True)
        self.tabela.itemDoubleClicked.connect(self.carregar_edicao)
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
        self.tabela.setSortingEnabled(False)
        self.tabela.setRowCount(0)
        agendamentos = self.controller.listar_agendamentos()
        for row_idx, a in enumerate(agendamentos):
            self.tabela.insertRow(row_idx)
            
            item_id = QTableWidgetItem()
            item_id.setData(0, a['id'])
            
            self.tabela.setItem(row_idx, 0, item_id)
            self.tabela.setItem(row_idx, 1, QTableWidgetItem(a['data_hora']))
            self.tabela.setItem(row_idx, 2, QTableWidgetItem(a['paciente_nome'] or "Desconhecido"))
            self.tabela.setItem(row_idx, 3, QTableWidgetItem(a['tipo']))
            self.tabela.setItem(row_idx, 4, QTableWidgetItem(a['descricao']))
        self.tabela.setSortingEnabled(True)
        
        self.limpar_form()

    def limpar_form(self):
        self.id_em_edicao = None
        self.btn_salvar.setText("Agendar")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.style().unpolish(self.btn_salvar)
        self.btn_salvar.style().polish(self.btn_salvar)
        
        self.input_data.setDateTime(QDateTime.currentDateTime())
        self.input_desc.clear()
        self.combo_pacientes.setCurrentIndex(0)

    def carregar_edicao(self, item):
        row = item.row()
        self.id_em_edicao = self.tabela.item(row, 0).data(0)
        
        agenda = self.controller.obter_agendamento(self.id_em_edicao)
        if agenda:
            idx = self.combo_pacientes.findData(agenda['paciente_id'])
            if idx >= 0:
                self.combo_pacientes.setCurrentIndex(idx)
                
            self.combo_tipo.setCurrentText(agenda['tipo'])
            self.input_desc.setText(agenda['descricao'])
            
            try:
                dt_obj = QDateTime.fromString(agenda['data_hora'], "dd/MM/yyyy HH:mm")
                if dt_obj.isValid():
                    self.input_data.setDateTime(dt_obj)
            except:
                pass

            self.btn_salvar.setText("Atualizar Agendamento")
            self.btn_salvar.setProperty("class", "WarningButton")
            self.btn_salvar.style().unpolish(self.btn_salvar)
            self.btn_salvar.style().polish(self.btn_salvar)

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

        if self.id_em_edicao:
            self.controller.atualizar_agendamento(self.id_em_edicao, data_hora, tipo, desc)
            QMessageBox.information(self, "Sucesso", "Agendamento atualizado.")
        else:
            self.controller.criar_agendamento(paciente_id, data_hora, tipo, desc)
            QMessageBox.information(self, "Sucesso", "Agendamento registrado.")
            
        self.load_data()
        self.agendamento_criado.emit()

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
