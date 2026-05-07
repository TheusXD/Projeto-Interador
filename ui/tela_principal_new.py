from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QLabel
)
from PyQt6.QtCore import Qt

from .pages.pag_dash import PagDash
from .pages.tela_paciente_definitivo import TelaPacienteDef
from .pages.consulta_front import FrontConsulta
from .pages.view_vacinas import ViewVacinas
from .pages.grafico_peso_altura import GraficosPesoAltura
from .pages.agenda_teste import AgendaApp

class TelaPrincipalApp(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        self.setWindowTitle("Sistema de Apoio Pediátrico")
        self.resize(1024, 768)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Configurar Sidebar e Stacked Widget
        self.setup_sidebar()
        self.setup_pages()

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stacked_widget, stretch=1)

        # Selecionar a primeira página
        self.navigate_to(0)

    def setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 20, 10, 20)
        self.sidebar_layout.setSpacing(10)

        title_label = QLabel("Apoio Pediátrico")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1F2937; margin-bottom: 20px;")
        self.sidebar_layout.addWidget(title_label)

        self.nav_buttons = []
        
        # Menu Items (Nome, Indice da página)
        menus = [
            ("Dashboard", 0),
            ("Pacientes", 1),
            ("Consultas", 2),
            ("Vacinas", 3),
            ("Crescimento", 4),
            ("Agendamentos", 5)
        ]

        for text, index in menus:
            btn = QPushButton(text)
            btn.setObjectName("MenuButton")
            btn.setProperty("class", "MenuButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=index: self.navigate_to(idx))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        self.sidebar_layout.addStretch()

    def setup_pages(self):
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("ContentArea")

        # Inicializando páginas
        self.page_dashboard = PagDash(self.db_manager)
        self.page_pacientes = TelaPacienteDef(self.db_manager)
        self.page_consultas = FrontConsulta(self.db_manager)
        self.page_vacinas = ViewVacinas(self.db_manager)
        self.page_crescimento = GraficosPesoAltura(self.db_manager)
        self.page_agenda = AgendaApp(self.db_manager)

        # Adicionando ao stack (deve bater com os índices do menu)
        self.stacked_widget.addWidget(self.page_dashboard)   # 0
        self.stacked_widget.addWidget(self.page_pacientes)   # 1
        self.stacked_widget.addWidget(self.page_consultas)   # 2
        self.stacked_widget.addWidget(self.page_vacinas)     # 3
        self.stacked_widget.addWidget(self.page_crescimento) # 4
        self.stacked_widget.addWidget(self.page_agenda)      # 5

        # Conectar sinal da agenda para atualizar o dashboard
        self.page_agenda.agendamento_criado.connect(self.page_dashboard.load_data)

    def navigate_to(self, index):
        # Atualizar estado dos botões
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Mudar a página
        self.stacked_widget.setCurrentIndex(index)
        
        # Opcional: Atualizar os dados da página quando ela for exibida
        current_page = self.stacked_widget.widget(index)
        if hasattr(current_page, "load_data"):
            current_page.load_data()
