from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QTextEdit, QFileDialog
)
from PyQt6.QtCore import Qt

from controllers.paciente_dao_controller import ControladorDoPaciente
from controllers.tudo_junto_controllers import ControladorDasConsultas, ControlaAsVacinas, Crescimento_Grafico

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

class TelaDetalhesPaciente(QDialog):
    def __init__(self, paciente_id, db_manager, parent=None):
        super().__init__(parent)
        self.paciente_id = paciente_id
        self.db = db_manager
        
        self.paciente_ctrl = ControladorDoPaciente(self.db)
        self.consulta_ctrl = ControladorDasConsultas(self.db)
        self.vacina_ctrl = ControlaAsVacinas(self.db)
        self.cresc_ctrl = Crescimento_Grafico(self.db)
        
        self.paciente = self.paciente_ctrl.obter_paciente(self.paciente_id)
        
        self.setWindowTitle(f"Prontuário - {self.paciente['nome']}")
        self.resize(800, 600)
        
        self.layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel(f"Prontuário Médico: {self.paciente['nome']}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1F2937;")
        header_layout.addWidget(title)
        
        btn_exportar = QPushButton("Exportar PDF")
        btn_exportar.setProperty("class", "PrimaryButton")
        btn_exportar.clicked.connect(self.exportar_pdf)
        header_layout.addStretch()
        header_layout.addWidget(btn_exportar)
        
        self.layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        self.tab_dados = QWidget()
        self.tab_consultas = QWidget()
        self.tab_vacinas = QWidget()
        self.tab_cresc = QWidget()
        
        self.tabs.addTab(self.tab_dados, "Dados Cadastrais")
        self.tabs.addTab(self.tab_consultas, "Consultas")
        self.tabs.addTab(self.tab_vacinas, "Vacinas")
        self.tabs.addTab(self.tab_cresc, "Crescimento")
        
        self.layout.addWidget(self.tabs)
        
        self.setup_tab_dados()
        self.setup_tab_consultas()
        self.setup_tab_vacinas()
        self.setup_tab_cresc()
        
    def setup_tab_dados(self):
        layout = QVBoxLayout(self.tab_dados)
        
        info = f"""
        <b>Nome:</b> {self.paciente['nome']}<br><br>
        <b>Data de Nascimento:</b> {self.paciente['data_nascimento']}<br><br>
        <b>Responsável:</b> {self.paciente['responsavel']}<br><br>
        <b>Telefone:</b> {self.paciente['telefone']}
        """
        lbl_info = QLabel(info)
        lbl_info.setStyleSheet("font-size: 14px; color: #374151;")
        layout.addWidget(lbl_info)
        
        layout.addWidget(QLabel("<b>Histórico Médico:</b>"))
        txt_historico = QTextEdit()
        txt_historico.setPlainText(self.paciente['historico'])
        txt_historico.setReadOnly(True)
        layout.addWidget(txt_historico)

    def setup_tab_consultas(self):
        layout = QVBoxLayout(self.tab_consultas)
        tabela = QTableWidget()
        tabela.setColumnCount(3)
        tabela.setHorizontalHeaderLabels(["Data", "Diagnóstico", "Prescrição"])
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        consultas = self.consulta_ctrl.listar_consultas_paciente(self.paciente_id)
        tabela.setRowCount(len(consultas))
        
        for i, c in enumerate(consultas):
            tabela.setItem(i, 0, QTableWidgetItem(c['data_consulta']))
            tabela.setItem(i, 1, QTableWidgetItem(c['diagnostico']))
            tabela.setItem(i, 2, QTableWidgetItem(c['prescricao']))
            
        layout.addWidget(tabela)

    def setup_tab_vacinas(self):
        layout = QVBoxLayout(self.tab_vacinas)
        tabela = QTableWidget()
        tabela.setColumnCount(3)
        tabela.setHorizontalHeaderLabels(["Vacina", "Data", "Status"])
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        vacinas = self.vacina_ctrl.listar_vacinas_paciente(self.paciente_id)
        tabela.setRowCount(len(vacinas))
        
        for i, v in enumerate(vacinas):
            tabela.setItem(i, 0, QTableWidgetItem(v['nome_vacina']))
            tabela.setItem(i, 1, QTableWidgetItem(v['data_aplicada'] or "-"))
            status = "Pendente" if v['pendente'] else "Aplicada"
            item_status = QTableWidgetItem(status)
            if v['pendente']:
                item_status.setForeground(Qt.GlobalColor.red)
            else:
                item_status.setForeground(Qt.GlobalColor.darkGreen)
            tabela.setItem(i, 2, item_status)
            
        layout.addWidget(tabela)

    def setup_tab_cresc(self):
        layout = QVBoxLayout(self.tab_cresc)
        tabela = QTableWidget()
        tabela.setColumnCount(4)
        tabela.setHorizontalHeaderLabels(["Data", "Peso (kg)", "Altura (cm)", "IMC"])
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        medidas = self.cresc_ctrl.listar_medidas_paciente(self.paciente_id)
        tabela.setRowCount(len(medidas))
        
        for i, m in enumerate(medidas):
            tabela.setItem(i, 0, QTableWidgetItem(m['data_medicao']))
            tabela.setItem(i, 1, QTableWidgetItem(str(m['peso'])))
            tabela.setItem(i, 2, QTableWidgetItem(str(m['altura'])))
            
            imc = 0.0
            if m['altura'] > 0:
                imc = m['peso'] / ((m['altura']/100) ** 2)
            tabela.setItem(i, 3, QTableWidgetItem(str(round(imc, 1))))
            
        layout.addWidget(tabela)

    def exportar_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Prontuário PDF", f"Prontuario_{self.paciente['nome']}.pdf", "PDF Files (*.pdf)")
        
        if not file_path:
            return
            
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Título
            elements.append(Paragraph(f"Prontuário Médico: {self.paciente['nome']}", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Dados Paciente
            elements.append(Paragraph("Dados Cadastrais", styles['Heading2']))
            dados = [
                [Paragraph("<b>Data Nascimento:</b>", styles['Normal']), self.paciente['data_nascimento']],
                [Paragraph("<b>Responsável:</b>", styles['Normal']), self.paciente['responsavel']],
                [Paragraph("<b>Telefone:</b>", styles['Normal']), self.paciente['telefone']]
            ]
            t = Table(dados, colWidths=[150, 300])
            t.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 12))
            
            # Histórico
            if self.paciente['historico']:
                elements.append(Paragraph("Histórico Básico", styles['Heading2']))
                elements.append(Paragraph(self.paciente['historico'], styles['Normal']))
                elements.append(Spacer(1, 12))
                
            # Consultas
            consultas = self.consulta_ctrl.listar_consultas_paciente(self.paciente_id)
            if consultas:
                elements.append(Paragraph("Consultas Registradas", styles['Heading2']))
                data = [["Data", "Diagnóstico", "Prescrição", "Observações"]]
                for c in consultas:
                    data.append([
                        c['data_consulta'], 
                        Paragraph(c['diagnostico'], styles['Normal']), 
                        Paragraph(c['prescricao'], styles['Normal']),
                        Paragraph(c['observacoes'], styles['Normal'])
                    ])
                t_cons = Table(data, colWidths=[80, 140, 140, 140])
                t_cons.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(t_cons)
                elements.append(Spacer(1, 12))
                
            doc.build(elements)
            QMessageBox.information(self, "Sucesso", "Prontuário exportado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF:\n{str(e)}")
