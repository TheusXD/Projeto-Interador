import matplotlib
matplotlib.use('QtAgg')

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QHeaderView, QComboBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime

from controllers.tudo_junto_controllers import Crescimento_Grafico
from controllers.paciente_dao_controller import ControladorDoPaciente

class GraficosPesoAltura(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.controller = Crescimento_Grafico(db_manager)
        self.paciente_controller = ControladorDoPaciente(db_manager)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Acompanhamento de Crescimento")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Seleção de Paciente
        paciente_layout = QHBoxLayout()
        paciente_layout.addWidget(QLabel("Paciente:"))
        self.combo_pacientes = QComboBox()
        self.combo_pacientes.currentIndexChanged.connect(self.on_paciente_changed)
        paciente_layout.addWidget(self.combo_pacientes, 1)
        self.layout.addLayout(paciente_layout)

        content_layout = QHBoxLayout()

        # Esquerda: Formulário e Tabela
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.input_peso = QLineEdit()
        self.input_peso.setPlaceholderText("Peso em kg")
        self.input_altura = QLineEdit()
        self.input_altura.setPlaceholderText("Altura em cm")
        self.input_data = QLineEdit()
        self.input_data.setText(datetime.datetime.now().strftime("%d/%m/%Y"))

        form_layout.addRow("Peso (kg):", self.input_peso)
        form_layout.addRow("Altura (cm):", self.input_altura)
        form_layout.addRow("Data Medição:", self.input_data)
        left_layout.addWidget(form_widget)

        self.btn_salvar = QPushButton("Registrar Medida")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.clicked.connect(self.salvar_medida)
        left_layout.addWidget(self.btn_salvar)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Data", "Peso (kg)", "Altura (cm)"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.tabela)

        content_layout.addWidget(left_widget, 1)

        # Direita: Gráfico Matplotlib
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0,0,0,0)
        
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.ax_peso = self.fig.add_subplot(211)
        self.ax_altura = self.fig.add_subplot(212)
        right_layout.addWidget(self.canvas)

        content_layout.addWidget(right_widget, 2)
        self.layout.addLayout(content_layout)

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
        self.tabela.setRowCount(0)
        self.ax_peso.clear()
        self.ax_altura.clear()
        
        if paciente_id:
            medidas = self.controller.listar_medidas_paciente(paciente_id)
            
            datas = []
            pesos = []
            alturas = []

            for row_idx, m in enumerate(medidas):
                self.tabela.insertRow(row_idx)
                self.tabela.setItem(row_idx, 0, QTableWidgetItem(str(m['id'])))
                self.tabela.setItem(row_idx, 1, QTableWidgetItem(m['data_medicao']))
                self.tabela.setItem(row_idx, 2, QTableWidgetItem(str(m['peso'])))
                self.tabela.setItem(row_idx, 3, QTableWidgetItem(str(m['altura'])))
                
                datas.append(m['data_medicao'])
                pesos.append(m['peso'])
                alturas.append(m['altura'])

            # Atualizar Gráfico
            if datas:
                self.ax_peso.plot(datas, pesos, marker='o', color='blue', label='Peso')
                self.ax_peso.set_title("Evolução do Peso")
                self.ax_peso.set_ylabel("kg")
                self.ax_peso.grid(True)

                self.ax_altura.plot(datas, alturas, marker='s', color='green', label='Altura')
                self.ax_altura.set_title("Evolução da Altura")
                self.ax_altura.set_ylabel("cm")
                self.ax_altura.grid(True)

                self.fig.tight_layout()
            
        self.canvas.draw()

    def salvar_medida(self):
        paciente_id = self.combo_pacientes.currentData()
        if not paciente_id:
            QMessageBox.warning(self, "Aviso", "Selecione um paciente primeiro.")
            return

        try:
            peso = float(self.input_peso.text().replace(',', '.'))
            altura = float(self.input_altura.text().replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Peso e Altura devem ser números.")
            return
            
        data = self.input_data.text()

        self.controller.registrar_medida(paciente_id, peso, altura, data)
        self.input_peso.clear()
        self.input_altura.clear()
        self.on_paciente_changed()
