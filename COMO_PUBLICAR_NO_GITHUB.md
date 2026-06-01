# Como publicar no GitHub e gerar um link

## 1) Criar repositório no GitHub
Crie um repositório com o nome:

```bash
fairhire-ai
```

## 2) Subir o projeto pelo terminal do VS Code
Dentro da pasta do projeto, execute:

```bash
git init
git add .
git commit -m "Projeto FairHire AI"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/fairhire-ai.git
git push -u origin main
```

> Troque `SEU_USUARIO` pelo seu usuário do GitHub.

## 3) Gerar o link com Streamlit Cloud
Depois de subir o projeto:

1. Acesse o Streamlit Community Cloud.
2. Faça login com GitHub.
3. Clique em **New app**.
4. Escolha seu repositório `fairhire-ai`.
5. Defina o arquivo principal como:

```bash
app.py
```

6. Clique em **Deploy**.

## 4) Resultado
Você terá um link público do tipo:

```bash
https://fairhire-ai.streamlit.app
```

## 5) Plano B
No dia da apresentação, deixe também rodando localmente com:

```bash
streamlit run app.py
```

Assim, mesmo se a internet falhar, você apresenta pelo navegador local.
