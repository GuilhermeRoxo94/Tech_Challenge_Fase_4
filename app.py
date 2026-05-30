import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Dashboard Executivo | Obesidade",
    page_icon="🏥",
    layout="wide"
)

# =========================
# Tema escuro estilo Power BI
# =========================
BACKGROUND = "#0F172A"
CARD = "#1E293B"
CARD_2 = "#111827"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
BLUE = "#3B82F6"
GREEN = "#10B981"
YELLOW = "#F59E0B"
RED = "#EF4444"
PURPLE = "#8B5CF6"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {BACKGROUND};
        color: {TEXT};
    }}

    [data-testid="stSidebar"] {{
        background-color: #020617;
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {TEXT} !important;
    }}

    .page-title {{
        font-size: 2.1rem;
        font-weight: 800;
        color: {TEXT};
        margin-bottom: 0.2rem;
    }}

    .page-subtitle {{
        font-size: 1rem;
        color: {MUTED};
        margin-bottom: 1.2rem;
    }}

    .kpi-card {{
        background: linear-gradient(180deg, #1E293B 0%, #111827 100%);
        padding: 20px 18px;
        border-radius: 18px;
        border: 1px solid #334155;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        min-height: 128px;
    }}

    .kpi-label {{
        font-size: 0.84rem;
        color: {MUTED};
        margin-bottom: 12px;
        font-weight: 600;
    }}

    .kpi-value {{
        font-size: 2.15rem;
        font-weight: 900;
        color: {TEXT};
        line-height: 1;
        white-space: nowrap;
    }}

    .kpi-footer {{
        margin-top: 10px;
        font-size: 0.78rem;
        color: {MUTED};
    }}

    .section-card {{
        background-color: {CARD};
        border: 1px solid #334155;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        margin-bottom: 16px;
    }}

    .insight-card {{
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-left: 6px solid {BLUE};
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
    }}

    .insight-title {{
        font-size: 0.9rem;
        color: {MUTED};
        font-weight: 700;
        margin-bottom: 8px;
    }}

    .insight-text {{
        font-size: 1.05rem;
        color: {TEXT};
        font-weight: 600;
    }}

    .risk-high {{
        color: {RED};
        font-weight: 800;
    }}

    .risk-medium {{
        color: {YELLOW};
        font-weight: 800;
    }}

    .risk-low {{
        color: {GREEN};
        font-weight: 800;
    }}

    div[data-testid="stMetricValue"] {{
        color: {TEXT};
    }}
</style>
""", unsafe_allow_html=True)


# =========================
# Dados
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("Obesity.csv")

    df["BMI"] = df["Weight"] / (df["Height"] ** 2)

    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[0, 18, 25, 35, 45, 60, 100],
        labels=["Até 18", "19-25", "26-35", "36-45", "46-60", "60+"]
    )

    df["Obesity_Group"] = df["Obesity"].replace({
        "Insufficient_Weight": "Abaixo do peso",
        "Normal_Weight": "Peso normal",
        "Overweight_Level_I": "Sobrepeso",
        "Overweight_Level_II": "Sobrepeso",
        "Obesity_Type_I": "Obesidade",
        "Obesity_Type_II": "Obesidade",
        "Obesity_Type_III": "Obesidade"
    })

    df["Obesity_Label_PT"] = df["Obesity"].replace({
        "Insufficient_Weight": "Abaixo do peso",
        "Normal_Weight": "Peso normal",
        "Overweight_Level_I": "Sobrepeso I",
        "Overweight_Level_II": "Sobrepeso II",
        "Obesity_Type_I": "Obesidade I",
        "Obesity_Type_II": "Obesidade II",
        "Obesity_Type_III": "Obesidade III"
    })

    # As variáveis FAF e CH2O vêm com valores decimais no dataset.
    # Para visualização executiva, agrupamos em categorias interpretáveis.
    df["FAF_Category"] = df["FAF"].round().clip(0, 3).astype(int).map({
        0: "0 - Não pratica",
        1: "1 - Baixa",
        2: "2 - Moderada",
        3: "3 - Alta"
    })

    df["CH2O_Category"] = df["CH2O"].round().clip(1, 3).astype(int).map({
        1: "1 - Baixo (<1L/dia)",
        2: "2 - Médio (1-2L/dia)",
        3: "3 - Alto (>2L/dia)"
    })

    return df

df = load_data()

obesity_order = [
    "Abaixo do peso",
    "Peso normal",
    "Sobrepeso I",
    "Sobrepeso II",
    "Obesidade I",
    "Obesidade II",
    "Obesidade III"
]

plotly_template = "plotly_dark"

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("## Filtros")

    gender_filter = st.multiselect(
        "Gênero",
        options=sorted(df["Gender"].dropna().unique()),
        default=sorted(df["Gender"].dropna().unique())
    )

    age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
    age_range = st.slider(
        "Faixa etária",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max)
    )

    family_filter = st.multiselect(
        "Histórico familiar",
        options=sorted(df["family_history"].dropna().unique()),
        default=sorted(df["family_history"].dropna().unique())
    )

    clinical_filter = st.multiselect(
        "Grupo clínico",
        options=["Abaixo do peso", "Peso normal", "Sobrepeso", "Obesidade"],
        default=["Abaixo do peso", "Peso normal", "Sobrepeso", "Obesidade"]
    )

filtered = df[
    (df["Gender"].isin(gender_filter)) &
    (df["Age"].between(age_range[0], age_range[1])) &
    (df["family_history"].isin(family_filter)) &
    (df["Obesity_Group"].isin(clinical_filter))
].copy()

# =========================
# Funções visuais
# =========================
def format_percent(value):
    return f"{value:.1f}%"

def format_number(value):
    return f"{value:,.0f}".replace(",", ".")

def kpi_card(col, label, value, footer, accent_color):
    col.markdown(
        f"""
        <div class="kpi-card" style="border-top: 4px solid {accent_color};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-footer">{footer}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def apply_dark_layout(fig, height=420):
    fig.update_layout(
        template=plotly_template,
        height=height,
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(color=TEXT),
        title=dict(font=dict(size=18, color=TEXT)),
        legend=dict(font=dict(color=TEXT)),
        margin=dict(l=30, r=30, t=65, b=40)
    )
    return fig

# =========================
# Header
# =========================
st.markdown('<div class="page-title">Painel Executivo de Indicadores Clínicos — Obesidade</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Análise estratégica de fatores de risco, perfil populacional e padrões comportamentais para suporte à decisão médica.</div>',
    unsafe_allow_html=True
)

# =========================
# KPIs
# =========================
total = len(filtered)
obesity_pct = filtered["Obesity_Group"].eq("Obesidade").mean() * 100 if total else 0
overweight_pct = filtered["Obesity_Group"].eq("Sobrepeso").mean() * 100 if total else 0
normal_pct = filtered["Obesity_Group"].eq("Peso normal").mean() * 100 if total else 0
avg_bmi = filtered["BMI"].mean() if total else 0
avg_age = filtered["Age"].mean() if total else 0
avg_weight = filtered["Weight"].mean() if total else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)

