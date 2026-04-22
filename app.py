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
        max-width: 1500px;
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
    .audit-box {
        background: #f8fbf9;
        padding: 1rem 1.2rem;
        border-radius: 18px;
        border: 1px solid #dbe7df;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
    }
    .footer-note {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Assunzioni e mapping
# -----------------------------
COUNTRY_ENERGY_PRICE = {
    "Italia": 0.25,
    "Spagna": 0.21,
    "Germania": 0.26
}

COUNTRY_EMISSION_FACTOR = {
    # Assunzioni illustrative interne per la demo (kg CO2 / kWh)
    "Italia": 0.23,
    "Spagna": 0.18,
    "Germania": 0.35
}

SECTOR_PROFILES = {
    "Manifatturiero": {
        "base_load": 3,
        "shiftability": 1,
        "description": "Consumi elevati e spesso concentrati nelle ore produttive."
    },
    "Retail": {
        "base_load": 2,
        "shiftability": 2,
        "description": "Consumi medi, con forte dipendenza dagli orari di apertura."
    },
    "Food & Beverage": {
        "base_load": 3,
        "shiftability": 1,
        "description": "Consumi continui e vincoli operativi elevati per refrigerazione e sicurezza."
    },
    "Consulenza / Uffici": {
        "base_load": 1,
        "shiftability": 3,
        "description": "Consumi più flessibili, legati soprattutto a HVAC, illuminazione e IT."
    }
}

OPERATING_HOURS_MAP = {
    "08:00–18:00": 10,
    "06:00–14:00": 8,
    "14:00–22:00": 8,
    "24/7": 24,
    "09:00–20:00": 11
}

FLEXIBILITY_MAP = {
    "Bassa": 1,
    "Media": 2,
    "Alta": 3
}

SOLAR_MAP = {
    "Bassa (< 200 kWh/giorno)": "Basso",
    "Media (200–500 kWh/giorno)": "Medio",
    "Alta (> 500 kWh/giorno)": "Alto"
}

BATTERY_MAP = {
    "Nessuna": "Nessuna",
    "Bassa (0–20% capacità disponibile)": "Basso",
    "Media (20–60% capacità disponibile)": "Medio",
    "Alta (> 60% capacità disponibile)": "Alto"
}

PRICE_MAP = {
    "Basso (< 0,18 €/kWh)": "Basso",
    "Medio (0,18–0,24 €/kWh)": "Medio",
    "Alto (> 0,24 €/kWh)": "Alto"
}

PLANT_MAP = {
    "Fotovoltaico standard": 1.0,
    "Fotovoltaico premium / high-efficiency": 1.1,
    "Fotovoltaico + accumulo": 1.2
}

PRIORITY_OPTIONS = ["Costo", "Continuità operativa", "Sostenibilità"]

# -----------------------------
# Funzioni
# -----------------------------
def build_profiles(solar_level, consumption_level, battery_level, price_level, sector, operating_hours):
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

    # Modifica leggera dei profili in base al settore
    sector_load = SECTOR_PROFILES[sector]["base_load"]
    hour_multiplier = 1.15 if operating_hours == "24/7" else 1.0

    solar_profile = solar_base[solar_level]
    consumption_profile = np.clip(consumption_base[consumption_level] * hour_multiplier + (sector_load - 2) * 0.4, 0, None)
    price_profile = price_base[price_level]

    battery_capacity = {
        "Nessuna": 0,
        "Basso": 2,
        "Medio": 5,
        "Alto": 8
    }[battery_level]

    return slots, x, solar_profile, consumption_profile, price_profile, battery_capacity


def create_energy_plot(slots, x, solar_profile, consumption_profile, price_profile):
    fig, ax = plt.subplots(figsize=(16, 7.5))
    ax.plot(x, solar_profile, marker="o", linewidth=3.2, markersize=10, label="Produzione solare stimata")
    ax.plot(x, consumption_profile, marker="o", linewidth=3.2, markersize=10, label="Consumo aziendale stimato")
    ax.plot(x, price_profile, marker="o", linestyle="--", linewidth=2.8, markersize=9, label="Indice prezzo energia")

    ax.set_xticks(x)
    ax.set_xticklabels(slots, fontsize=13)
    ax.set_title("Profilo energetico giornaliero", fontsize=18, pad=18)
    ax.set_xlabel("Fasce orarie", fontsize=13)
    ax.set_ylabel("Indice relativo", fontsize=13)
    ax.tick_params(axis='y', labelsize=12)
    ax.legend(fontsize=12, loc="upper left")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig


def classify_consumption(monthly_kwh):
    if monthly_kwh < 5000:
        return "Basso"
    elif monthly_kwh < 20000:
        return "Medio"
    return "Alto"


def scenario_comparison(monthly_bill, score, priority):
    if score >= 75:
        savings_pct = 0.18
    elif score >= 50:
        savings_pct = 0.12
    else:
        savings_pct = 0.07

    if priority == "Costo":
        savings_pct += 0.02
    elif priority == "Continuità operativa":
        savings_pct -= 0.01

    savings_pct = max(0.04, min(0.22, savings_pct))

    baseline_cost = round(monthly_bill, 1)
    optimized_cost = round(baseline_cost * (1 - savings_pct), 1)
    savings_value = round(baseline_cost - optimized_cost, 1)
    savings_pct_display = int(round(savings_pct * 100))

    return baseline_cost, optimized_cost, savings_value, savings_pct_display


def estimate_carbon_impact(country, monthly_kwh, savings_pct_display):
    emission_factor = COUNTRY_EMISSION_FACTOR[country]  # kg CO2 / kWh (assunzione demo)
    annual_kwh = monthly_kwh * 12
    avoided_kwh = annual_kwh * (savings_pct_display / 100)
    avoided_co2_tons = round((avoided_kwh * emission_factor) / 1000, 2)
    return avoided_co2_tons


def compliance_relevance(priority, country, avoided_co2_tons):
    if priority == "Sostenibilità" or avoided_co2_tons >= 8:
        return "Alta"
    elif country in ["Germania", "Italia"] and avoided_co2_tons >= 4:
        return "Media"
    return "Base"


def energy_guidance(
    country,
    sector,
    square_meters,
    monthly_kwh,
    monthly_bill,
    operating_hours,
    flexibility,
    solar_level,
    battery_level,
    price_level,
    plant_type,
    critical_slot,
    priority
):
    score = 100
    suggestions = []

    consumption_level = classify_consumption(monthly_kwh)

    # Penalità / bonus base
    if consumption_level == "Alto":
        score -= 18
    elif consumption_level == "Medio":
        score -= 8

    if solar_level == "Basso":
        score -= 18
    elif solar_level == "Medio":
        score -= 8

    if battery_level == "Nessuna":
        score -= 12
    elif battery_level == "Basso":
        score -= 10
    elif battery_level == "Medio":
        score -= 4

    if price_level == "Alto":
        score -= 18
    elif price_level == "Medio":
        score -= 8

    # Vincoli settore / flessibilità
    shiftability = SECTOR_PROFILES[sector]["shiftability"]
    flexibility_value = FLEXIBILITY_MAP[flexibility]
    if shiftability <= 1 and flexibility_value == 1:
        score -= 10
    elif flexibility_value == 3:
        score += 4

    if operating_hours == "24/7":
        score -= 8

    if plant_type == "Fotovoltaico + accumulo":
        score += 6
    elif plant_type == "Fotovoltaico premium / high-efficiency":
        score += 3

    # Efficienza spaziale molto semplice
    intensity = monthly_kwh / max(square_meters, 1)
    if intensity > 20:
        score -= 8
    elif intensity < 8:
        score += 3

    score = max(0, min(100, score))

    if score >= 75:
        risk = "Basso"
        insight = "Profilo energetico complessivamente efficiente, con margini di ottimizzazione incrementale e buona leggibilità decisionale."
    elif score >= 50:
        risk = "Medio"
        insight = "Profilo energetico discreto, ma con aree di miglioramento nella distribuzione dei carichi, nella gestione operativa e nell’utilizzo delle risorse energetiche."
    else:
        risk = "Alto"
        insight = "Profilo energetico critico: elevata esposizione a inefficienze operative, costi evitabili e limitata flessibilità nella gestione dei carichi."

    # Raccomandazioni contestuali
    if solar_level == "Alto" and flexibility_value >= 2:
        suggestions.append(
            "Concentrare i carichi secondari o differibili nelle ore di maggiore disponibilità solare per aumentare l’autoconsumo."
        )

    if price_level == "Alto" and battery_level in ["Medio", "Alto"]:
        suggestions.append(
            f"Ridurre il prelievo dalla rete nella fascia {critical_slot}, privilegiando l’utilizzo dell’energia accumulata."
        )

    if battery_level == "Nessuna" and priority == "Continuità operativa":
        suggestions.append(
            "Valutare l’integrazione di un sistema di accumulo per aumentare resilienza energetica e continuità del servizio."
        )

    if sector == "Manifatturiero" and flexibility == "Bassa":
        suggestions.append(
            "Evitare raccomandazioni di spostamento della linea principale: intervenire invece su carichi ausiliari, HVAC, compressori o sistemi non core."
        )

    if sector == "Retail" and operating_hours in ["09:00–20:00", "14:00–22:00"]:
        suggestions.append(
            "Ottimizzare illuminazione, climatizzazione e picchi serali, poiché le fasce operative coincidono con finestre di costo potenzialmente elevate."
        )

    if sector == "Food & Beverage":
        suggestions.append(
            "Mantenere prioritaria la continuità dei carichi critici, intervenendo sulla riduzione dei consumi accessori e non sui processi essenziali."
        )

    if monthly_bill > (monthly_kwh * COUNTRY_ENERGY_PRICE[country] * 1.15):
        suggestions.append(
            "La bolletta dichiarata risulta elevata rispetto al profilo di consumo: verificare struttura tariffaria, oneri accessori e profilo di prelievo."
        )

    if priority == "Sostenibilità":
        suggestions.append(
            "Integrare il piano energetico con metriche di riduzione CO₂ per supportare ESG reporting e narrativa di compliance."
        )

    default_messages = [
        "Mantenere monitoraggio continuo dei flussi energetici per individuare tempestivamente opportunità di efficientamento.",
        "Valutare una migliore distribuzione interna dei carichi per aumentare l’autoconsumo energetico.",
        "Consolidare una pianificazione energetica orientata a costo, disponibilità, vincoli operativi e continuità del servizio."
    ]

    for msg in default_messages:
        if len(suggestions) < 3:
            suggestions.append(msg)

    suggestions = suggestions[:3]

    # Auditabilità / spiegazione inferenza
    inference_lines = [
        f"Paese selezionato: {country} (prezzo energia di riferimento demo: {COUNTRY_ENERGY_PRICE[country]:.2f} €/kWh).",
        f"Settore aziendale: {sector} ({SECTOR_PROFILES[sector]['description']})",
        f"Consumo mensile dichiarato: {monthly_kwh:,.0f} kWh/mese | Bolletta media: € {monthly_bill:,.0f}/mese.",
        f"Orari attività: {operating_hours} | Flessibilità operativa: {flexibility}.",
        f"Produzione solare: {solar_level} | Batteria: {battery_level} | Tipo impianto: {plant_type}.",
        f"Priorità strategica selezionata: {priority}."
    ]

    return score, risk, insight, suggestions, inference_lines, consumption_level


def generate_executive_profile(score, risk, sector, monthly_kwh, price_level, battery_level):
    if monthly_kwh > 20000 and price_level == "Alto":
        profile = "PMI energivora esposta a forte pressione sui costi operativi e alla variabilità del prezzo dell’energia."
    elif battery_level in ["Medio", "Alto"] and risk == "Basso":
        profile = "PMI con buona base infrastrutturale per strategie avanzate di autoconsumo e gestione flessibile dell’energia."
    elif sector == "Consulenza / Uffici":
        profile = "PMI a profilo energetico leggero, con opportunità di ottimizzazione prevalentemente gestionale e comportamentale."
    else:
        profile = "PMI con profilo energetico intermedio e margini di efficientamento legati alla pianificazione dei carichi."

    if risk == "Basso":
        priority = "Consolidare l’efficienza raggiunta e introdurre logiche di pianificazione energetica più granulari."
    elif risk == "Medio":
        priority = "Ridurre la variabilità dei carichi e migliorare il coordinamento tra consumo, accumulo e costo dell’energia."
    else:
        priority = "Intervenire sui carichi critici e ridurre l’esposizione alle fasce a maggiore costo energetico."

    if score >= 75:
        executive_message = (
            "Lo scenario evidenzia una configurazione già efficiente: il valore aggiunto dell’AI è soprattutto incrementale, "
            "orientato a stabilità operativa, leggibilità decisionale e ulteriore ottimizzazione."
        )
    elif score >= 50:
        executive_message = (
            "Lo scenario presenta una base discreta ma non ancora ottimizzata: il layer AI genera valore nel coordinare meglio "
            "profilo di consumo, vincoli operativi, costo dell’energia e priorità manageriali."
        )
    else:
        executive_message = (
            "Lo scenario mostra una criticità energetica significativa: il layer AI assume una funzione prioritaria di supporto "
            "decisionale per contenere costi, ridurre sprechi e migliorare la sostenibilità operativa."
        )

    return profile, priority, executive_message


def generate_report_text(
    country,
    sector,
    square_meters,
    monthly_kwh,
    monthly_bill,
    operating_hours,
    flexibility,
    plant_type,
    priority_selected,
    score,
    risk,
    insight,
    suggestions,
    baseline_cost,
    optimized_cost,
    savings_value,
    savings_pct_display,
    profile,
    priority,
    executive_message,
    critical_slot,
    avoided_co2_tons,
    compliance_level,
    inference_lines
):
    report = f"""
GREENTECH AI GUIDANCE LAYER
Report sintetico di scenario

1. Company profile
- Paese: {country}
- Settore: {sector}
- Superficie: {square_meters} m²
- Consumo mensile: {monthly_kwh:,.0f} kWh/mese
- Bolletta media: € {monthly_bill:,.0f}/mese
- Orari attività: {operating_hours}
- Flessibilità operativa: {flexibility}
- Tipo impianto: {plant_type}
- Priorità selezionata: {priority_selected}

2. Executive overview
- Energy Behavior Score: {score}/100
- Livello di rischio energetico: {risk}
- Risparmio mensile stimato: € {savings_value}
- Riduzione CO₂ stimata: {avoided_co2_tons} t/anno
- Rilevanza compliance / ESG: {compliance_level}

3. Insight AI
{insight}

4. Raccomandazioni operative
1) {suggestions[0]}
2) {suggestions[1]}
3) {suggestions[2]}

5. Scenario comparison
- Scenario baseline: € {baseline_cost}/mese
- Scenario con AI Guidance: € {optimized_cost}/mese
- Risparmio stimato: € {savings_value}/mese ({savings_pct_display}%)

6. Profilo aziendale sintetico
- Profilo del cliente: {profile}
- Priorità strategica: {priority}

7. Executive takeaway
{executive_message}

8. Auditabilità del risultato
- {inference_lines[0]}
- {inference_lines[1]}
- {inference_lines[2]}
- {inference_lines[3]}
- {inference_lines[4]}
- {inference_lines[5]}

Nota metodologica
Il prototipo utilizza logiche dimostrative e assunzioni illustrative, finalizzate a rappresentare il valore consulenziale del layer AI.
Fascia critica analizzata: {critical_slot}
""".strip()
    return report


# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>⚡ Greentech AI Guidance Layer</h1>
    <p>
        Prototipo di supporto decisionale per PMI: trasforma uno scenario energetico personalizzato
        in insight operativi, raccomandazioni, spiegabilità e confronto economico.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Configura lo scenario")

    st.subheader("Profilo aziendale")
    country = st.selectbox(
        "Paese",
        ["Italia", "Spagna", "Germania"],
        help="Serve a contestualizzare il prezzo dell’energia e il profilo regolatorio in modo illustrativo."
    )

    sector = st.selectbox(
        "Settore aziendale",
        ["Manifatturiero", "Retail", "Food & Beverage", "Consulenza / Uffici"],
        help="Il settore influenza intensità di consumo, rigidità operativa e possibilità di spostamento dei carichi."
    )

    square_meters = st.number_input(
        "Superficie sito (m²)",
        min_value=100,
        max_value=50000,
        value=2500,
        step=100,
        help="Valore indicativo utile per contestualizzare l’intensità energetica dell’azienda."
    )

    operating_hours = st.selectbox(
        "Orari attività",
        ["08:00–18:00", "06:00–14:00", "14:00–22:00", "24/7", "09:00–20:00"],
        help="L’orario operativo influenza la sovrapposizione con le fasce di prezzo e con la produzione solare."
    )

    flexibility = st.radio(
        "Flessibilità operativa",
        ["Bassa", "Media", "Alta"],
        help="Indica quanto l’azienda può modificare carichi o attività senza impattare il core business."
    )

    st.subheader("Profilo energetico")
    monthly_kwh = st.slider(
        "Consumo mensile (kWh/mese)",
        min_value=1000,
        max_value=60000,
        value=12000,
        step=500,
        help="Valore indicativo del fabbisogno energetico mensile dell’azienda."
    )

    monthly_bill = st.slider(
        "Bolletta media mensile (€ / mese)",
        min_value=500,
        max_value=20000,
        value=3000,
        step=100,
        help="Serve per stimare il baseline economico e il potenziale risparmio."
    )

    plant_type = st.selectbox(
        "Tipo impianto",
        ["Fotovoltaico standard", "Fotovoltaico premium / high-efficiency", "Fotovoltaico + accumulo"],
        help="Il tipo di impianto influenza la qualità della base tecnica disponibile per l’ottimizzazione."
    )

    solar_label = st.radio(
        "Produzione solare stimata",
        list(SOLAR_MAP.keys()),
        help="Range indicativo di produzione giornaliera. È una semplificazione utile per la demo."
    )

    battery_label = st.radio(
        "Stato batteria / accumulo",
        list(BATTERY_MAP.keys()),
        help="Seleziona la disponibilità di accumulo. Se assente, alcune strategie non saranno proponibili."
    )

    price_label = st.radio(
        "Prezzo energia / fascia prevalente",
        list(PRICE_MAP.keys()),
        help="Range semplificato per descrivere il contesto di costo dell’energia."
    )

    critical_slot = st.selectbox(
        "Fascia critica",
        ["08:00–10:00", "10:00–13:00", "13:00–15:00", "15:00–18:00", "18:00–20:00"],
        help="Finestra temporale su cui concentrare l’analisi delle raccomandazioni."
    )

    priority_selected = st.selectbox(
        "Priorità strategica",
        PRIORITY_OPTIONS,
        help="Seleziona cosa pesa di più nella raccomandazione: costo, continuità o sostenibilità."
    )

    run = st.button("Genera analisi AI", use_container_width=True)

# -----------------------------
# Main
# -----------------------------
if run:
    solar_level = SOLAR_MAP[solar_label]
    battery_level = BATTERY_MAP[battery_label]
    price_level = PRICE_MAP[price_label]

    score, risk, insight, suggestions, inference_lines, consumption_level = energy_guidance(
        country,
        sector,
        square_meters,
        monthly_kwh,
        monthly_bill,
        operating_hours,
        flexibility,
        solar_level,
        battery_level,
        price_level,
        plant_type,
        critical_slot,
        priority_selected
    )

    slots, x, solar_profile, consumption_profile, price_profile, battery_capacity = build_profiles(
        solar_level, consumption_level, battery_level, price_level, sector, operating_hours
    )

    baseline_cost, optimized_cost, savings_value, savings_pct_display = scenario_comparison(
        monthly_bill, score, priority_selected
    )

    profile, priority, executive_message = generate_executive_profile(
        score, risk, sector, monthly_kwh, price_level, battery_level
    )

    avoided_co2_tons = estimate_carbon_impact(country, monthly_kwh, savings_pct_display)
    compliance_level = compliance_relevance(priority_selected, country, avoided_co2_tons)

    report_text = generate_report_text(
        country,
        sector,
        square_meters,
        monthly_kwh,
        monthly_bill,
        operating_hours,
        flexibility,
        plant_type,
        priority_selected,
        score,
        risk,
        insight,
        suggestions,
        baseline_cost,
        optimized_cost,
        savings_value,
        savings_pct_display,
        profile,
        priority,
        executive_message,
        critical_slot,
        avoided_co2_tons,
        compliance_level,
        inference_lines
    )

    if risk == "Basso":
        risk_class = "risk-low"
    elif risk == "Medio":
        risk_class = "risk-medium"
    else:
        risk_class = "risk-high"

    # KPI
    st.markdown('<div class="section-title">Executive overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

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
            <div class="small-label">Risparmio mensile stimato</div>
            <p class="big-number">€ {savings_value}</p>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="card">
            <div class="small-label">CO₂ evitata stimata</div>
            <p class="big-number">{avoided_co2_tons} t/anno</p>
        </div>
        """, unsafe_allow_html=True)

    # Insight + Suggestions
    left, right = st.columns([1, 1])

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
        st.markdown('<div class="section-title">Profilo aziendale sintetico</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="compare-box">
            <div class="small-label">Profilo del cliente</div>
            <p>{profile}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="compare-box">
            <div class="small-label">Priorità strategica</div>
            <p>{priority}</p>
        </div>
        """, unsafe_allow_html=True)

    # Grafico full width
    st.markdown('<div class="section-title">Profilo energetico giornaliero</div>', unsafe_allow_html=True)
    fig = create_energy_plot(slots, x, solar_profile, consumption_profile, price_profile)
    st.pyplot(fig, use_container_width=True)

    # Comparison
    st.markdown('<div class="section-title">Scenario comparison</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)

    with d1:
        st.markdown(f"""
        <div class="compare-box">
            <div class="small-label">Scenario baseline</div>
            <p class="big-number">€ {baseline_cost}</p>
            <p>Costo energetico mensile dichiarato</p>
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

    with d3:
        st.markdown(f"""
        <div class="compare-box">
            <div class="small-label">Compliance / sustainability relevance</div>
            <p class="big-number">{compliance_level}</p>
            <p>Indicatore dimostrativo utile per reporting e orientamento ESG</p>
        </div>
        """, unsafe_allow_html=True)

    # Auditabilità
    st.markdown('<div class="section-title">How the AI generated this recommendation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="audit-box">
        <ul>
            <li>{inference_lines[0]}</li>
            <li>{inference_lines[1]}</li>
            <li>{inference_lines[2]}</li>
            <li>{inference_lines[3]}</li>
            <li>{inference_lines[4]}</li>
            <li>{inference_lines[5]}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Executive takeaway
    st.markdown('<div class="section-title">Executive takeaway</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
        {executive_message}
    </div>
    """, unsafe_allow_html=True)

    # Download e next step
    st.markdown('<div class="section-title">Output consulenziale</div>', unsafe_allow_html=True)
    c_download, c_next = st.columns([1, 1])

    with c_download:
        st.download_button(
            label="Scarica report sintetico",
            data=report_text,
            file_name="greentech_ai_guidance_report.txt",
            mime="text/plain",
            use_container_width=True
        )

    with c_next:
        st.markdown("""
        <div class="card">
            <div class="small-label">Prossimo step consulenziale</div>
            <p>Trasformare questo assessment in audit personalizzato per settore, paese, struttura tariffaria, emissioni e compliance ESG.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="footer-note">Nota: il prototipo utilizza scenari semplificati e assunzioni illustrative. Le raccomandazioni non sostituiscono un audit tecnico-commerciale completo, ma mostrano come un layer AI possa tradurre dati energetici e vincoli aziendali in indicazioni operative spiegabili.</div>',
        unsafe_allow_html=True
    )

else:
    st.markdown("""
    <div class="card">
        <strong>Come usare la demo</strong><br><br>
        1. Configura i parametri nella sidebar.<br>
        2. Inserisci un profilo aziendale ed energetico più realistico.<br>
        3. Clicca su <em>Genera analisi AI</em>.<br>
        4. Osserva KPI, raccomandazioni operative, spiegazione dell’inferenza, grafico, confronto economico e output di sostenibilità.
    </div>
    """, unsafe_allow_html=True)
