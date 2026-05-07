CSS_DO_APP = """
QTelaPrincipalApp {
    background-color: #F0F4F8; /* Fundo suave claro */
}

/* Menu Lateral */
QWidget#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #D1D5DB;
}

QPushButton#MenuButton {
    text-align: left;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: bold;
    color: #4B5563;
    background-color: transparent;
    border: none;
    border-radius: 8px;
    margin: 4px 10px;
}

QPushButton#MenuButton:hover {
    background-color: #E5E7EB;
    color: #1F2937;
}

QPushButton#MenuButton:checked {
    background-color: #DBEAFE; /* Azul claro */
    color: #1D4ED8;
}

/* Área de Conteúdo Central */
QWidget#ContentArea {
    background-color: #F0F4F8;
}

/* Títulos */
QLabel.PageTitle {
    font-size: 24px;
    font-weight: bold;
    color: #1F2937;
    margin-bottom: 20px;
}

QLabel.SectionTitle {
    font-size: 18px;
    font-weight: bold;
    color: #374151;
    margin-top: 10px;
    margin-bottom: 10px;
}

/* Cards (Ex: no dashboard) */
QWidget.Card {
    background-color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
}

/* Botões de Ação */
QPushButton.PrimaryButton {
    background-color: #3B82F6; /* Azul */
    color: white;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}
QPushButton.PrimaryButton:hover { background-color: #2563EB; }

QPushButton.SuccessButton {
    background-color: #10B981; /* Verde */
    color: white;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}
QPushButton.SuccessButton:hover { background-color: #059669; }

QPushButton.DangerButton {
    background-color: #EF4444; /* Vermelho */
    color: white;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}
QPushButton.DangerButton:hover { background-color: #DC2626; }

/* Entradas de Texto e ComboBox */
QLineEdit, QComboBox, QTextEdit, QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px;
    font-size: 14px;
    color: #1F2937;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {
    border: 1px solid #3B82F6;
}

/* Tabelas */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    gridline-color: #F3F4F6;
    selection-background-color: #DBEAFE;
    selection-color: #1D4ED8;
}

QHeaderView::section {
    background-color: #F9FAFB;
    color: #4B5563;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #E5E7EB;
    font-weight: bold;
}
"""