kpi_card(c1, "Pacientes analisados", format_number(total), "Base filtrada", BLUE)
kpi_card(c2, "Obesidade", format_percent(obesity_pct), "Tipos I, II e III", RED)
kpi_card(c3, "Sobrepeso", format_percent(overweight_pct), "Níveis I e II", YELLOW)
kpi_card(c4, "Peso normal", format_percent(normal_pct), "Classificação saudável", GREEN)
kpi_card(c5, "IMC médio", f"{avg_bmi:.1f}", "Índice de massa corporal", PURPLE)
kpi_card(c6, "Idade média", f"{avg_age:.1f}", "Anos", BLUE)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# Linha principal
# =========================
left, right = st.columns([1.35, 0.85])

dist = (
    filtered["Obesity_Label_PT"]
    .value_counts()
    .reindex(obesity_order)
    .dropna()
    .reset_index()
)
dist.columns = ["Classificação", "Quantidade"]

with left:
    fig = px.bar(
        dist,
        x="Classificação",
        y="Quantidade",
        text="Quantidade",
        title="Distribuição dos níveis de obesidade",
        color="Classificação",
        color_discrete_map={
            "Abaixo do peso": "#38BDF8",
            "Peso normal": GREEN,
            "Sobrepeso I": YELLOW,
            "Sobrepeso II": "#F97316",
            "Obesidade I": RED,
            "Obesidade II": "#DC2626",
            "Obesidade III": "#991B1B",
        }
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(tickangle=-25)
    fig = apply_dark_layout(fig, 470)
    st.plotly_chart(fig, use_container_width=True)

with right:
    group = filtered["Obesity_Group"].value_counts().reset_index()
    group.columns = ["Grupo", "Quantidade"]

    fig = px.pie(
        group,
        names="Grupo",
        values="Quantidade",
        hole=0.62,
        title="Composição clínica",
        color="Grupo",
        color_discrete_map={
            "Abaixo do peso": "#38BDF8",
            "Peso normal": GREEN,
            "Sobrepeso": YELLOW,
            "Obesidade": RED
        }
    )
    fig.update_traces(textinfo="percent+label")
    fig = apply_dark_layout(fig, 470)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# Segunda linha
# =========================
a, b, c = st.columns(3)

with a:
    age_risk = (
        filtered.groupby("Age_Group", observed=True)["Obesity_Group"]
        .apply(lambda x: (x == "Obesidade").mean() * 100)
        .reset_index(name="% Obesidade")
    )

    fig = px.bar(
        age_risk,
        x="Age_Group",
        y="% Obesidade",
        text=age_risk["% Obesidade"].map(lambda x: f"{x:.1f}%"),
        title="Risco de obesidade por idade",
        color="% Obesidade",
        color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"]
    )
    fig.update_traces(textposition="outside")
    fig = apply_dark_layout(fig, 390)
    st.plotly_chart(fig, use_container_width=True)

with b:
    family_risk = (
        filtered.groupby("family_history", observed=True)["Obesity_Group"]
        .apply(lambda x: (x == "Obesidade").mean() * 100)
        .reset_index(name="% Obesidade")
    )

    fig = px.bar(
        family_risk,
        x="family_history",
        y="% Obesidade",
        text=family_risk["% Obesidade"].map(lambda x: f"{x:.1f}%"),
        title="Risco por histórico familiar",
        color="% Obesidade",
        color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"]
    )
    fig.update_traces(textposition="outside")
    fig = apply_dark_layout(fig, 390)
    st.plotly_chart(fig, use_container_width=True)

with c:
    gender_risk = (
        filtered.groupby("Gender", observed=True)["Obesity_Group"]
        .apply(lambda x: (x == "Obesidade").mean() * 100)
        .reset_index(name="% Obesidade")
    )

    fig = px.bar(
        gender_risk,
        x="Gender",
        y="% Obesidade",
        text=gender_risk["% Obesidade"].map(lambda x: f"{x:.1f}%"),
        title="Risco por gênero",
        color="% Obesidade",
        color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"]
    )
    fig.update_traces(textposition="outside")
    fig = apply_dark_layout(fig, 390)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# Hábitos
# =========================
h1, h2 = st.columns(2)

with h1:
    activity_order = [
        "0 - Não pratica",
        "1 - Baixa",
        "2 - Moderada",
        "3 - Alta"
    ]

    activity = (
        filtered.groupby("FAF_Category", observed=True)["Obesity_Group"]
        .apply(lambda x: (x == "Obesidade").mean() * 100)
        .reindex(activity_order)
        .dropna()
        .reset_index(name="% Obesidade")
    )

    fig = px.bar(
        activity,
        x="FAF_Category",
        y="% Obesidade",
        text=activity["% Obesidade"].map(lambda x: f"{x:.1f}%"),
        title="Obesidade x frequência de atividade física",
        labels={
            "FAF_Category": "Frequência de atividade física",
            "% Obesidade": "% de pacientes com obesidade"
        },
        color="% Obesidade",
        color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"]
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(
        tickangle=0,
        tickfont=dict(size=12),
        title_standoff=24
    )
    fig.update_yaxes(
        range=[0, max(100, activity["% Obesidade"].max() * 1.25)],
        title_standoff=22,
        ticksuffix="%"
    )
    fig.update_layout(
        margin=dict(l=45, r=45, t=75, b=95),
        bargap=0.42,
        uniformtext_minsize=10,
        uniformtext_mode="show"
    )
    fig = apply_dark_layout(fig, 460)
    fig.update_layout(margin=dict(l=45, r=45, t=75, b=95), bargap=0.42)
    st.plotly_chart(fig, use_container_width=True)

with h2:
    water_order = [
        "1 - Baixo (<1L/dia)",
        "2 - Médio (1-2L/dia)",
        "3 - Alto (>2L/dia)"
    ]

    water = (
        filtered.groupby("CH2O_Category", observed=True)["Obesity_Group"]
        .apply(lambda x: (x == "Obesidade").mean() * 100)
        .reindex(water_order)
        .dropna()
        .reset_index(name="% Obesidade")
    )

    fig = px.bar(
        water,
        x="CH2O_Category",
        y="% Obesidade",
        text=water["% Obesidade"].map(lambda x: f"{x:.1f}%"),
        title="Obesidade x consumo diário de água",
        labels={
            "CH2O_Category": "Consumo diário de água",
            "% Obesidade": "% de pacientes com obesidade"
        },
        color="% Obesidade",
        color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"]
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(
        tickangle=0,
        tickfont=dict(size=12),
        title_standoff=24
    )
    fig.update_yaxes(
        range=[0, max(100, water["% Obesidade"].max() * 1.25)],
        title_standoff=22,
        ticksuffix="%"
    )
    fig.update_layout(
        margin=dict(l=45, r=45, t=75, b=105),
        bargap=0.48,
        uniformtext_minsize=10,
        uniformtext_mode="show"
    )
    fig = apply_dark_layout(fig, 460)
    fig.update_layout(margin=dict(l=45, r=45, t=75, b=105), bargap=0.48)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# Insights executivos
# =========================
st.markdown("## 📌 Insights executivos para a equipe médica")

family_yes = filtered[filtered["family_history"] == "yes"]["Obesity_Group"].eq("Obesidade").mean() * 100
family_no = filtered[filtered["family_history"] == "no"]["Obesity_Group"].eq("Obesidade").mean() * 100
avg_activity_obese = filtered[filtered["Obesity_Group"] == "Obesidade"]["FAF"].mean()
avg_activity_normal = filtered[filtered["Obesity_Group"] == "Peso normal"]["FAF"].mean()
avg_bmi_obese = filtered[filtered["Obesity_Group"] == "Obesidade"]["BMI"].mean()
avg_bmi_normal = filtered[filtered["Obesity_Group"] == "Peso normal"]["BMI"].mean()

i1, i2 = st.columns(2)

with i1:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Fator de risco familiar</div>
            <div class="insight-text">
                Pacientes com histórico familiar positivo apresentam <span class="risk-high">{family_yes:.1f}%</span> de obesidade,
                contra <span class="risk-medium">{family_no:.1f}%</span> entre pacientes sem histórico.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Composição corporal</div>
            <div class="insight-text">
                O IMC médio dos pacientes com obesidade é <span class="risk-high">{avg_bmi_obese:.1f}</span>,
                enquanto no grupo de peso normal é <span class="risk-low">{avg_bmi_normal:.1f}</span>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with i2:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Atividade física</div>
            <div class="insight-text">
                A frequência média de atividade física no grupo com obesidade é <span class="risk-medium">{avg_activity_obese:.2f}</span>,
                comparada a <span class="risk-low">{avg_activity_normal:.2f}</span> no grupo de peso normal.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Recomendação executiva</div>
            <div class="insight-text">
                Priorizar triagem preventiva em pacientes com histórico familiar, alto IMC, baixa atividade física e sinais de sobrepeso.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# Ranking executivo
# =========================
st.markdown("## 🧭 Ranking de fatores para acompanhamento")

ranking = pd.DataFrame({
    "Fator": [
        "IMC elevado",
        "Histórico familiar",
        "Baixa atividade física",
        "Peso elevado",
        "Hábitos alimentares",
        "Consumo de água",
        "Faixa etária"
    ],
    "Prioridade médica": [
        "Muito alta",
        "Muito alta",
        "Alta",
        "Alta",
        "Média",
        "Média",
        "Média"
    ],
    "Uso no acompanhamento": [
        "Triagem e monitoramento clínico",
        "Identificação de risco preventivo",
        "Plano de intervenção comportamental",
        "Acompanhamento de evolução",
        "Educação alimentar",
        "Orientação preventiva",
        "Segmentação de campanhas"
    ]
})

st.dataframe(ranking, use_container_width=True, hide_index=True)

# =========================
# Exportação
# =========================
csv_export = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Baixar dados filtrados",
    data=csv_export,
    file_name="dados_filtrados_obesidade.csv",
    mime="text/csv"
)