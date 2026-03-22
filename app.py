import streamlit as st
import anthropic
import random
from datetime import date, timedelta

# ── Config da página ─────────────────────────────────────────
st.set_page_config(
    page_title="AgroData Palmital",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background-color: #f7f5f0; }
.block-container { padding: 2rem 2.5rem 2rem 2.5rem; max-width: 1100px; }

.brand-header {
    background: #1a3a2a;
    color: #e8f0e0;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.brand-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: #c8e6c0;
    margin: 0;
    line-height: 1.1;
}
.brand-sub {
    font-size: 0.82rem;
    color: #8ab89a;
    margin: 0;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.metric-card {
    background: white;
    border: 1px solid #e0ddd5;
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.7rem;
}
.metric-label {
    font-size: 0.72rem;
    color: #8a8880;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-size: 1.55rem;
    font-weight: 600;
    color: #1a3a2a;
    line-height: 1.1;
}
.metric-delta-up   { font-size: 0.78rem; color: #2d7a4f; font-weight: 500; }
.metric-delta-down { font-size: 0.78rem; color: #b84040; font-weight: 500; }
.metric-unit { font-size: 0.75rem; color: #aaa; margin-left: 3px; }

.chat-msg-user {
    background: #1a3a2a;
    color: #e8f0e0;
    padding: 0.75rem 1rem;
    border-radius: 14px 14px 4px 14px;
    margin: 0.5rem 0 0.5rem 3rem;
    font-size: 0.9rem;
    line-height: 1.5;
}
.chat-msg-ai {
    background: white;
    border: 1px solid #e0ddd5;
    color: #2a2a25;
    padding: 0.75rem 1rem;
    border-radius: 14px 14px 14px 4px;
    margin: 0.5rem 3rem 0.5rem 0;
    font-size: 0.9rem;
    line-height: 1.6;
}
.chat-label-user { text-align: right; font-size: 0.7rem; color: #8a8880; margin-bottom: 2px; }
.chat-label-ai   { font-size: 0.7rem; color: #8a8880; margin-bottom: 2px; }

.alert-card {
    background: #fffbf0;
    border-left: 4px solid #d4a017;
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    color: #3a3020;
    line-height: 1.5;
}
.alert-card.green {
    background: #f0f7f2;
    border-left-color: #2d7a4f;
    color: #1a3a2a;
}
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.15rem;
    color: #1a3a2a;
    margin: 1.2rem 0 0.7rem 0;
}
.farm-badge {
    display: inline-block;
    background: #e8f0e0;
    color: #1a3a2a;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 2px;
}
.sidebar-section {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    border: 1px solid #e8e5de;
}
div[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border-color: #c8c5be !important;
}
</style>
""", unsafe_allow_html=True)

# ── Dados simulados (MVP sem banco) ─────────────────────────
@st.cache_data(ttl=3600)
def get_market_data():
    """Simula dados de mercado — substituir por API real no futuro."""
    today = date.today()
    random.seed(today.toordinal())

    def price_series(base, vol=0.015):
        series = []
        p = base
        for i in range(14):
            p = round(p * (1 + random.uniform(-vol, vol * 1.2)), 2)
            series.append(p)
        return series

    soja  = price_series(152.0)
    milho = price_series(78.5)
    cana  = price_series(111.0)

    return {
        "soja":  {"atual": soja[-1],  "ontem": soja[-2],  "serie": soja,  "unidade": "sc 60kg"},
        "milho": {"atual": milho[-1], "ontem": milho[-2], "serie": milho, "unidade": "sc 60kg"},
        "cana":  {"atual": cana[-1],  "ontem": cana[-2],  "serie": cana,  "unidade": "tonelada"},
    }

@st.cache_data(ttl=3600)
def get_weather():
    today = date.today()
    random.seed(today.toordinal() + 99)
    month = today.month
    is_summer = month in (11, 12, 1, 2, 3)
    return {
        "temp_max": round(random.uniform(28, 36) if is_summer else random.uniform(22, 30), 1),
        "temp_min": round(random.uniform(18, 23) if is_summer else random.uniform(11, 17), 1),
        "rain_mm":  round(random.uniform(0, 20)  if is_summer else random.uniform(0, 4), 1),
        "humidity": round(random.uniform(60, 85)  if is_summer else random.uniform(45, 70), 0),
        "previsao": "Chuva à tarde" if is_summer and random.random() > 0.5 else "Sol com poucas nuvens",
    }

FAZENDAS = [
    {"nome": "Fazenda São João",  "produtor": "João Silva",   "ha": 120, "culturas": ["Soja", "Milho"]},
    {"nome": "Sítio Boa Vista",   "produtor": "Maria Santos", "ha": 45,  "culturas": ["Cana", "Milho"]},
    {"nome": "Fazenda Três Irmãs","produtor": "Carlos Mendes","ha": 210, "culturas": ["Soja", "Cana"]},
]

# ── Estado da sessão ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "farm_idx" not in st.session_state:
    st.session_state.farm_idx = 0

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### AgroData Palmital")
    st.markdown("---")

    api_key = st.text_input(
        "Chave API Claude",
        type="password",
        help="Obtenha em console.anthropic.com",
        placeholder="sk-ant-...",
    )

    st.markdown("**Fazenda selecionada**")
    farm_names = [f["nome"] for f in FAZENDAS]
    selected = st.selectbox("", farm_names, label_visibility="collapsed")
    farm = FAZENDAS[farm_names.index(selected)]

    st.markdown(f"""
    <div class="sidebar-section">
        <div style="font-size:0.8rem;color:#8a8880;margin-bottom:6px">PRODUTOR</div>
        <div style="font-weight:500;color:#1a3a2a">{farm['produtor']}</div>
        <div style="font-size:0.82rem;color:#666;margin-top:4px">{farm['ha']} hectares</div>
        <div style="margin-top:8px">
            {''.join(f'<span class="farm-badge">{c}</span>' for c in farm['culturas'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Perguntas rápidas**")
    quick_questions = [
        "Vale vender soja essa semana?",
        "Previsão de chuva afeta o plantio?",
        "Como está o preço do milho?",
        "Qual a margem atual por hectare?",
        "Devo esperar mais para vender?",
    ]
    for q in quick_questions:
        if st.button(q, use_container_width=True, key=f"q_{q[:10]}"):
            st.session_state._quick_q = q

    if st.button("🗑 Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Cabeçalho ────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <div>
        <p class="brand-title">AgroData Palmital</p>
        <p class="brand-sub">Inteligência de dados para o produtor rural · MVP</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Layout principal ─────────────────────────────────────────
col_dados, col_chat = st.columns([1, 1.4], gap="large")

# ── Coluna esquerda: dados ───────────────────────────────────
with col_dados:
    market = get_market_data()
    weather = get_weather()

    st.markdown('<div class="section-title">Mercado hoje</div>', unsafe_allow_html=True)

    for commodity, info in market.items():
        delta = info["atual"] - info["ontem"]
        delta_pct = (delta / info["ontem"]) * 100
        arrow = "▲" if delta >= 0 else "▼"
        delta_cls = "metric-delta-up" if delta >= 0 else "metric-delta-down"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{commodity.upper()} · CEPEA/ESALQ</div>
            <div class="metric-value">R$ {info['atual']:.2f}<span class="metric-unit">/{info['unidade']}</span></div>
            <div class="{delta_cls}">{arrow} R$ {abs(delta):.2f} ({delta_pct:+.1f}% hoje)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Clima · Palmital/SP</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">TEMPERATURA</div>
            <div class="metric-value">{weather['temp_max']}°<span class="metric-unit">max</span></div>
            <div style="font-size:0.78rem;color:#8a8880">{weather['temp_min']}° mínima</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CHUVA</div>
            <div class="metric-value">{weather['rain_mm']}<span class="metric-unit">mm</span></div>
            <div style="font-size:0.78rem;color:#8a8880">{weather['humidity']:.0f}% umidade</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="alert-card {'green' if weather['rain_mm'] < 5 else ''}">
        <strong>Previsão:</strong> {weather['previsao']}
        {'· Boas condições para operações de campo.' if weather['rain_mm'] < 5 else '· Atenção ao preparo do solo.'}
    </div>
    """, unsafe_allow_html=True)

    # Alerta de oportunidade
    soja_delta = market["soja"]["atual"] - market["soja"]["ontem"]
    if soja_delta > 0:
        st.markdown(f"""
        <div class="alert-card green">
            <strong>Oportunidade:</strong> Soja em alta +{soja_delta:.2f}/sc hoje.
            Preço atual ({market['soja']['atual']:.2f}) está acima da média recente.
        </div>
        """, unsafe_allow_html=True)

# ── Coluna direita: chat IA ──────────────────────────────────
with col_chat:
    st.markdown('<div class="section-title">Assistente IA · Pergunte sobre seus dados</div>', unsafe_allow_html=True)

    if not api_key:
        st.info("Cole sua chave da API Claude na barra lateral para ativar o assistente.", icon="🔑")
    else:
        # Renderiza histórico
        chat_container = st.container(height=420)
        with chat_container:
            if not st.session_state.messages:
                st.markdown(f"""
                <div class="chat-msg-ai">
                    Olá, {farm['produtor'].split()[0]}! 👋 Sou o assistente da AgroData Palmital.<br><br>
                    Posso analisar os preços de hoje, clima e te ajudar a decidir sobre vendas e plantio.<br><br>
                    <em>O que você quer saber?</em>
                </div>
                """, unsafe_allow_html=True)

            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-label-user">Você</div><div class="chat-msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-label-ai">AgroData IA</div><div class="chat-msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)

        # Input do chat
        user_input = st.chat_input("Digite sua pergunta sobre mercado, clima ou produção...")

        # Pergunta rápida via botão da sidebar
        if hasattr(st.session_state, "_quick_q"):
            user_input = st.session_state._quick_q
            del st.session_state._quick_q

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Monta contexto com dados reais
            m = market
            w = weather
            context = f"""
Dados atuais da plataforma AgroData Palmital:
Data: {date.today().strftime('%d/%m/%Y')}

Fazenda: {farm['nome']}
Produtor: {farm['produtor']}
Área: {farm['ha']} hectares
Culturas: {', '.join(farm['culturas'])}

Preços de mercado hoje (CEPEA/ESALQ):
- Soja: R$ {m['soja']['atual']:.2f}/sc 60kg (ontem: R$ {m['soja']['ontem']:.2f}, variação: {((m['soja']['atual']-m['soja']['ontem'])/m['soja']['ontem']*100):+.1f}%)
- Milho: R$ {m['milho']['atual']:.2f}/sc 60kg (ontem: R$ {m['milho']['ontem']:.2f}, variação: {((m['milho']['atual']-m['milho']['ontem'])/m['milho']['ontem']*100):+.1f}%)
- Cana: R$ {m['cana']['atual']:.2f}/tonelada (ontem: R$ {m['cana']['ontem']:.2f})

Clima Palmital/SP hoje:
- Temperatura: {w['temp_max']}°C máx / {w['temp_min']}°C mín
- Chuva: {w['rain_mm']}mm
- Umidade: {w['humidity']:.0f}%
- Previsão: {w['previsao']}
"""
            system_prompt = f"""Você é o assistente agrícola da AgroData Palmital.
Responda de forma direta, prática e amigável — como um consultor de confiança para um produtor rural do interior de SP.
Use os dados fornecidos para dar respostas concretas com números.
Seja conciso (máximo 4 linhas por resposta). Português brasileiro.
Não invente dados além do contexto.

{context}"""

            try:
                client = anthropic.Anthropic(api_key=api_key)
                history = [
                    {"role": h["role"], "content": h["content"]}
                    for h in st.session_state.messages[:-1]
                ][-10:]
                history.append({"role": "user", "content": user_input})

                with st.spinner("Analisando..."):
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=512,
                        system=system_prompt,
                        messages=history,
                    )
                reply = response.content[0].text
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

            except Exception as e:
                err = str(e)
                if "api_key" in err.lower() or "authentication" in err.lower():
                    st.error("Chave API inválida. Verifique em console.anthropic.com")
                else:
                    st.error(f"Erro: {err}")
