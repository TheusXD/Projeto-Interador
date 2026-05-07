import sys
import os

# Garantir que o diretório atual está no path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from database.banco_db import GerenciaDB
from ui.tela_principal_new import TelaPrincipalApp
from ui.estilo_do_app import CSS_DO_APP

def main():
    app = QApplication(sys.path)
    app.setStyleSheet(CSS_DO_APP)

    # Inicializar banco de dados
    db_manager = GerenciaDB("pediatria.db")

    # Inicializar e mostrar janela principal
    window = TelaPrincipalApp(db_manager)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
