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

# =============================
# CSS CUSTOMIZADO
# =============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #eef4ff 100%);
    color: #0f172a;
    font-family: 'Segoe UI', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
    padding: 32px 36px;
    border-radius: 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
}

.hero h1 {
    color: white;
    font-size: 40px;
    font-weight: 800;
    margin: 0;
}

.hero p {
    color: #dbeafe;
    font-size: 17px;
    margin-top: 10px;
    margin-bottom: 0;
    line-height: 1.5;
}

.badge {
    display: inline-block;
    background: rgba(255,255,255,0.16);
    color: #ffffff;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,0.18);
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
}

.custom-card {
    background: #ffffff;
    padding: 22px;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
    margin-bottom: 20px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

.sidebar-card {
    background: rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.10);
    margin-top: 12px;
}

.stTextInput > div > div > input,
.stTextArea textarea {
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #ffffff !important;
    padding: 12px 14px !important;
    font-size: 15px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border: 1px solid #2563eb !important;
    box-shadow: 0 0 0 1px #2563eb !important;
}

div[data-baseweb="select"] > div {
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    min-height: 48px !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    font-weight: 700;
    font-size: 16px;
    border: none;
    border-radius: 14px;
    padding: 14px 18px;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.25);
    transition: all 0.2s ease-in-out;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.32);
    background: linear-gradient(90deg, #1d4ed8 0%, #1e3a8a 100%);
}

.streamlit-expanderHeader {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
}

.metric-card {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border: 1px solid #bfdbfe;
    padding: 16px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 14px;
}

.metric-title {
    font-size: 13px;
    color: #334155;
    margin-bottom: 6px;
    font-weight: 600;
}

.metric-value {
    font-size: 28px;
    font-weight: 800;
    color: #1d4ed8;
}

.tag {
    display: inline-block;
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# FUNÇÕES
# =============================
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
        return "\\n".join(pages).strip()

    if name.endswith('.docx') and docx is not None:
        d = docx.Document(io.BytesIO(file_bytes))
        return "\\n".join(p.text for p in d.paragraphs).strip()

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
        (r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b", "[EMAIL_REMOVIDO]", "emails"),
        (r"(\\+?55\\s*)?(\\(?\\d{2}\\)?\\s*)?(9?\\d{4})[-\\s]?(\\d{4})", "[TELEFONE_REMOVIDO]", "telefones"),
        (r"\\b(https?://\\S+|www\\.\\S+)\\b", "[LINK_REMOVIDO]", "links"),
        (r"\\b\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}\\b|\\b\\d{11}\\b", "[CPF_REMOVIDO]", "cpf"),
        (r"\\b(rua|avenida|av\\.|travessa|alameda|praça|rodovia)\\b[^\\n]{0,80}\\b\\d{1,6}\\b", "[ENDERECO_REMOVIDO]", "enderecos"),
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
    found = [k for k in items if re.search(r"\\b" + re.escape(k) + r"\\b", text)]
    return len(found), len(items), found


# =============================
# INTERFACE
# =============================
st.markdown("""
<div class="hero">
    <div class="badge">MVP • Recrutamento Inteligente</div>
    <h1>🟢 SKILLMATCH AI</h1>
    <p>
        Plataforma de análise curricular com anonimização de dados e cálculo de aderência
        entre candidato e vaga, promovendo mais eficiência e redução de vieses na triagem inicial.
    </p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Sobre o projeto")
    st.markdown("""
    <div class="sidebar-card">
        <strong>SKILLMATCH AI</strong><br><br>
        Este MVP demonstra uma plataforma web voltada à triagem inicial de currículos,
        com foco em anonimização de dados pessoais e análise de compatibilidade com vagas.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Benefícios")
    st.markdown("""
    - Triagem mais justa  
    - Apoio à decisão no recrutamento  
    - Redução de vieses iniciais  
    - Estrutura pronta para evolução com IA  
    """)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1) Dados da vaga</div>', unsafe_allow_html=True)

    vaga = st.text_input("Título da vaga", value="Analista de Suporte / Sustentação")
    desc_vaga = st.text_area(
        "Descrição da vaga",
        value=(
            "Responsável por suporte a sistemas corporativos, análise de incidentes, atendimento ao usuário, "
            "documentação, e melhoria contínua.\\n\\n"
            "Requisitos: SQL básico, noções de ERP, boa comunicação, troubleshooting, ITIL."
        ),
        height=180,
    )
    palavras = st.text_input(
        "Palavras-chave (separadas por vírgula)",
        value="SQL, ERP, ITIL, troubleshooting, atendimento, documentação",
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2) Currículos</div>', unsafe_allow_html=True)

    files = st.file_uploader(
        "Envie arquivos .pdf, .docx ou .txt",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    st.markdown("**Opcional para melhorar a anonimização**")
    candidate_name = st.text_input("Nome do candidato (opcional)")
    company_name = st.text_input("Empresa/Instituição a mascarar (opcional)")
    st.markdown('</div>', unsafe_allow_html=True)

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
        st.subheader("3) Ranking dos currículos")

        for i, r in enumerate(resultados, start=1):
            with st.expander(f"#{i} — {r['arquivo']} | Fit: {r['score']}% | Keywords: {r['keywords']}", expanded=(i == 1)):
                st.progress(min(int(r["score"]), 100))

                if r["score"] >= 70:
                    st.markdown('<div class="tag">Alta aderência</div>', unsafe_allow_html=True)
                elif r["score"] >= 40:
                    st.markdown(
                        '<div class="tag" style="background:#fff7ed;color:#9a3412;border:1px solid #fdba74;">Aderência moderada</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="tag" style="background:#fef2f2;color:#991b1b;border:1px solid #fca5a5;">Baixa aderência</div>',
                        unsafe_allow_html=True
                    )

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