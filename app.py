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


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="SKILLMATCH AI",
    page_icon="🟢",
    layout="wide"
)


# =========================================================
# CSS - DARK PREMIUM
# =========================================================
st.markdown(
    """
    <style>
    /* =====================================================
       BASE GERAL / FUNDO
    ===================================================== */
    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(37, 99, 235, 0.16), transparent 22%),
            radial-gradient(circle at 85% 15%, rgba(14, 165, 233, 0.12), transparent 20%),
            radial-gradient(circle at 30% 80%, rgba(59, 130, 246, 0.10), transparent 25%),
            linear-gradient(135deg, #050b16 0%, #08111f 35%, #0b1730 70%, #0d1b38 100%);
        color: #e5eefc;
    }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .block-container {
        max-width: 1180px;
        padding-top: 1.8rem;
        padding-bottom: 2.2rem;
    }

    /* =====================================================
       HERO
    ===================================================== */
    .hero-box {
        background:
            radial-gradient(circle at 15% 20%, rgba(96, 165, 250, 0.18), transparent 22%),
            linear-gradient(135deg, #08101f 0%, #0c1730 35%, #12264f 70%, #1d4ed8 100%);
        padding: 36px 38px;
        border-radius: 28px;
        margin-bottom: 22px;
        box-shadow: 0 22px 44px rgba(0, 0, 0, 0.34);
        border: 1px solid rgba(255,255,255,0.08);
        overflow: hidden;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.10);
        color: #ffffff;
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.10);
    }

    .hero-title {
        color: #ffffff;
        font-size: 46px;
        font-weight: 850;
        line-height: 1.08;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        color: #dbeafe;
        font-size: 17px;
        line-height: 1.75;
        max-width: 930px;
    }

    /* =====================================================
       BENEFÍCIOS
    ===================================================== */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-top: 8px;
        margin-bottom: 22px;
    }

    .feature-card {
        background: rgba(12, 23, 48, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 20px;
        padding: 18px;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
        backdrop-filter: blur(8px);
    }

    .feature-title {
        color: #f8fbff;
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .feature-text {
        color: #b8c7e6;
        font-size: 13px;
        line-height: 1.6;
    }

    /* =====================================================
       SIDEBAR
    ===================================================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050b16 0%, #0b1730 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* =====================================================
       TÍTULOS
    ===================================================== */
    .section-heading {
        font-size: 24px;
        font-weight: 850;
        color: #f8fbff;
        margin-top: 6px;
        margin-bottom: 4px;
    }

    .section-desc {
        font-size: 14px;
        color: #9db0d4;
        margin-bottom: 18px;
        line-height: 1.55;
    }

    /* =====================================================
       CONTAINERS NATIVOS
    ===================================================== */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(10, 18, 35, 0.84);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 22px;
        box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
        padding: 8px;
    }

    /* =====================================================
       LABELS / TEXTOS
    ===================================================== */
    label {
        color: #dbe7fb !important;
        font-weight: 650 !important;
    }

    .stMarkdown p,
    .stCaption,
    .stText {
        color: #dbe7fb !important;
    }

    /* =====================================================
       INPUTS / TEXTAREAS / CURSOR VISÍVEL
    ===================================================== */
    .stTextInput > div > div > input,
    .stTextArea textarea {
        background: #0d1729 !important;
        color: #f8fbff !important;
        border: 1px solid #29406d !important;
        border-radius: 16px !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 4px 12px rgba(0, 0, 0, 0.16);
        caret-color: #60a5fa !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border: 1px solid #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18) !important;
        caret-color: #93c5fd !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #7f93b8 !important;
        opacity: 1 !important;
    }

    /* =====================================================
       FILE UPLOADER
    ===================================================== */
    [data-testid="stFileUploader"] {
        background: rgba(13, 23, 41, 0.9);
        border: 1.5px dashed #38548a;
        border-radius: 18px;
        padding: 14px;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.18);
    }

    [data-testid="stFileUploader"] section {
        padding: 8px !important;
    }

    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] div {
        color: #d9e7ff !important;
    }

    /* =====================================================
       BOTÃO
    ===================================================== */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #0a1836 0%, #163b8c 52%, #2563eb 100%);
        color: white !important;
        border: none !important;
        border-radius: 18px !important;
        padding: 16px 18px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        box-shadow: 0 14px 26px rgba(0, 0, 0, 0.24);
        transition: all 0.22s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 18px 30px rgba(0, 0, 0, 0.30);
        background: linear-gradient(90deg, #08101f 0%, #123373 58%, #1d4ed8 100%);
    }

    /* =====================================================
       KPI CARDS
    ===================================================== */
    .kpi-box {
        background: linear-gradient(180deg, rgba(12, 23, 48, 0.96) 0%, rgba(10, 18, 35, 0.96) 100%);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
    }

    .kpi-label {
        font-size: 13px;
        font-weight: 750;
        color: #9fb3d8;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 900;
        color: #f8fbff;
    }

    /* =====================================================
       MELHOR CANDIDATO
    ===================================================== */
    .winner-card {
        background:
            radial-gradient(circle at top right, rgba(96, 165, 250, 0.14), transparent 28%),
            linear-gradient(135deg, #08101f 0%, #0d1e3f 62%, #18439b 100%);
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 24px;
        box-shadow: 0 18px 34px rgba(0, 0, 0, 0.28);
        margin-top: 8px;
        margin-bottom: 18px;
    }

    .winner-eyebrow {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.10);
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 14px;
    }

    .winner-title {
        color: #ffffff;
        font-size: 24px;
        font-weight: 850;
        margin-bottom: 8px;
    }

    .winner-subtitle {
        color: #dbeafe;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 16px;
    }

    .winner-metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 6px;
    }

    .winner-metric {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 14px;
    }

    .winner-metric-label {
        color: #c7ddff;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .winner-metric-value {
        color: #ffffff;
        font-size: 22px;
        font-weight: 850;
    }

    /* =====================================================
       EXPANDERS
    ===================================================== */
    .streamlit-expanderHeader {
        font-size: 15px;
        font-weight: 850;
        color: #f8fbff;
    }

    /* =====================================================
       ALERTAS
    ===================================================== */
    [data-testid="stSuccessMessage"],
    [data-testid="stWarning"],
    [data-testid="stInfo"] {
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.16);
        background: rgba(10, 18, 35, 0.92);
        color: #f8fbff !important;
    }

    /* =====================================================
       TAGS
    ===================================================== */
    .tag-high, .tag-medium, .tag-low {
        display: inline-block;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 12px;
        font-weight: 850;
        margin-bottom: 10px;
    }

    .tag-high {
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.28);
        color: #9ae6bf;
    }

    .tag-medium {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.28);
        color: #fcd34d;
    }

    .tag-low {
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.22);
        color: #fca5a5;
    }

    /* =====================================================
       JSON / TEXTAREA VISUAL
    ===================================================== */
    pre, code {
        color: #e5eefc !important;
    }

    /* =====================================================
       RODAPÉ
    ===================================================== */
    .caption-center {
        text-align: center;
        color: #95a8cb;
        font-size: 13px;
        margin-top: 26px;
    }

    .stTextInput, .stTextArea, .stFileUploader {
        margin-bottom: 12px;
    }

    @media (max-width: 900px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }

        .winner-metrics {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 36px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FUNÇÕES
# =========================================================
def extract_text(file_name: str, file_bytes: bytes) -> str:
    name = file_name.lower()

    if name.endswith(".pdf") and PdfReader is not None:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pages.append("")
        return "\n".join(pages).strip()

    if name.endswith(".docx") and docx is not None:
        document = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    for encoding in ("utf-8", "latin-1"):
        try:
            return file_bytes.decode(encoding, errors="ignore").strip()
        except Exception:
            pass

    return ""


def mask_personal_data(
    text: str,
    candidate_name: str = "",
    company_name: str = ""
) -> Tuple[str, Dict[str, int]]:
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

    for pattern, replacement, key in patterns:
        regex = re.compile(pattern, re.IGNORECASE)
        masked, matches = regex.subn(replacement, masked)
        counts[key] += matches

    if candidate_name.strip():
        regex = re.compile(re.escape(candidate_name.strip()), re.IGNORECASE)
        masked, matches = regex.subn("[NOME_REMOVIDO]", masked)
        counts["nome"] += matches

    if company_name.strip():
        regex = re.compile(re.escape(company_name.strip()), re.IGNORECASE)
        masked, matches = regex.subn("[EMPRESA_REMOVIDA]", masked)
        counts["empresa"] += matches

    return masked, counts


def fit_score(cv_text: str, job_text: str) -> float:
    if TfidfVectorizer is None or cosine_similarity is None:
        return 0.0

    docs = [job_text, cv_text]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=4000)
    matrix = vectorizer.fit_transform(docs)
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return float(score * 100)


def keyword_match(cv_text: str, keywords: str):
    items = [item.strip().lower() for item in keywords.split(",") if item.strip()]
    text = cv_text.lower()
    found = [item for item in items if re.search(r"\b" + re.escape(item) + r"\b", text)]
    return len(found), len(items), found


def render_fit_tag(score: float):
    if score >= 70:
        st.markdown('<div class="tag-high">Alta aderência</div>', unsafe_allow_html=True)
    elif score >= 40:
        st.markdown('<div class="tag-medium">Aderência moderada</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="tag-low">Baixa aderência</div>', unsafe_allow_html=True)


# =========================================================
# HERO
# =========================================================
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-badge">• Recrutamento Inteligente</div>
        <div class="hero-title">🟢 SKILLMATCH AI</div>
        <div class="hero-subtitle">
            Plataforma de triagem curricular com anonimização de dados e análise de aderência entre candidato e vaga,
            apoiando uma avaliação mais eficiente, estruturada e com menor viés inicial.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# BENEFÍCIOS
# =========================================================
st.markdown(
    """
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-title">Anonimização Inteligente</div>
            <div class="feature-text">
                Redução de vieses na triagem inicial por meio da remoção automática de dados sensíveis do currículo.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-title">Matching com Aderência</div>
            <div class="feature-text">
                Comparação entre currículo e vaga com score percentual, análise textual e conferência por palavras-chave.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-title">Ranking para Decisão</div>
            <div class="feature-text">
                Organização dos candidatos por relevância para apoiar uma triagem mais rápida, clara e objetiva.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## Sobre o projeto")
    st.write(
        "O SKILLMATCH AI é um MVP acadêmico voltado à triagem inicial de currículos, "
        "com foco em anonimização, aderência à vaga e apoio à decisão."
    )

    st.markdown("### Funcionalidades")
    st.markdown("""
    - Anonimização de dados pessoais  
    - Matching entre currículo e vaga  
    - Análise por palavras-chave  
    - Ranking de aderência  
    - Visualização comparativa para demonstração  
    """)

    st.markdown("### Onde está a IA?")
    st.write(
        "A inteligência do sistema está no matching textual entre o conteúdo do currículo "
        "e a descrição da vaga, além da análise por palavras-chave e aderência."
    )

    if TfidfVectorizer is None:
        st.info("Se o fit aparecer 0%, instale o pacote scikit-learn.")


descricao_padrao = (
    "Responsável por suporte a sistemas corporativos, análise de incidentes, atendimento ao usuário, "
    "documentação e melhoria contínua.\n\n"
    "Requisitos: SQL básico, noções de ERP, boa comunicação, troubleshooting e ITIL."
)

if "desc_vaga" not in st.session_state:
    st.session_state.desc_vaga = descricao_padrao


# =========================================================
# FORMULÁRIO
# =========================================================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    with st.container(border=True):
        st.markdown('<div class="section-heading">1) Dados da vaga</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-desc">Defina os critérios usados na comparação dos currículos.</div>',
            unsafe_allow_html=True
        )

        vaga = st.text_input(
            "Título da vaga",
            value="Analista de Suporte / Sustentação"
        )

        desc_vaga = st.text_area(
    "Descrição da vaga",
    key="desc_vaga",
    height=220
)

        palavras = st.text_input(
            "Palavras-chave (separadas por vírgula)",
            value="SQL, ERP, ITIL, troubleshooting, atendimento, documentação"
        )

with col2:
    with st.container(border=True):
        st.markdown('<div class="section-heading">2) Currículos</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-desc">Envie arquivos PDF, DOCX ou TXT para análise.</div>',
            unsafe_allow_html=True
        )

        files = st.file_uploader(
            "Envie arquivos .pdf, .docx ou .txt",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )

        st.markdown("### Anonimização")
        candidate_name = st.text_input("Nome do candidato (opcional)")
        company_name = st.text_input("Empresa/Instituição a mascarar (opcional)")


st.write("")

# =========================================================
# BOTÃO E RESULTADO
# =========================================================
if st.button("Analisar currículos", type="primary", use_container_width=True):
    if not files:
        st.warning("Envie pelo menos um currículo para analisar.")
    else:
        resultados = []

        for file in files:
            original = extract_text(file.name, file.getvalue())
            anonimizado, contagem = mask_personal_data(original, candidate_name, company_name)
            score = fit_score(anonimizado, desc_vaga)
            achadas, total, lista = keyword_match(anonimizado, palavras)

            resultados.append(
                {
                    "arquivo": file.name,
                    "score": round(score, 1),
                    "keywords_encontradas": achadas,
                    "keywords_total": total,
                    "keywords_ratio": f"{achadas}/{total}",
                    "lista": ", ".join(lista) if lista else "-",
                    "contagem": contagem,
                    "anonimizado": anonimizado,
                    "original": original,
                }
            )

        resultados.sort(key=lambda item: item["score"], reverse=True)

        melhor_fit = resultados[0]["score"] if resultados else 0
        media_fit = round(sum(item["score"] for item in resultados) / len(resultados), 1) if resultados else 0
        total_arquivos = len(resultados)
        top_resultado = resultados[0] if resultados else None

        st.success("Análise concluída com sucesso!")

        k1, k2, k3 = st.columns(3)

        with k1:
            st.markdown(
                f"""
                <div class="kpi-box">
                    <div class="kpi-label">Currículos analisados</div>
                    <div class="kpi-value">{total_arquivos}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with k2:
            st.markdown(
                f"""
                <div class="kpi-box">
                    <div class="kpi-label">Melhor fit</div>
                    <div class="kpi-value">{melhor_fit}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with k3:
            st.markdown(
                f"""
                <div class="kpi-box">
                    <div class="kpi-label">Média de aderência</div>
                    <div class="kpi-value">{media_fit}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        if top_resultado is not None:
            st.markdown(
                f"""
                <div class="winner-card">
                    <div class="winner-eyebrow">Melhor aderência identificada</div>
                    <div class="winner-title">{top_resultado['arquivo']}</div>
                    <div class="winner-subtitle">
                        Este currículo apresentou a melhor compatibilidade com a vaga informada,
                        reunindo o maior score de aderência textual entre os arquivos analisados.
                    </div>
                    <div class="winner-metrics">
                        <div class="winner-metric">
                            <div class="winner-metric-label">Fit</div>
                            <div class="winner-metric-value">{top_resultado['score']}%</div>
                        </div>
                        <div class="winner-metric">
                            <div class="winner-metric-label">Keywords</div>
                            <div class="winner-metric-value">{top_resultado['keywords_ratio']}</div>
                        </div>
                        <div class="winner-metric">
                            <div class="winner-metric-label">Vaga</div>
                            <div class="winner-metric-value" style="font-size:15px;">{vaga}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("## 3) Ranking dos currículos")
        st.caption("Os currículos são ordenados automaticamente do maior para o menor nível de aderência com a vaga.")

        for index, resultado in enumerate(resultados, start=1):
            with st.expander(
                f"#{index} — {resultado['arquivo']} | Fit: {resultado['score']}% | Keywords: {resultado['keywords_ratio']}",
                expanded=(index == 1)
            ):
                render_fit_tag(resultado["score"])
                st.progress(min(max(int(resultado["score"]), 0), 100))

                c1, c2 = st.columns(2, gap="large")

                with c1:
                    with st.container(border=True):
                        st.markdown("**Resumo da análise**")
                        st.write(
                            {
                                "Vaga": vaga,
                                "Fit": f"{resultado['score']}%",
                                "Palavras-chave encontradas": resultado["keywords_ratio"],
                                "Lista encontrada": resultado["lista"],
                            }
                        )

                        st.markdown("**Dados mascarados**")
                        st.json(resultado["contagem"], expanded=False)

                with c2:
                    with st.container(border=True):
                        st.markdown("**Currículo anonimizado**")
                        st.text_area(
                            "Texto anonimizado",
                            value=resultado["anonimizado"],
                            height=260,
                            key=f"anon_{index}"
                        )

                st.markdown("**Texto original**")
                st.text_area(
                    "Texto original",
                    value=resultado["original"],
                    height=180,
                    key=f"orig_{index}"
                )


# =========================================================
# RODAPÉ
# =========================================================
st.markdown(
    '<div class="caption-center">SKILLMATCH AI • Recrutamento com Matching Inteligente</div>',
    unsafe_allow_html=True
)
