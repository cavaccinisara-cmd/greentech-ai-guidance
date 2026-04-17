import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="Greentech AI Guidance Layer",
    page_icon="⚡",
    layout="wide"
)

# -----------------------------
# Stile custom
# -----------------------------
st.markdown("""
<style>
    .main {
        background-color: #f7faf8;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    .hero {
        background: linear-gradient(135deg, #e8f5ee 0%, #eef7ff 100%);
        padding: 1.6rem 1.6rem;
        border-radius: 20px;
        border: 1px solid #d9e8dd;
        margin-bottom: 1.4rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.3rem;
    }
    .hero p {
        margin-top: 0.5rem;
        color: #4a5568;
        font-size: 1rem;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.7rem;
    }
    .card {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .small-label {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
    }
    .big-number {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .risk-low {
        color: #15803d;
        font-weight: 700;
    }
    .risk-medium {
        color: #b45309;
        font-weight: 700;
    }
    .risk-high {
        color: #b91c1c;
        font-weight: 700;
    }
    .suggestion-box {
        background: #ffffff;
        border-left: 5px solid #16a34a;
        padding: 0.95rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        border-top: 1px solid #e5e7eb;
        border-right: 1px solid #e5e7eb;
        border-bottom: 1px solid #e5e7eb;
    }
    .compare-box {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
        min-height: 170px;
    }
    .footer-note {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Funzioni
# -----------------------------
def build_profiles(solar_level, consumption_level, battery_level, price_level):
    slots = ["08-10", "10-13", "13-15", "15-18", "18-20"]
    x = np.arange(len(slots))

    solar_base = {
        "Basso": np.array([1, 2, 2, 1, 0]),
        "Medio": np.array([2, 4, 5, 3, 1]),
        "Alto":  np.array([3, 6, 8, 5, 1]),
    }

    consumption_base = {
        "Basso": np.array([2, 2, 2, 2, 1]),
        "Medio": np.array([3, 4, 4, 3, 2]),
        "Alto":  np.array([4, 6, 5, 6, 4]),
    }

    price_base = {
        "Basso": np.array([2, 2, 2, 2, 2]),
        "Medio": np.array([2, 3, 2, 3, 4]),
        "Alto":  np.array([3, 4, 3, 5, 6]),
    }

    battery_base = {
        "Basso": 2,
        "Medio": 5,
        "Alto": 8,
    }

    solar_profile = solar_base[solar_level]
    consumption_profile = consumption_base[consumption_level]
    price_profile = price_base[price_level]
    battery_capacity = battery_base[battery_level]

    return slots, x, solar_profile, consumption_profile, price_profile, battery_capacity


def create_energy_plot(slots, x, solar_profile, consumption_profile, price_profile):
    fig, ax = plt.subplots(figsize=(12, 5.8))
    ax.plot(x, solar_profile, marker="o", linewidth=2.8, markersize=8, label="Produzione solare")
    ax.plot(x, consumption_profile, marker="o", linewidth=2.8, markersize=8, label="Consumo aziendale")
    ax.plot(x, price_profile, marker="o", linestyle="--", linewidth=2.4, markersize=7, label="Indice prezzo energia")

    ax.set_xticks(x)
    ax.set_xticklabels(slots, fontsize=11)
    ax.set_title("Profilo energetico giornaliero", fontsize=15, pad=14)
    ax.set_xlabel("Fasce orarie", fontsize=11)
    ax.set_ylabel("Indice relativo", fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig


def scenario_comparison(score, consumption_level, price_level):
    base_cost_map = {
        ("Basso", "Basso"): 80,
        ("Basso", "Medio"): 95,
        ("Basso", "Alto"): 110,
        ("Medio", "Basso"): 120,
        ("Medio", "Medio"): 145,
        ("Medio", "Alto"): 170,
        ("Alto", "Basso"): 180,
        ("Alto", "Medio"): 220,
        ("Alto", "Alto"): 270,
    }

    baseline_cost = base_cost_map[(consumption_level, price_level)]

    if score >= 75:
        savings_pct = 0.16
    elif score >= 50:
        savings_pct = 0.11
    else:
        savings_pct = 0.06

    optimized_cost = round(baseline_cost * (1 - savings_pct), 1)
    savings_value = round(baseline_cost - optimized_cost, 1)
    savings_pct_display = int(savings_pct * 100)

    return baseline_cost, optimized_cost, savings_value, savings_pct_display


def energy_guidance(solar_level, consumption_level, battery_level, price_level, critical_slot):
    score = 100
    suggestions = []

    if consumption_level == "Alto":
        score -= 20
    elif consumption_level == "Medio":
        score -= 10

    if solar_level == "Basso":
        score -= 20
    elif solar_level == "Medio":
        score -= 10

    if battery_level == "Basso":
        score -= 15
    elif battery_level == "Medio":
        score -= 5

    if price_level == "Alto":
        score -= 20
    elif price_level == "Medio":
        score -= 10

    score = max(0, min(100, score))

    if score >= 75:
        risk = "Basso"
        insight = "Profilo energetico complessivamente efficiente, con margini di ottimizzazione incrementale."
    elif score >= 50:
        risk = "Medio"
        insight = "Profilo energetico discreto, ma con aree di miglioramento nella gestione dei carichi e della batteria."
    else:
        risk = "Alto"
        insight = "Profilo energetico critico: elevata esposizione a inefficienze operative e costi energetici non ottimizzati."

    if solar_level == "Alto" and consumption_level in ["Medio", "Alto"]:
        suggestions.append(
            "Ottimizzare lo scheduling produttivo concentrando i carichi energivori nelle ore di maggiore disponibilità solare."
        )

    if price_level == "Alto" and battery_level in ["Medio", "Alto"]:
        suggestions.append(
            f"Ridurre il prelievo dalla rete nella fascia {critical_slot}, privilegiando l’utilizzo dell’energia accumulata."
        )

    if battery_level == "Basso" and price_level == "Alto":
        suggestions.append(
            "Preservare la capacità residua della batteria per coprire le finestre orarie a maggiore costo energetico."
        )

    if solar_level == "Basso" and consumption_level == "Alto":
        suggestions.append(
            "Valutare il rinvio delle attività non prioritarie per ridurre l’esposizione a energia di rete nelle ore meno favorevoli."
        )

    if consumption_level == "Alto" and price_level == "Alto":
        suggestions.append(
            "Monitorare i carichi critici: l’attuale configurazione potrebbe comprimere la marginalità operativa nelle fasce più costose."
        )

    if solar_level == "Medio" and battery_level == "Basso":
        suggestions.append(
            "Pianificare una strategia di accumulo più conservativa per migliorare la copertura energetica nelle ore successive."
        )

    default_messages = [
        "Mantenere un monitoraggio continuo dei flussi energetici per individuare tempestivamente opportunità di efficientamento.",
        "Valutare una migliore distribuzione interna dei carichi per aumentare l’autoconsumo energetico.",
        "Consolidare una pianificazione energetica giornaliera orientata a costo, disponibilità e continuità operativa."
    ]

    for msg in default_messages:
        if len(suggestions) < 3:
            suggestions.append(msg)

    return score, risk, insight, suggestions[:3]


def generate_executive_profile(score, risk, solar_level, consumption_level, battery_level, price_level):
    if consumption_level == "Alto" and price_level == "Alto":
        profile = "PMI energivora esposta a pressione sui costi operativi."
    elif solar_level == "Alto" and battery_level in ["Medio", "Alto"]:
        profile = "PMI con buon potenziale di autoconsumo e margini di ottimizzazione avanzata."
    elif solar_level == "Basso" and battery_level == "Basso":
        profile = "PMI con limitata flessibilità energetica e maggiore dipendenza dalla rete."
    else:
        profile = "PMI con profilo energetico intermedio e opportunità di efficientamento progressivo."

    if risk == "Basso":
        priority = "Consolidare l’efficienza raggiunta e introdurre logiche di pianificazione energetica più granulari."
    elif risk == "Medio":
        priority = "Ridurre la variabilità dei carichi e migliorare il coordinamento tra consumo, accumulo e costo dell’energia."
    else:
        priority = "Intervenire sui carichi critici e ridurre l’esposizione alle fasce a maggiore costo energetico."

    if score >= 75:
        executive_message = (
            "Lo scenario evidenzia una configurazione già efficiente: il valore aggiunto dell’AI è soprattutto incrementale, "
            "orientato a stabilità operativa e ulteriore ottimizzazione."
        )
    elif score >= 50:
        executive_message = (
            "Lo scenario presenta una base discreta ma non ancora ottimizzata: il layer AI genera valore nel coordinare meglio "
            "consumo, accumulo e timing operativo."
        )
    else:
        executive_message = (
            "Lo scenario mostra una criticità energetica significativa: il layer AI assume una funzione prioritaria di supporto "
            "decisionale per contenere costi e inefficienze."
        )

    return profile, priority, executive_message


# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>⚡ Greentech AI Guidance Layer</h1>
    <p>
        Prototipo di supporto decisionale per PMI: trasforma uno scenario energetico semplificato
        in insight operativi, raccomandazioni e confronto economico.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Configura lo scenario")
    solar_level = st.radio("Produzione solare", ["Basso", "Medio", "Alto"])
    consumption_level = st.radio("Consumo aziendale", ["Basso", "Medio", "Alto"])
    battery_level = st.radio("Stato batteria", ["Basso", "Medio", "Alto"])
    price_level = st.radio("Prezzo energia", ["Basso", "Medio", "Alto"])
    critical_slot = st.selectbox(
        "Fascia critica",
        ["08:00–10:00", "10:00–13:00", "13:00–15:00", "15:00–18:00", "18:00–20:00"]
    )
    run = st.button("Genera analisi AI", use_container_width=True)

if run:
    score, risk, insight, suggestions = energy_guidance(
        solar_level, consumption_level, battery_level, price_level, critical_slot
    )

    slots, x, solar_profile, consumption_profile, price_profile, battery_capacity = build_profiles(
        solar_level, consumption_level, battery_level, price_level
    )

    baseline_cost, optimized_cost, savings_value, savings_pct_display = scenario_comparison(
        score, consumption_level, price_level
    )

    profile, priority, executive_message = generate_executive_profile(
        score, risk, solar_level, consumption_level, battery_level, price_level
    )

    if risk == "Basso":
        risk_class = "risk-low"
    elif risk == "Medio":
        risk_class = "risk-medium"
    else:
        risk_class = "risk-high"

    # KPI
    st.markdown('<div class="section-title">Executive overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="small-label">Energy Behavior Score</div>
            <p class="big-number">{score}/100</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="small-label">Livello di rischio</div>
            <p class="big-number {risk_class}">{risk}</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="small-label">Risparmio stimato</div>
            <p class="big-number">€ {savings_value}</p>
        </div>
        """, unsafe_allow_html=True)

    # Insight + Suggestions
    left, right = st.columns([1, 1.25])

    with left:
        st.markdown('<div class="section-title">Insight AI</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
            {insight}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">Raccomandazioni operative</div>', unsafe_allow_html=True)
        for i, s in enumerate(suggestions, start=1):
            st.markdown(f"""
            <div class="suggestion-box">
                <strong>{i}.</strong> {s}
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title">Profilo energetico giornaliero</div>', unsafe_allow_html=True)
        fig = create_energy_plot(slots, x, solar_profile, consumption_profile, price_profile)
        st.pyplot(fig, use_container_width=True)

    # Comparison
    st.markdown('<div class="section-title">Scenario comparison</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)

    with d1:
        st.markdown(f"""
        <div class="compare-box">
            <div class="small-label">Scenario standard</div>
            <p class="big-number">€ {baseline_cost}</p>
            <p>Gestione reattiva dei carichi</p>
        </div>
        """, unsafe_allow_html=True)

    with d2:
        st.markdown(f"""
        <div class="compare-box">
            <div class="small-label">Scenario con AI Guidance</div>
            <p class="big-number">€ {optimized_cost}</p>
            <p>Risparmio stimato: € {savings_value} ({savings_pct_display}%)</p>
        </div>
        """, unsafe_allow_html=True)

    # Profilo consulenziale
    st.markdown('<div class="section-title">Profilo aziendale sintetico</div>', unsafe_allow_html=True)
    e1, e2 = st.columns(2)

    with e1:
        st.markdown(f"""
        <div class="compare-box">
            <div class="small-label">Profilo del cliente</div>
            <p>{profile}</p>
        </div>
        """, unsafe_allow_html=True)

    with e2:
        st.markdown(f"""
        <div class="compare-box">
            <div class="small-label">Priorità strategica</div>
            <p>{priority}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Executive takeaway</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
        {executive_message}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="footer-note">Nota: il prototipo utilizza scenari semplificati e una logica dimostrativa, finalizzata a rappresentare il valore consulenziale del layer AI.</div>',
        unsafe_allow_html=True
    )

else:
    st.markdown("""
    <div class="card">
        <strong>Come usare la demo</strong><br><br>
        1. Configura i parametri nella sidebar.<br>
        2. Clicca su <em>Genera analisi AI</em>.<br>
        3. Osserva KPI, raccomandazioni operative, grafico e scenario comparison.
    </div>
    """, unsafe_allow_html=True)
