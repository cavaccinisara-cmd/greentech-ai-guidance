import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Greentech AI Guidance Layer", layout="wide")

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
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(x, solar_profile, marker="o", label="Produzione solare stimata")
    ax.plot(x, consumption_profile, marker="o", label="Consumo aziendale")
    ax.plot(x, price_profile, marker="o", linestyle="--", label="Indice prezzo energia")
    ax.set_xticks(x)
    ax.set_xticklabels(slots)
    ax.set_title("Profilo energetico giornaliero")
    ax.set_xlabel("Fasce orarie")
    ax.set_ylabel("Indice relativo")
    ax.legend()
    ax.grid(True, alpha=0.3)
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

    suggestions = suggestions[:3]

    return score, risk, insight, suggestions

st.title("Greentech AI Guidance Layer")
st.markdown("**Prototype demo for SME energy decision support**")
st.write(
    "Questa demo mostra un layer di supporto decisionale che traduce uno scenario energetico aziendale "
    "in raccomandazioni operative per il decision-maker."
)

with st.sidebar:
    st.header("Input scenario")
    solar_level = st.radio("Produzione solare", ["Basso", "Medio", "Alto"])
    consumption_level = st.radio("Consumo aziendale", ["Basso", "Medio", "Alto"])
    battery_level = st.radio("Stato batteria", ["Basso", "Medio", "Alto"])
    price_level = st.radio("Prezzo energia", ["Basso", "Medio", "Alto"])
    critical_slot = st.selectbox(
        "Fascia critica",
        ["08:00–10:00", "10:00–13:00", "13:00–15:00", "15:00–18:00", "18:00–20:00"]
    )
    run = st.button("Genera analisi AI")

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

    c1, c2, c3 = st.columns(3)
    c1.metric("Energy Behavior Score", f"{score}/100")
    c2.metric("Livello di rischio", risk)
    c3.metric("Risparmio stimato", f"€ {savings_value}")

    st.subheader("Insight AI")
    st.info(insight)

    st.subheader("Raccomandazioni operative")
    for i, s in enumerate(suggestions, start=1):
        st.write(f"{i}. {s}")

    st.subheader("Profilo energetico giornaliero")
    fig = create_energy_plot(slots, x, solar_profile, consumption_profile, price_profile)
    st.pyplot(fig)

    st.subheader("Scenario comparison")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("### Scenario standard")
        st.write("Costo energetico giornaliero stimato")
        st.success(f"€ {baseline_cost}")
        st.caption("Gestione reattiva dei carichi")
    with d2:
        st.markdown("### Scenario con AI Guidance")
        st.write("Costo energetico giornaliero stimato")
        st.success(f"€ {optimized_cost}")
        st.caption(f"Risparmio stimato: € {savings_value} ({savings_pct_display}%)")
else:
    st.info("Seleziona i parametri nella sidebar e clicca su 'Genera analisi AI'.")
