from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from controllers.dashboard_controller import DashboardController

class PagDash(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.controller = DashboardController(db_manager)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        title = QLabel("Dashboard")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Banners (Alertas)
        self.banners_layout = QVBoxLayout()
        self.banners_layout.setSpacing(10)
        self.layout.addLayout(self.banners_layout)

        # Container para cards
        self.cards_layout = QHBoxLayout()
        
        # 4 Cards
        self.card_pacientes = self.create_card("Total Pacientes", "0")
        self.card_consultas = self.create_card("Consultas/Mês", "0")
        self.card_vacinas = self.create_card("Vacinas Pendentes", "0")
        self.card_agenda = self.create_card("Próx. Agendamento", "-")

        self.cards_layout.addWidget(self.card_pacientes)
        self.cards_layout.addWidget(self.card_consultas)
        self.cards_layout.addWidget(self.card_vacinas)
        self.cards_layout.addWidget(self.card_agenda)

        self.layout.addLayout(self.cards_layout)
        self.layout.addStretch()

    def create_card(self, title_text, content_text):
        card = QFrame()
        card.setProperty("class", "Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(title_text)
        title.setProperty("class", "SectionTitle")
        title.setWordWrap(True)
        card_layout.addWidget(title)

        content = QLabel(content_text)
        content.setWordWrap(True)
        content.setStyleSheet("color: #1F2937; font-size: 28px; font-weight: bold;")
        
        card.content_label = content
        card_layout.addWidget(content)
        card_layout.addStretch()
        
        return card

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clear_layout(item.layout())

    def create_banner(self, text):
        banner = QFrame()
        banner.setStyleSheet("background-color: #FEE2E2; border-left: 4px solid #EF4444; border-radius: 4px;")
        l = QHBoxLayout(banner)
        l.setContentsMargins(15, 15, 15, 15)
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #991B1B; font-weight: bold; font-size: 14px;")
        l.addWidget(lbl)
        return banner

    def load_data(self):
        stats = self.controller.get_estatisticas()
        
        # Atualizar Cards
        self.card_pacientes.content_label.setText(str(stats['total_pacientes']))
        self.card_consultas.content_label.setText(str(stats['consultas_mes']))
        self.card_vacinas.content_label.setText(str(stats['vacinas_pendentes']))
        
        prox_ag = stats['proximo_agendamento']
        if len(prox_ag) > 22:
            prox_ag = prox_ag[:20] + "..."
            
        self.card_agenda.content_label.setText(prox_ag)
        self.card_agenda.content_label.setStyleSheet("color: #4B5563; font-size: 14px; font-weight: normal;")

        # Atualizar Banners
        self.clear_layout(self.banners_layout)
        for alert in stats['alertas']:
            self.banners_layout.addWidget(self.create_banner(alert))
