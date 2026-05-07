import matplotlib
matplotlib.use('QtAgg')

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QHeaderView, QComboBox, QDateEdit
)
from PyQt6.QtCore import QDate
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import datetime

from controllers.tudo_junto_controllers import Crescimento_Grafico
from controllers.paciente_dao_controller import ControladorDoPaciente

class GraficosPesoAltura(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.controller = Crescimento_Grafico(db_manager)
        self.paciente_controller = ControladorDoPaciente(db_manager)
        self.id_em_edicao = None
        
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
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDisplayFormat("dd/MM/yyyy")
        self.input_data.setDate(QDate.currentDate())

        form_layout.addRow("Peso (kg):", self.input_peso)
        form_layout.addRow("Altura (cm):", self.input_altura)
        form_layout.addRow("Data Medição:", self.input_data)
        left_layout.addWidget(form_widget)

        self.btn_salvar = QPushButton("Registrar Medida")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.clicked.connect(self.salvar_medida)
        left_layout.addWidget(self.btn_salvar)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Data", "Peso (kg)", "Altura (cm)", "IMC"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSortingEnabled(True)
        self.tabela.itemDoubleClicked.connect(self.carregar_edicao)
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

        # Tooltips
        self.annot_peso = self.ax_peso.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w", alpha=0.9), arrowprops=dict(arrowstyle="->"))
        self.annot_peso.set_visible(False)
        self.annot_altura = self.ax_altura.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w", alpha=0.9), arrowprops=dict(arrowstyle="->"))
        self.annot_altura.set_visible(False)
        self.canvas.mpl_connect("motion_notify_event", self.hover)

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
        self.tabela.setSortingEnabled(False)
        self.tabela.setRowCount(0)
        self.ax_peso.clear()
        self.ax_altura.clear()
        
        if paciente_id:
            medidas = self.controller.listar_medidas_paciente(paciente_id)
            
            parsed_data = []

            for row_idx, m in enumerate(medidas):
                self.tabela.insertRow(row_idx)
                
                item_id = QTableWidgetItem()
                item_id.setData(0, m['id'])
                
                self.tabela.setItem(row_idx, 0, item_id)
                self.tabela.setItem(row_idx, 1, QTableWidgetItem(m['data_medicao']))
                
                item_peso = QTableWidgetItem()
                item_peso.setData(0, float(m['peso']))
                self.tabela.setItem(row_idx, 2, item_peso)
                
                item_altura = QTableWidgetItem()
                item_altura.setData(0, float(m['altura']))
                self.tabela.setItem(row_idx, 3, item_altura)
                
                imc = 0.0
                if m['altura'] > 0:
                    imc = m['peso'] / ((m['altura']/100) ** 2)
                item_imc = QTableWidgetItem()
                item_imc.setData(0, round(imc, 1))
                self.tabela.setItem(row_idx, 4, item_imc)
                
                try:
                    dt_obj = datetime.datetime.strptime(m['data_medicao'], "%d/%m/%Y")
                    parsed_data.append((dt_obj, m['peso'], m['altura']))
                except (ValueError, TypeError):
                    continue

            self.tabela.setSortingEnabled(True)

            parsed_data.sort(key=lambda x: x[0])

            # Calcular Referências OMS
            paciente = self.paciente_controller.obter_paciente(paciente_id)
            data_nasc = None
            if paciente and paciente['data_nascimento']:
                try:
                    data_nasc = datetime.datetime.strptime(paciente['data_nascimento'], "%d/%m/%Y")
                except:
                    pass

            # Atualizar Gráfico
            if parsed_data:
                d_list = [x[0] for x in parsed_data]
                p_list = [x[1] for x in parsed_data]
                a_list = [x[2] for x in parsed_data]

                self.ax_peso.plot(d_list, p_list, marker='o', color='blue', label='Peso Real', zorder=5)
                self.ax_altura.plot(d_list, a_list, marker='s', color='green', label='Altura Real', zorder=5)

                if data_nasc:
                    # Gerar curva aproximada da OMS
                    # Pontos: desde o nascimento até a última data medida + margem
                    d_start = data_nasc
                    d_end = max(d_list[-1], data_nasc + datetime.timedelta(days=365*2))
                    days_diff = (d_end - d_start).days
                    
                    # Se houver diferença
                    if days_diff > 0:
                        oms_dates = [d_start + datetime.timedelta(days=x) for x in range(0, days_diff+30, 30)]
                        p3_peso, p50_peso, p97_peso = [], [], []
                        p3_altura, p50_altura, p97_altura = [], [], []

                        for d_oms in oms_dates:
                            age_years = (d_oms - d_start).days / 365.25
                            
                            # Peso Aproximado
                            if age_years < 1:
                                p50_p = 3.3 + (10 - 3.3) * age_years
                            else:
                                p50_p = age_years * 2 + 8
                                
                            p3_peso.append(p50_p * 0.8)
                            p50_peso.append(p50_p)
                            p97_peso.append(p50_p * 1.2)
                            
                            # Altura Aproximada
                            if age_years < 1:
                                p50_a = 50 + 25 * age_years
                            elif age_years < 2:
                                p50_a = 75 + 12 * (age_years - 1)
                            else:
                                p50_a = age_years * 6 + 77
                                
                            p3_altura.append(p50_a * 0.95)
                            p50_altura.append(p50_a)
                            p97_altura.append(p50_a * 1.05)

                        self.ax_peso.plot(oms_dates, p50_peso, '--', color='gray', label='P50', alpha=0.7)
                        self.ax_peso.fill_between(oms_dates, p3_peso, p97_peso, color='gray', alpha=0.15, label='P3-P97')

                        self.ax_altura.plot(oms_dates, p50_altura, '--', color='gray', label='P50', alpha=0.7)
                        self.ax_altura.fill_between(oms_dates, p3_altura, p97_altura, color='gray', alpha=0.15, label='P3-P97')


                self.ax_peso.set_title("Evolução do Peso")
                self.ax_peso.set_ylabel("kg")
                self.ax_peso.grid(True)
                self.ax_peso.tick_params(axis='x', rotation=45)
                self.ax_peso.legend(loc='upper left', fontsize='small')

                self.ax_altura.set_title("Evolução da Altura")
                self.ax_altura.set_ylabel("cm")
                self.ax_altura.grid(True)
                self.ax_altura.tick_params(axis='x', rotation=45)
                self.ax_altura.legend(loc='upper left', fontsize='small')

                # Format the dates
                self.ax_peso.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
                self.ax_altura.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))

                self.fig.tight_layout()
            
        self.canvas.draw()
        
        self.limpar_form()

    def hover(self, event):
        vis_p = False
        vis_a = False
        
        if event.inaxes == self.ax_peso:
            for line in self.ax_peso.lines:
                if line.get_label() == 'Peso Real':
                    cont, ind = line.contains(event)
                    if cont:
                        x, y = line.get_data()
                        x_val = x[ind["ind"][0]]
                        y_val = y[ind["ind"][0]]
                        self.annot_peso.xy = (x_val, y_val)
                        dt = mdates.num2date(x_val).strftime('%d/%m/%Y')
                        self.annot_peso.set_text(f"{dt}\n{y_val:.1f} kg")
                        self.annot_peso.set_visible(True)
                        vis_p = True
                        break
        
        if event.inaxes == self.ax_altura:
            for line in self.ax_altura.lines:
                if line.get_label() == 'Altura Real':
                    cont, ind = line.contains(event)
                    if cont:
                        x, y = line.get_data()
                        x_val = x[ind["ind"][0]]
                        y_val = y[ind["ind"][0]]
                        self.annot_altura.xy = (x_val, y_val)
                        dt = mdates.num2date(x_val).strftime('%d/%m/%Y')
                        self.annot_altura.set_text(f"{dt}\n{y_val:.1f} cm")
                        self.annot_altura.set_visible(True)
                        vis_a = True
                        break
                        
        if not vis_p and self.annot_peso.get_visible():
            self.annot_peso.set_visible(False)
        if not vis_a and self.annot_altura.get_visible():
            self.annot_altura.set_visible(False)
            
        if vis_p or vis_a or not vis_p or not vis_a:
            self.canvas.draw_idle()

    def limpar_form(self):
        self.id_em_edicao = None
        self.btn_salvar.setText("Registrar Medida")
        self.btn_salvar.setProperty("class", "SuccessButton")
        self.btn_salvar.style().unpolish(self.btn_salvar)
        self.btn_salvar.style().polish(self.btn_salvar)
        
        self.input_peso.clear()
        self.input_altura.clear()
        self.input_data.setDate(QDate.currentDate())

    def carregar_edicao(self, item):
        row = item.row()
        self.id_em_edicao = self.tabela.item(row, 0).data(0)
        
        medida = self.controller.obter_medida(self.id_em_edicao)
        if medida:
            self.input_peso.setText(str(medida['peso']).replace('.', ','))
            self.input_altura.setText(str(medida['altura']).replace('.', ','))
            
            try:
                date_obj = QDate.fromString(medida['data_medicao'], "dd/MM/yyyy")
                if date_obj.isValid():
                    self.input_data.setDate(date_obj)
            except:
                pass

            self.btn_salvar.setText("Atualizar Registro")
            self.btn_salvar.setProperty("class", "WarningButton")
            self.btn_salvar.style().unpolish(self.btn_salvar)
            self.btn_salvar.style().polish(self.btn_salvar)

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

        if self.id_em_edicao:
            self.controller.atualizar_medida(self.id_em_edicao, peso, altura, data)
            QMessageBox.information(self, "Sucesso", "Medida atualizada.")
        else:
            self.controller.registrar_medida(paciente_id, peso, altura, data)
            QMessageBox.information(self, "Sucesso", "Medida registrada.")
            
        self.limpar_form()
        self.on_paciente_changed()
