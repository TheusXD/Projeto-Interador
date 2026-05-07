from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QHeaderView, QComboBox, QCheckBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from controllers.tudo_junto_controllers import ControlaAsVacinas
from controllers.paciente_dao_controller import ControladorDoPaciente

class ViewVacinas(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.controller = ControlaAsVacinas(db_manager)
        self.paciente_controller = ControladorDoPaciente(db_manager)
        self.id_em_edicao = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Controle de Vacinas")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Seleção de Paciente
        paciente_layout = QHBoxLayout()
        paciente_layout.addWidget(QLabel("Paciente:"))
        self.combo_pacientes = QComboBox()
        self.combo_pacientes.currentIndexChanged.connect(self.on_paciente_changed)
        paciente_layout.addWidget(self.combo_pacientes, 1)
        self.layout.addLayout(paciente_layout)

        # Formulário
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.input_vacina = QLineEdit()
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDisplayFormat("dd/MM/yyyy")
        self.input_data.setDate(QDate.currentDate())
        self.check_pendente = QCheckBox("Vacina Pendente")
        self.check_pendente.setChecked(True)
        self.input_data.setEnabled(False)
        self.check_pendente.stateChanged.connect(self.on_pendente_changed)

        form_layout.addRow("Nome da Vacina:", self.input_vacina)
        form_layout.addRow("Data Aplicada:", self.input_data)
        form_layout.addRow("", self.check_pendente)
        
        self.layout.addWidget(form_widget)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Registrar Vacina")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.clicked.connect(self.salvar_vacina)
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Vacina", "Data", "Status"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.setSortingEnabled(True)
        self.tabela.itemDoubleClicked.connect(self.carregar_edicao)
        self.layout.addWidget(self.tabela)

    def load_data(self):
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
        self.tabela.setSortingEnabled(False)
        self.tabela.setRowCount(0)
        if paciente_id:
            vacinas = self.controller.listar_vacinas_paciente(paciente_id)
            for row_idx, v in enumerate(vacinas):
                self.tabela.insertRow(row_idx)
                
                item_id = QTableWidgetItem()
                item_id.setData(0, v['id'])
                
                self.tabela.setItem(row_idx, 0, item_id)
                self.tabela.setItem(row_idx, 1, QTableWidgetItem(v['nome_vacina']))
                self.tabela.setItem(row_idx, 2, QTableWidgetItem(v['data_aplicada'] or "-"))
                
                status = "Pendente" if v['pendente'] else "Aplicada"
                item_status = QTableWidgetItem(status)
                if v['pendente']:
                    item_status.setForeground(Qt.GlobalColor.red)
                else:
                    item_status.setForeground(Qt.GlobalColor.darkGreen)
                self.tabela.setItem(row_idx, 3, item_status)
        self.tabela.setSortingEnabled(True)
        
        self.limpar_form()

    def limpar_form(self):
        self.id_em_edicao = None
        self.btn_salvar.setText("Registrar Vacina")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.style().unpolish(self.btn_salvar)
        self.btn_salvar.style().polish(self.btn_salvar)
        
        self.input_vacina.clear()
        self.input_data.setDate(QDate.currentDate())
        self.check_pendente.setChecked(True)

    def carregar_edicao(self, item):
        row = item.row()
        self.id_em_edicao = self.tabela.item(row, 0).data(0)
        
        vacina = self.controller.obter_vacina(self.id_em_edicao)
        if vacina:
            self.input_vacina.setText(vacina['nome_vacina'])
            self.check_pendente.setChecked(bool(vacina['pendente']))
            
            if not vacina['pendente'] and vacina['data_aplicada']:
                try:
                    date_obj = QDate.fromString(vacina['data_aplicada'], "dd/MM/yyyy")
                    if date_obj.isValid():
                        self.input_data.setDate(date_obj)
                except:
                    pass

            self.btn_salvar.setText("Atualizar Registro")
            self.btn_salvar.setProperty("class", "WarningButton")
            self.btn_salvar.style().unpolish(self.btn_salvar)
            self.btn_salvar.style().polish(self.btn_salvar)

    def on_pendente_changed(self, state):
        self.input_data.setEnabled(not bool(state))

    def salvar_vacina(self):
        paciente_id = self.combo_pacientes.currentData()
        if not paciente_id:
            QMessageBox.warning(self, "Aviso", "Selecione um paciente primeiro.")
            return

        vacina = self.input_vacina.text()
        pendente = self.check_pendente.isChecked()
        data = "" if pendente else self.input_data.text()

        if not vacina:
            QMessageBox.warning(self, "Aviso", "Nome da vacina é obrigatório.")
            return

        if self.id_em_edicao:
            self.controller.atualizar_vacina(self.id_em_edicao, vacina, data, pendente)
            QMessageBox.information(self, "Sucesso", "Vacina atualizada.")
        else:
            self.controller.registrar_vacina(paciente_id, vacina, data, pendente)
            QMessageBox.information(self, "Sucesso", "Vacina registrada.")
            
        self.limpar_form()
        self.on_paciente_changed()
