import io
import re
from typing import Dict, Tuple

import streamlit as st

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    import docx
except Exception:
    docx = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None

st.set_page_config(page_title="SKILLMATCH AI", page_icon="🟢", layout="wide")

# -----------------------------
# Funções
# -----------------------------

def extract_text(file_name: str, file_bytes: bytes) -> str:
    name = file_name.lower()

    if name.endswith('.pdf') and PdfReader is not None:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
        return "\n".join(pages).strip()

    if name.endswith('.docx') and docx is not None:
        d = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in d.paragraphs).strip()

    # fallback para txt / outros
    for enc in ('utf-8', 'latin-1'):
        try:
            return file_bytes.decode(enc, errors='ignore').strip()
        except Exception:
            pass
    return ""


def mask_personal_data(text: str, candidate_name: str = "", company_name: str = "") -> Tuple[str, Dict[str, int]]:
    counts = {
        "emails": 0,
        "telefones": 0,
        "links": 0,
        "cpf": 0,
        "enderecos": 0,
        "nome": 0,
        "empresa": 0,
    }

    masked = text

    patterns = [
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[EMAIL_REMOVIDO]", "emails"),
        (r"(\+?55\s*)?(\(?\d{2}\)?\s*)?(9?\d{4})[-\s]?(\d{4})", "[TELEFONE_REMOVIDO]", "telefones"),
        (r"\b(https?://\S+|www\.\S+)\b", "[LINK_REMOVIDO]", "links"),
        (r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b", "[CPF_REMOVIDO]", "cpf"),
        (r"\b(rua|avenida|av\.|travessa|alameda|praça|rodovia)\b[^\n]{0,80}\b\d{1,6}\b", "[ENDERECO_REMOVIDO]", "enderecos"),
    ]

    for pat, repl, key in patterns:
        regex = re.compile(pat, re.IGNORECASE)
        masked, n = regex.subn(repl, masked)
        counts[key] += n

    if candidate_name.strip():
        regex = re.compile(re.escape(candidate_name.strip()), re.IGNORECASE)
        masked, n = regex.subn("[NOME_REMOVIDO]", masked)
        counts["nome"] += n

    if company_name.strip():
        regex = re.compile(re.escape(company_name.strip()), re.IGNORECASE)
        masked, n = regex.subn("[EMPRESA_REMOVIDA]", masked)
        counts["empresa"] += n

    return masked, counts


def fit_score(cv_text: str, job_text: str) -> float:
    if TfidfVectorizer is None:
        return 0.0
    docs = [job_text, cv_text]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=4000)
    matrix = vectorizer.fit_transform(docs)
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return float(score * 100)


def keyword_match(cv_text: str, keywords: str):
    items = [k.strip().lower() for k in keywords.split(',') if k.strip()]
    text = cv_text.lower()
    found = [k for k in items if re.search(r"\b" + re.escape(k) + r"\b", text)]
    return len(found), len(items), found


# -----------------------------
# Interface
# -----------------------------

st.title("🟢 SKILLMATCH AI")
st.caption("MVP acadêmico: anonimização de currículos e ranking por aderência à vaga.")

with st.sidebar:
    st.header("Sobre o projeto")
    st.write(
        "Este MVP demonstra uma plataforma web para reduzir vieses iniciais no recrutamento, "
        "removendo dados pessoais e calculando a aderência do candidato à vaga."
    )
    st.info("Dica: para a apresentação, use 2 currículos diferentes para mostrar o ranking.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1) Dados da vaga")
    vaga = st.text_input("Título da vaga", value="Analista de Suporte / Sustentação")
    desc_vaga = st.text_area(
        "Descrição da vaga",
        value=(
            "Responsável por suporte a sistemas corporativos, análise de incidentes, atendimento ao usuário, "
            "documentação, e melhoria contínua.\n\n"
            "Requisitos: SQL básico, noções de ERP, boa comunicação, troubleshooting, ITIL."
        ),
        height=180,
    )
    palavras = st.text_input(
        "Palavras-chave (separadas por vírgula)",
        value="SQL, ERP, ITIL, troubleshooting, atendimento, documentação",
    )

with col2:
    st.subheader("2) Currículos")
    files = st.file_uploader(
        "Envie arquivos .pdf, .docx ou .txt",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    st.markdown("**Opcional para melhorar a anonimização**")
    candidate_name = st.text_input("Nome do candidato (opcional)")
    company_name = st.text_input("Empresa/Instituição a mascarar (opcional)")

if st.button("Analisar currículos", type="primary", use_container_width=True):
    if not files:
        st.warning("Envie pelo menos um currículo para analisar.")
    else:
        resultados = []
        for f in files:
            original = extract_text(f.name, f.getvalue())
            anonimizado, contagem = mask_personal_data(original, candidate_name, company_name)
            score = fit_score(anonimizado, desc_vaga)
            achadas, total, lista = keyword_match(anonimizado, palavras)
            resultados.append({
                "arquivo": f.name,
                "score": round(score, 1),
                "keywords": f"{achadas}/{total}",
                "lista": ", ".join(lista) if lista else "-",
                "contagem": contagem,
                "anonimizado": anonimizado,
                "original": original,
            })

        resultados.sort(key=lambda x: x["score"], reverse=True)

        st.success("Análise concluída com sucesso!")
        st.subheader("3) Ranking")
        for i, r in enumerate(resultados, start=1):
            with st.expander(f"#{i} — {r['arquivo']} | Fit: {r['score']}% | Keywords: {r['keywords']}", expanded=(i == 1)):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Resumo da análise**")
                    st.write({
                        "Vaga": vaga,
                        "Fit": f"{r['score']}%",
                        "Palavras-chave encontradas": r['keywords'],
                        "Lista": r['lista'],
                    })
                    st.markdown("**Dados mascarados**")
                    st.json(r["contagem"], expanded=False)
                with c2:
                    st.markdown("**Currículo anonimizado**")
                    st.text_area("", value=r["anonimizado"], height=260)
                st.markdown("**Texto original (apenas para comparação na demo)**")
                st.text_area(" ", value=r["original"], height=180)

st.divider()

