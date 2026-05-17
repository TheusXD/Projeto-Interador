<h1 align="center">PROJETO INTEGRADOR</h1>
<h2 align="center">Ferramenta Desktop para Gestão de Consultório Pediátrico</h2>

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt-6-green.svg)
![SQLite](https://img.shields.io/badge/sqlite-3-blue.svg)

## Descrição do Projeto
Este projeto é um **Projeto Integrador do curso da UNIVESP**, e tem como objetivo criar uma aplicação desktop amigável e funcional para suporte pediátrico. Desenvolvido em Python com PyQt6 e banco de dados SQLite, o sistema oferece recursos essenciais como registro de pacientes, acompanhamento de consultas, gestão de vacinas, monitoramento de crescimento e agendamento de horários. Tudo é organizado através de uma interface limpa, intuitiva e moderna, projetada para facilitar o dia a dia e usuários com o mínimo de conhecimento técnico.

### Funcionalidades
- **Dashboard Informativo:** Visão global de consultas do mês, total de pacientes e avisos de vacinas em atraso ou agendamentos diários (banners visuais).
- **Gestão de Pacientes (CRUD):** Inserção, edição via duplo-clique e exclusão em cascata (com avisos).
- **Calendário Vacinal Automatizado (SUS):** Ao registrar um novo paciente, as primeiras vacinas (BCG, Hep B, Penta, VIP, Rotavírus) são pré-agendadas como pendentes.
- **Consultas e Agendamentos:** Registro de prescrições, diagnósticos e sistema de agenda (integrado ao dashboard).
- **Monitoramento de Crescimento (Padrão OMS):**
  - Plotagem automática das curvas P3, P50 e P97 de acordo com as referências mundiais de desenvolvimento infantil.
  - Interação "Tooltip" no gráfico mostrando valores de peso, altura e data exatos.
  - Cálculo automático de IMC.
- **Prontuário Eletrônico:**
  - Visão unificada via abas (Dados Cadastrais, Vacinas, Consultas, Crescimento).
  - Exportação completa do histórico médico e dados do paciente para PDF via `ReportLab`.

## Pré-requisitos

Antes de executar o projeto, certifique-se de ter os seguintes pré-requisitos instalados em seu sistema:

- Python 3.10 ou superior: [Download Python](https://www.python.org/downloads/)

## Como Rodar o Projeto

### Configuração Inicial

1. Navegue até o diretório do projeto:

```bash
cd caminho/para/AppPI
```

2. Crie um ambiente virtual e o ative:

- **Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- **Linux/macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

3. Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

*(Dependências principais: PyQt6, matplotlib, reportlab)*

### Execução

Para iniciar o aplicativo, execute o arquivo principal:

```bash
python main.py
```

### Gerar Executável (Windows)

O sistema pode ser compilado para um executável autônomo `.exe` usando `PyInstaller`:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --add-data "database;database/" --name "Sistema Pediatrico" main.py
```
O executável final estará disponível na pasta `dist/Sistema Pediatrico/`.

## Desenvolvedores

Projeto desenvolvido pelos alunos:
- Bruno Coelho Tini
- Felipe Camargo da Silva
- Matheus da Silva Pinto
