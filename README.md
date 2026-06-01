# FairHire AI - Projeto completo (MVP Web)

Este é um **projeto completo** de uma plataforma web de **recrutamento com currículo cego**, feito para apresentação acadêmica.

## O que esse projeto faz
- Recebe uma **descrição de vaga**
- Permite **upload de currículos** (`.pdf`, `.docx`, `.txt`)
- **Mascara dados sensíveis** (e-mail, telefone, CPF, links e endereço)
- Calcula um **fit score** baseado em aderência textual
- Mostra um **ranking dos candidatos**

## Estrutura do projeto
```bash
fairhire_site_completo/
  app.py
  requirements.txt
  README.md
  .gitignore
  sample_job.txt
  sample_cv_1.txt
  sample_cv_2.txt
  COMO_PUBLICAR_NO_GITHUB.md
  ROTEIRO_APRESENTACAO.md
```

## 1) Como rodar localmente no VS Code

### Pré-requisitos
- Python 3.10 ou superior
- VS Code
- Terminal/PowerShell

### Passo a passo
Abra a pasta do projeto no VS Code e rode:

```bash
python -m venv .venv
```

#### Windows (PowerShell)
```bash
.venv\Scriptsctivate
```

#### Mac/Linux
```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o site:

```bash
streamlit run app.py
```

O sistema abrirá no navegador em algo como:

```bash
http://localhost:8501
```

## 2) Como publicar no GitHub
Consulte o arquivo `COMO_PUBLICAR_NO_GITHUB.md`.

## 3) Como gerar um link público (site web)
A forma mais simples é usar o **Streamlit Community Cloud**.

Passos resumidos:
1. Suba os arquivos no GitHub.
2. Acesse o Streamlit Community Cloud.
3. Conecte sua conta GitHub.
4. Selecione seu repositório.
5. Escolha o arquivo `app.py`.
6. Clique em **Deploy**.

## 4) Arquivos de exemplo
- `sample_job.txt` → descrição da vaga
- `sample_cv_1.txt` → currículo com boa aderência
- `sample_cv_2.txt` → currículo com menor aderência

## 5) O que falar para o professor
Consulte o arquivo `ROTEIRO_APRESENTACAO.md`.
