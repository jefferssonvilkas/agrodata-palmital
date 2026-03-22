import streamlit as st
import anthropic
import random
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

# ── Página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="AgroData Palmital",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS Global ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,400;0,600;1,300&family=DM+Sans:wght@300;400;500&display=swap');

/* Reset geral */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1c1a16;
}
.main { background: #f5f2eb; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Esconde elementos padrão do streamlit */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stSidebar"] { display: none; }

/* ── LOGIN ── */
.login-wrap {
    min-height: 100vh;
    background: #1a2e1f;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}
.login-box {
    background: #f5f2eb;
    border-radius: 24px;
    padding: 3rem 2.5rem;
    width: 100%;
    max-width: 420px;
    text-align: center;
}
.login-logo {
    font-family: 'Fraunces', serif;
    font-size: 2.2rem;
    font-weight: 300;
    color: #1a2e1f;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}
.login-sub {
    font-size: 0.78rem;
    color: #8a8575;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
}
.login-field label {
    font-size: 0.78rem !important;
    color: #8a8575 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── TOPO / NAV ── */
.topbar {
    background: #1a2e1f;
    padding: 0 2.5rem;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}
.topbar-brand {
    font-family: 'Fraunces', serif;
    font-size: 1.35rem;
    font-weight: 300;
    color: #c8ddc0;
    letter-spacing: 0.02em;
}
.topbar-farm {
    font-size: 0.78rem;
    color: #7a9e7e;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.topbar-right {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.topbar-user {
    font-size: 0.82rem;
    color: #a8c4aa;
}
.topbar-date {
    font-size: 0.78rem;
    color: #5a7a5e;
}

/* ── HERO STRIP ── */
.hero-strip {
    background: #2d4a32;
    padding: 2rem 2.5rem;
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}
.hero-kpi {
    flex: 1;
    min-width: 160px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
}
.hero-kpi-label {
    font-size: 0.7rem;
    color: #7a9e7e;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}
.hero-kpi-val {
    font-family: 'Fraunces', serif;
    font-size: 2rem;
    font-weight: 300;
    color: #e8f0e0;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.hero-kpi-unit {
    font-size: 0.72rem;
    color: #7a9e7e;
}
.hero-kpi-delta-up   { font-size: 0.78rem; color: #7dd88a; font-weight: 500; }
.hero-kpi-delta-down { font-size: 0.78rem; color: #e87a7a; font-weight: 500; }

/* ── PÁGINA CONTENT ── */
.page-content {
    padding: 2rem 2.5rem;
    background: #f5f2eb;
    min-height: calc(100vh - 64px - 120px);
}

/* ── CARDS ── */
.card {
    background: white;
    border: 1px solid #e8e4db;
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    height: 100%;
}
.card-title {
    font-family: 'Fraunces', serif;
    font-size: 1.05rem;
    font-weight: 400;
    color: #1a2e1f;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #f0ece3;
}

/* ── TALHOES ── */
.talhao-row {
    display: flex;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid #f5f2eb;
    gap: 1rem;
}
.talhao-color {
    width: 10px;
    height: 36px;
    border-radius: 4px;
    flex-shrink: 0;
}
.talhao-info { flex: 1; }
.talhao-name { font-size: 0.88rem; font-weight: 500; color: #1c1a16; }
.talhao-sub  { font-size: 0.75rem; color: #8a8575; margin-top: 1px; }
.talhao-val  { text-align: right; }
.talhao-num  { font-size: 1rem; font-weight: 500; color: #1a2e1f; }
.talhao-unit { font-size: 0.72rem; color: #8a8575; }
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 500;
}
.badge-green  { background: #e8f5e0; color: #2d6a2e; }
.badge-yellow { background: #fdf5e0; color: #8a6a10; }
.badge-blue   { background: #e0edf5; color: #1a4a6e; }
.badge-gray   { background: #f0ede8; color: #6a6560; }

/* ── ALERTAS ── */
.alert-item {
    display: flex;
    gap: 0.8rem;
    padding: 0.8rem 0;
    border-bottom: 1px solid #f5f2eb;
    align-items: flex-start;
}
.alert-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}
.alert-text  { font-size: 0.85rem; color: #3a3830; line-height: 1.5; flex: 1; }
.alert-time  { font-size: 0.72rem; color: #aaa89f; white-space: nowrap; }

/* ── CHAT ── */
.chat-history {
    height: 360px;
    overflow-y: auto;
    padding: 0.5rem 0;
    margin-bottom: 0.8rem;
}
.chat-bubble-user {
    background: #1a2e1f;
    color: #e8f0e0;
    padding: 0.65rem 1rem;
    border-radius: 16px 16px 4px 16px;
    margin: 0.4rem 0 0.4rem 2.5rem;
    font-size: 0.87rem;
    line-height: 1.5;
}
.chat-bubble-ai {
    background: #f5f2eb;
    border: 1px solid #e8e4db;
    color: #1c1a16;
    padding: 0.65rem 1rem;
    border-radius: 16px 16px 16px 4px;
    margin: 0.4rem 2.5rem 0.4rem 0;
    font-size: 0.87rem;
    line-height: 1.6;
}
.chat-name-user { text-align:right; font-size:0.68rem; color:#aaa89f; margin-bottom:2px; }
.chat-name-ai   { font-size:0.68rem; color:#aaa89f; margin-bottom:2px; }
.chip {
    display: inline-block;
    background: #f0ece3;
    border: 1px solid #e0dbd0;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.78rem;
    color: #3a3830;
    margin: 3px;
    cursor: pointer;
}

/* Ajustes streamlit nativos */
div[data-testid="stChatInput"] > div {
    border-radius: 14px !important;
    background: white !important;
    border: 1px solid #e0dbd0 !important;
}
.stButton button {
    border-radius: 10px !important;
    border: 1px solid #d8d4cb !important;
    background: white !important;
    color: #3a3830 !important;
    font-size: 0.82rem !important;
    padding: 0.3rem 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Dados mockados ────────────────────────────────────────────
def gerar_precos(seed_offset=0):
    hoje = date.today()
    random.seed(hoje.toordinal() + seed_offset)
    def serie(base, dias=30, vol=0.012):
        p, s = base, []
        for _ in range(dias):
            p = round(p * (1 + random.uniform(-vol, vol * 1.3)), 2)
            s.append(p)
        return s
    soja  = serie(152.0)
    milho = serie(78.5)
    cana  = serie(111.0)
    return {
        "soja":  {"atual": soja[-1],  "ontem": soja[-2],  "serie": soja,  "un": "sc 60kg"},
        "milho": {"atual": milho[-1], "ontem": milho[-2], "serie": milho, "un": "sc 60kg"},
        "cana":  {"atual": cana[-1],  "ontem": cana[-2],  "serie": cana,  "un": "ton"},
    }

def gerar_talhoes(crops):
    cores = {"Soja": "#4a8c3f", "Milho": "#c8a020", "Cana": "#4a7a9b", "Mandioca": "#9b6a3e"}
    status_opts = ["Crescimento", "Plantio", "Colheita", "Preparo"]
    talhoes = []
    random.seed(date.today().toordinal() + 7)
    for i, crop in enumerate(crops * 3):
        talhoes.append({
            "nome": f"Talhão {i+1} — {crop}",
            "cultura": crop,
            "cor": cores.get(crop, "#888"),
            "ha": round(random.uniform(12, 45), 1),
            "prod_est": round(random.uniform(48, 72) if crop == "Soja"
                              else random.uniform(90, 130) if crop == "Milho"
                              else random.uniform(75, 95), 1),
            "status": random.choice(status_opts),
            "dias": random.randint(18, 95),
        })
    return talhoes[:6]

def gerar_producao_mensal(crops):
    meses = ["Set", "Out", "Nov", "Dez", "Jan", "Fev", "Mar"]
    random.seed(42)
    result = {}
    for crop in crops:
        base = 150 if crop == "Soja" else 80 if crop == "Milho" else 110
        result[crop] = [round(base * random.uniform(0.85, 1.2)) for _ in meses]
    return meses, result

def gerar_clima():
    random.seed(date.today().toordinal() + 3)
    m = date.today().month
    verao = m in (11, 12, 1, 2, 3)
    return {
        "max": round(random.uniform(29, 36) if verao else random.uniform(23, 30), 1),
        "min": round(random.uniform(19, 24) if verao else random.uniform(12, 18), 1),
        "chuva": round(random.uniform(0, 18) if verao else random.uniform(0, 4), 1),
        "umidade": round(random.uniform(62, 85) if verao else random.uniform(45, 65)),
        "prev": "Chuva à tarde" if verao and random.random() > 0.45 else "Sol com poucas nuvens",
    }

ALERTAS = [
    {"cor": "#4a8c3f", "texto": "Soja em alta por 3 dias consecutivos — janela favorável para venda.", "hora": "08:14"},
    {"cor": "#c8a020", "texto": "Umidade do solo no Talhão 3 abaixo do ideal — considerar irrigação.", "hora": "07:30"},
    {"cor": "#4a7a9b", "texto": "Previsão de chuva forte para quinta-feira — adiar aplicação de defensivo.", "hora": "Ontem"},
    {"cor": "#c84040", "texto": "Preço do milho recuou 1,8% esta semana. Acompanhar mercado.", "hora": "Ontem"},
]

# ── Autenticação ─────────────────────────────────────────────
def check_login(username, password):
    try:
        users = st.secrets.get("users", {})
        user_data = users.get(username)
        if user_data and user_data.get("password") == password:
            return dict(user_data)
    except Exception:
        pass
    # Fallback demo (para quando não há secrets configurados)
    DEMO = {
        "joao":   {"password": "senha123", "farm": "Fazenda São João",   "owner": "João Silva",   "hectares": 120, "crops": ["Soja", "Milho"], "city": "Palmital"},
        "maria":  {"password": "senha456", "farm": "Sítio Boa Vista",    "owner": "Maria Santos", "hectares": 45,  "crops": ["Cana", "Milho"], "city": "Palmital"},
        "carlos": {"password": "senha789", "farm": "Fazenda Três Irmãs", "owner": "Carlos Mendes","hectares": 210, "crops": ["Soja", "Cana"],  "city": "Palmital"},
    }
    u = DEMO.get(username.lower())
    if u and u["password"] == password:
        return u
    return None

def get_api_key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        return ""

# ── Estado ───────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "dashboard"

# ════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div style="min-height:100vh;background:#1a2e1f;display:flex;
        align-items:center;justify-content:center;padding:2rem;">
      <div style="background:#f5f2eb;border-radius:28px;padding:3rem 2.5rem;
          width:100%;max-width:400px;text-align:center;">
        <div style="font-family:'Fraunces',serif;font-size:2.4rem;
            font-weight:300;color:#1a2e1f;line-height:1.1;margin-bottom:0.3rem;">
          AgroData
        </div>
        <div style="font-size:0.75rem;color:#8a8575;letter-spacing:0.14em;
            text-transform:uppercase;margin-bottom:0.5rem;">
          Palmital · SP
        </div>
        <div style="width:40px;height:2px;background:#4a8c3f;
            margin:0 auto 2.2rem;border-radius:2px;"></div>
        <div style="font-size:0.82rem;color:#6a6560;margin-bottom:2rem;">
          Inteligência de dados para o produtor rural
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Centraliza o formulário
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top:-420px;'>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<div style='height:200px'></div>", unsafe_allow_html=True)
            username = st.text_input("Usuário", placeholder="joao", key="login_user")
            password = st.text_input("Senha", type="password", placeholder="••••••••", key="login_pass")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Entrar", use_container_width=True)

            if submitted:
                user_data = check_login(username, password)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.session_state.username = username
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

        st.markdown("""
        <div style='text-align:center;font-size:0.75rem;color:#aaa89f;margin-top:1rem;'>
            Demo: joao / senha123 &nbsp;·&nbsp; maria / senha456
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ════════════════════════════════════════════════════════════
# DASHBOARD (pós-login)
# ════════════════════════════════════════════════════════════
user    = st.session_state.user
crops   = user["crops"]
farm    = user["farm"]
owner   = user["owner"]
hectares= user["hectares"]

precos  = gerar_precos()
talhoes = gerar_talhoes(crops)
clima   = gerar_clima()
meses, prod_mensal = gerar_producao_mensal(crops)
api_key = get_api_key()

hoje_str = date.today().strftime("%d de %B de %Y").replace(
    "January","janeiro").replace("February","fevereiro").replace("March","março"
    ).replace("April","abril").replace("May","maio").replace("June","junho"
    ).replace("July","julho").replace("August","agosto").replace("September","setembro"
    ).replace("October","outubro").replace("November","novembro").replace("December","dezembro")

# ── Topbar ───────────────────────────────────────────────────
c_logout = st.columns([6,1])
with c_logout[1]:
    if st.button("Sair", key="logout_btn"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f"""
<div class="topbar">
  <div>
    <div class="topbar-brand">AgroData Palmital</div>
    <div class="topbar-farm">{farm}</div>
  </div>
  <div class="topbar-right">
    <div style="text-align:right">
      <div class="topbar-user">{owner}</div>
      <div class="topbar-date">{hoje_str}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Hero ─────────────────────────────────────────────────
def delta_html(atual, ontem, cls_base="hero-kpi-delta"):
    d = atual - ontem
    pct = d / ontem * 100
    arrow = "▲" if d >= 0 else "▼"
    cls = f"{cls_base}-up" if d >= 0 else f"{cls_base}-down"
    return f'<span class="{cls}">{arrow} {abs(d):.2f} ({pct:+.1f}%)</span>'

soja_d  = delta_html(precos["soja"]["atual"],  precos["soja"]["ontem"])
milho_d = delta_html(precos["milho"]["atual"], precos["milho"]["ontem"])
cana_d  = delta_html(precos["cana"]["atual"],  precos["cana"]["ontem"])

st.markdown(f"""
<div class="hero-strip">
  <div class="hero-kpi">
    <div class="hero-kpi-label">Soja · CEPEA</div>
    <div class="hero-kpi-val">R$ {precos['soja']['atual']:.2f}</div>
    <div class="hero-kpi-unit">{precos['soja']['un']}</div>
    {soja_d}
  </div>
  <div class="hero-kpi">
    <div class="hero-kpi-label">Milho · CEPEA</div>
    <div class="hero-kpi-val">R$ {precos['milho']['atual']:.2f}</div>
    <div class="hero-kpi-unit">{precos['milho']['un']}</div>
    {milho_d}
  </div>
  <div class="hero-kpi">
    <div class="hero-kpi-label">Cana · CEPEA</div>
    <div class="hero-kpi-val">R$ {precos['cana']['atual']:.2f}</div>
    <div class="hero-kpi-unit">{precos['cana']['un']}</div>
    {cana_d}
  </div>
  <div class="hero-kpi">
    <div class="hero-kpi-label">Clima · Palmital</div>
    <div class="hero-kpi-val">{clima['max']}°</div>
    <div class="hero-kpi-unit">máx · {clima['min']}° mín</div>
    <span style="font-size:0.75rem;color:#a8c4aa">{clima['chuva']}mm · {clima['prev']}</span>
  </div>
  <div class="hero-kpi">
    <div class="hero-kpi-label">Área total</div>
    <div class="hero-kpi-val">{hectares}</div>
    <div class="hero-kpi-unit">hectares</div>
    <span style="font-size:0.75rem;color:#a8c4aa">{', '.join(crops)}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Conteúdo ─────────────────────────────────────────────────
st.markdown('<div class="page-content">', unsafe_allow_html=True)

col_esq, col_dir = st.columns([1.1, 1], gap="large")

# ════ COLUNA ESQUERDA ════
with col_esq:

    # Gráfico de preços
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Evolução de preços — 30 dias</div>', unsafe_allow_html=True)

    dias = [(date.today() - timedelta(days=29-i)).strftime("%d/%m") for i in range(30)]
    fig = go.Figure()
    cores_linha = {"soja": "#4a8c3f", "milho": "#c8a020", "cana": "#4a7a9b"}
    for nome, info in precos.items():
        if any(c.lower() == nome or
               (nome == "cana" and "Cana" in crops) or
               (nome == "soja" and "Soja" in crops) or
               (nome == "milho" and "Milho" in crops)
               for c in crops):
            fig.add_trace(go.Scatter(
                x=dias, y=info["serie"],
                name=nome.capitalize(),
                line=dict(color=cores_linha[nome], width=2.5),
                mode="lines",
            ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=220,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11, color="#6a6560")),
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#aaa89f"),
                   tickmode="array",
                   tickvals=dias[::5], ticktext=dias[::5]),
        yaxis=dict(showgrid=True, gridcolor="#f0ece3",
                   tickfont=dict(size=10, color="#aaa89f"),
                   tickprefix="R$ "),
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Talhões
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Talhões · situação atual</div>', unsafe_allow_html=True)

    status_badge = {
        "Crescimento": "badge-green",
        "Plantio":     "badge-blue",
        "Colheita":    "badge-yellow",
        "Preparo":     "badge-gray",
    }
    for t in talhoes:
        badge_cls = status_badge.get(t["status"], "badge-gray")
        st.markdown(f"""
        <div class="talhao-row">
          <div class="talhao-color" style="background:{t['cor']}"></div>
          <div class="talhao-info">
            <div class="talhao-name">{t['nome']}</div>
            <div class="talhao-sub">{t['ha']} ha · {t['dias']} dias de ciclo</div>
          </div>
          <div style="text-align:right">
            <div><span class="badge {badge_cls}">{t['status']}</span></div>
            <div style="font-size:0.78rem;color:#8a8575;margin-top:4px">
                Est. {t['prod_est']} sc/ha
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Gráfico produção estimada
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Produção estimada por mês (sacas)</div>', unsafe_allow_html=True)

    fig2 = go.Figure()
    cores_bar = {"Soja": "#4a8c3f", "Milho": "#c8a020", "Cana": "#4a7a9b", "Mandioca": "#9b6a3e"}
    for crop, vals in prod_mensal.items():
        fig2.add_trace(go.Bar(
            name=crop, x=meses, y=vals,
            marker_color=cores_bar.get(crop, "#888"),
            marker_line_width=0,
        ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="group",
        margin=dict(l=0, r=0, t=10, b=0),
        height=200,
        bargap=0.25,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11, color="#6a6560")),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#aaa89f")),
        yaxis=dict(showgrid=True, gridcolor="#f0ece3", tickfont=dict(size=10, color="#aaa89f")),
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ════ COLUNA DIREITA ════
with col_dir:

    # Alertas
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Alertas e oportunidades</div>', unsafe_allow_html=True)
    for a in ALERTAS:
        st.markdown(f"""
        <div class="alert-item">
          <div class="alert-dot" style="background:{a['cor']}"></div>
          <div class="alert-text">{a['texto']}</div>
          <div class="alert-time">{a['hora']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat IA
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Assistente IA · AgroData</div>', unsafe_allow_html=True)

    # Chips de perguntas rápidas
    st.markdown("""
    <div style="margin-bottom:0.8rem;line-height:2.2">
      <span class="chip" onclick="void(0)">Vale vender soja agora?</span>
      <span class="chip">Risco de chuva no plantio?</span>
      <span class="chip">Margem por hectare</span>
      <span class="chip">Preço do milho esta semana</span>
    </div>
    """, unsafe_allow_html=True)

    quick_cols = st.columns(2)
    quick_qs = [
        "Vale vender soja agora?",
        "Risco de chuva no plantio?",
        "Qual a margem por hectare?",
        "Como está o preço do milho?",
    ]
    for i, q in enumerate(quick_qs):
        with quick_cols[i % 2]:
            if st.button(q, key=f"chip_{i}", use_container_width=True):
                st.session_state._qinput = q

    # Histórico
    chat_html = ""
    if not st.session_state.messages:
        primeiro_nome = owner.split()[0]
        chat_html = f"""
        <div class="chat-bubble-ai">
          Olá, {primeiro_nome}! Sou o assistente da AgroData.<br>
          Posso analisar preços, clima e situação dos seus talhões.<br>
          <em>O que você quer saber hoje?</em>
        </div>"""
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                chat_html += f'<div class="chat-name-user">Você</div><div class="chat-bubble-user">{msg["content"]}</div>'
            else:
                chat_html += f'<div class="chat-name-ai">AgroData IA</div><div class="chat-bubble-ai">{msg["content"]}</div>'

    st.markdown(f'<div class="chat-history">{chat_html}</div>', unsafe_allow_html=True)

    # Input
    user_input = st.chat_input("Pergunte sobre mercado, clima ou seus talhões...")

    if hasattr(st.session_state, "_qinput"):
        user_input = st.session_state._qinput
        del st.session_state._qinput

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        p = precos
        c = clima
        context = f"""
Dados da plataforma AgroData Palmital — {date.today().strftime('%d/%m/%Y')}

Fazenda: {farm} | Produtor: {owner} | {hectares} ha | Culturas: {', '.join(crops)}

Preços hoje (CEPEA):
- Soja:  R$ {p['soja']['atual']:.2f}/sc 60kg  (var: {((p['soja']['atual']-p['soja']['ontem'])/p['soja']['ontem']*100):+.1f}%)
- Milho: R$ {p['milho']['atual']:.2f}/sc 60kg (var: {((p['milho']['atual']-p['milho']['ontem'])/p['milho']['ontem']*100):+.1f}%)
- Cana:  R$ {p['cana']['atual']:.2f}/ton      (var: {((p['cana']['atual']-p['cana']['ontem'])/p['cana']['ontem']*100):+.1f}%)

Clima Palmital: {c['max']}°C máx / {c['min']}°C mín | {c['chuva']}mm chuva | {c['umidade']}% umidade | {c['prev']}

Talhões:
""" + "\n".join(
    f"- {t['nome']}: {t['ha']} ha, {t['status']}, estimativa {t['prod_est']} sc/ha"
    for t in talhoes
)

        system = f"""Você é o assistente agrícola da AgroData Palmital.
Responda de forma direta, prática e amigável — como um consultor para produtor rural do interior de SP.
Use os dados abaixo para dar respostas concretas com números reais.
Seja conciso (máximo 4 linhas). Português brasileiro coloquial.
Não invente dados além do contexto fornecido.

{context}"""

        if not api_key:
            reply = "⚠️ Chave da API não configurada. Configure ANTHROPIC_API_KEY nos Secrets do Streamlit Cloud."
        else:
            try:
                client = anthropic.Anthropic(api_key=api_key)
                hist = [{"role": h["role"], "content": h["content"]}
                        for h in st.session_state.messages[:-1]][-10:]
                hist.append({"role": "user", "content": user_input})
                with st.spinner(""):
                    resp = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=512,
                        system=system,
                        messages=hist,
                    )
                reply = resp.content[0].text
            except Exception as e:
                reply = f"Erro na API: {str(e)[:120]}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.messages:
        if st.button("Limpar conversa", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
