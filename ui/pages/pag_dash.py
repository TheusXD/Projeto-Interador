from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from controllers.tudo_junto_controllers import ControladorAgenda

class PagDash(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.agenda_controller = ControladorAgenda(db_manager)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        title = QLabel("Dashboard")
        title.setProperty("class", "PageTitle")
        self.layout.addWidget(title)

        # Container para cards
        cards_layout = QHBoxLayout()
        
        # Card 1: Consultas Hoje/Próximas
        self.card_consultas = self.create_card("Próximos Agendamentos", "")
        cards_layout.addWidget(self.card_consultas)

        # Card 2: Vacinas Pendentes (Resumo)
        self.card_vacinas = self.create_card("Resumo", "Bem-vindo ao Sistema de Apoio Pediátrico!")
        cards_layout.addWidget(self.card_vacinas)

        self.layout.addLayout(cards_layout)
        self.layout.addStretch()

    def create_card(self, title_text, content_text):
        card = QFrame()
        card.setProperty("class", "Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(title_text)
        title.setProperty("class", "SectionTitle")
        card_layout.addWidget(title)

        content = QLabel(content_text)
        content.setWordWrap(True)
        content.setStyleSheet("color: #4B5563; font-size: 14px;")
        
        # Guardar referência ao label de conteúdo se precisar atualizar
        card.content_label = content
        card_layout.addWidget(content)
        card_layout.addStretch()
        
        return card

    def load_data(self):
        # Atualizar dados do dashboard
        agendamentos = self.agenda_controller.listar_agendamentos(limite_dias=7) # próximos 7 dias
        if not agendamentos:
            self.card_consultas.content_label.setText("Nenhum agendamento para os próximos 7 dias.")
        else:
            texto = ""
            for a in agendamentos[:5]: # Mostrar até 5
                texto += f"• {a['data_hora'][:16]} - {a['paciente_nome']} ({a['tipo']})\n"
            self.card_consultas.content_label.setText(texto)
