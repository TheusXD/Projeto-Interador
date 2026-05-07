import os

renames = {
    "main.py": "rodar_app_v2_final.py",
    "database/db_manager.py": "database/banco_db.py",
    "controllers/geral_controllers.py": "controllers/tudo_junto_controllers.py",
    "controllers/paciente_controller.py": "controllers/paciente_dao_controller.py",
    "ui/main_window.py": "ui/tela_principal_new.py",
    "ui/styles.py": "ui/estilo_do_app.py",
    "ui/pages/dashboard_page.py": "ui/pages/pag_dash.py",
    "ui/pages/pacientes_page.py": "ui/pages/tela_paciente_definitivo.py",
    "ui/pages/consultas_page.py": "ui/pages/consulta_front.py",
    "ui/pages/vacinas_page.py": "ui/pages/view_vacinas.py",
    "ui/pages/crescimento_page.py": "ui/pages/grafico_peso_altura.py",
    "ui/pages/agenda_page.py": "ui/pages/agenda_teste.py",
}

replacements = {
    "database.banco_db": "database.banco_db",
    "controllers.tudo_junto_controllers": "controllers.tudo_junto_controllers",
    "controllers.paciente_dao_controller": "controllers.paciente_dao_controller",
    "ui.tela_principal_new": "ui.tela_principal_new",
    "ui.estilo_do_app": "ui.estilo_do_app",
    "ui.pages.pag_dash": "ui.pages.pag_dash",
    "ui.pages.tela_paciente_definitivo": "ui.pages.tela_paciente_definitivo",
    "ui.pages.consulta_front": "ui.pages.consulta_front",
    "ui.pages.view_vacinas": "ui.pages.view_vacinas",
    "ui.pages.grafico_peso_altura": "ui.pages.grafico_peso_altura",
    "ui.pages.agenda_teste": "ui.pages.agenda_teste",
    
    "PagDash": "PagDash",
    "TelaPacienteDef": "TelaPacienteDef",
    "FrontConsulta": "FrontConsulta",
    "ViewVacinas": "ViewVacinas",
    "GraficosPesoAltura": "GraficosPesoAltura",
    "AgendaApp": "AgendaApp",
    "GerenciaDB": "GerenciaDB",
    "TelaPrincipalApp": "TelaPrincipalApp",
    "CSS_DO_APP": "CSS_DO_APP",
    "ControladorDoPaciente": "ControladorDoPaciente",
    "ControladorDasConsultas": "ControladorDasConsultas",
    "ControlaAsVacinas": "ControlaAsVacinas",
    "Crescimento_Grafico": "Crescimento_Grafico",
    "ControladorAgenda": "ControladorAgenda",
}

for root, _, files in os.walk("."):
    if "venv" in root: continue
    for file in files:
        if not file.endswith(".py"): continue
        filepath = os.path.join(root, file)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

for old_rel, new_rel in renames.items():
    old_path = os.path.abspath(old_rel)
    new_path = os.path.abspath(new_rel)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

print("Arquivos renomeados com sucesso!")
