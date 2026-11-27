import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. HILFSFUNKTIONEN (Mathematik & Logik)
# -----------------------------------------------------------------------------

def safe_get(val):
    """Wandelt None (leeres Feld) in 0.0 um, damit gerechnet werden kann."""
    if val is None:
        return 0.0
    return float(val)

def kaufm_runden(wert):
    """
    Kaufmännisches Runden auf 2 Nachkommastellen.
    Vermeidet Floating-Point-Fehler und rundet .5 immer auf.
    """
    if wert is None:
        return 0.0
    return int(wert * 100 + 0.5) / 100.0

def format_currency(val):
    """Formatiert Zahl als Währung string."""
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percent(val):
    """Formatiert Zahl als Prozent string."""
    return f"{val:,.2f} %".replace(".", ",")

# -----------------------------------------------------------------------------
# 2. UI & SEITENKONFIGURATION
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Handelskalkulator Pro",
    page_icon="🧮",
    layout="centered"
)

st.title("🧮 Handelskalkulation")
st.markdown("""
Dieser Rechner führt eine vollständige Handelskalkulation durch.
Fahre mit der Maus über die Eingabefelder, um Erklärungen zu den Begriffen zu erhalten.
""")

st.markdown("""
<style>
    /* Tabs Container */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
    }
    /* Nicht ausgewählte Tabs */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #262730;
        color: #ffffff;
        border-radius: 4px 4px 0 0;
        padding: 10px;
        border: 1px solid #4f4f4f;
    }
    /* Ausgewählter Tab */
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: #ffffff;
        border: none;
    }
    /* Hover Effekt */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3e4050;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Tabs erstellen
tab1, tab2, tab3 = st.tabs(["➡️ Vorwärtskalkulation", "⬅️ Rückwärtskalkulation", "📊 Differenzkalkulation"])

# -----------------------------------------------------------------------------
# 3. TAB 1: VORWÄRTSKALKULATION
# -----------------------------------------------------------------------------

with tab1:
    st.header("Vom Einkauf zum Verkauf")
    st.info("Berechnet den notwendigen Verkaufspreis basierend auf Kosten und Zuschlägen.")

    # --- Eingaben ---
    with st.expander("Eingabeparameter", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Einkauf & Intern**")
            lep = st.number_input(
                "Listeneinkaufspreis (€)", min_value=0.0, step=1.00, value=None, format="%.2f", key="v_lep",
                help="Der Preis, der in der Preisliste des Lieferanten steht (Netto, ohne Abzüge).", placeholder="0.00"
            )
            l_rabatt = st.number_input(
                "Liefererrabatt (%)", min_value=0.0, step=0.5, value=None, format="%.2f", key="v_lr",
                help="Rabatt, den uns der Lieferant gewährt (wird vom Listeneinkaufspreis abgezogen).", placeholder="0.00"
            )
            l_skonto = st.number_input(
                "Liefererskonto (%)", min_value=0.0, step=0.1, value=None, format="%.2f", key="v_ls",
                help="Preisnachlass für schnelle Zahlung an den Lieferanten (wird vom Zieleinkaufspreis abgezogen).", placeholder="0.00"
            )
            bezugskosten = st.number_input(
                "Bezugskosten (€)", min_value=0.0, step=0.5, value=None, format="%.2f", key="v_bz",
                help="Kosten für Transport, Verpackung, Zoll oder Versicherung (Eingangsfracht).", placeholder="0.00"
            )
            hkz = st.number_input(
                "Handlungskostenzuschlag (%)", min_value=0.0, step=1.0, value=None, format="%.2f", key="v_hkz",
                help="Zuschlag zur Deckung der Gemeinkosten (Miete, Strom, Personal, Verwaltung).", placeholder="0.00"
            )
            gewinn = st.number_input(
                "Gewinnzuschlag (%)", min_value=0.0, step=1.0, value=None, format="%.2f", key="v_gew",
                help="Der geplante Gewinnanteil des Unternehmens.", placeholder="0.00"
            )

        with col2:
            st.markdown("**Verkauf (Kunde)**")
            k_skonto = st.number_input(
                "Kundenskonto (%)", min_value=0.0, step=0.1, value=None, format="%.2f", key="v_ks",
                help="Skonto, den wir dem Kunden gewähren (i.H. = Im Hundert gerechnet).", placeholder="0.00"
            )
            k_rabatt = st.number_input(
                "Kundenrabatt (%)", min_value=0.0, step=0.5, value=None, format="%.2f", key="v_kr",
                help="Rabatt, den wir dem Kunden gewähren (i.H. = Im Hundert gerechnet).", placeholder="0.00"
            )
            ust = st.number_input(
                "Umsatzsteuer (%)", min_value=0.0, step=1.0, value=None, format="%.2f", key="v_ust",
                help="Gesetzliche Mehrwertsteuer (meist 19% oder 7%).", placeholder="0.00"
            )

    # --- Berechnung ---
    # Werte sicher abrufen (None -> 0.0)
    _lep = safe_get(lep)
    _l_rabatt = safe_get(l_rabatt)
    _l_skonto = safe_get(l_skonto)
    _bezugskosten = safe_get(bezugskosten)
    _hkz = safe_get(hkz)
    _gewinn = safe_get(gewinn)
    _k_skonto = safe_get(k_skonto)
    _k_rabatt = safe_get(k_rabatt)
    _ust = safe_get(ust)

    # Schritt 1: Einkauf
    zep = kaufm_runden(_lep * (1 - _l_rabatt / 100))
    betrag_l_rabatt = kaufm_runden(_lep - zep)

    bep = kaufm_runden(zep * (1 - _l_skonto / 100))
    betrag_l_skonto = kaufm_runden(zep - bep)

    bp = kaufm_runden(bep + _bezugskosten)

    # Schritt 2: Intern
    skp = kaufm_runden(bp * (1 + _hkz / 100))
    betrag_hkz = kaufm_runden(skp - bp)

    bvp = kaufm_runden(skp * (1 + _gewinn / 100))
    betrag_gewinn = kaufm_runden(bvp - skp)

    # Schritt 3: Verkauf (Im Hundert)
    if _k_skonto < 100:
        zvp = kaufm_runden(bvp / (1 - _k_skonto / 100))
    else:
        zvp = 0
    betrag_k_skonto = kaufm_runden(zvp - bvp)

    if _k_rabatt < 100:
        lvp = kaufm_runden(zvp / (1 - _k_rabatt / 100))
    else:
        lvp = 0
    betrag_k_rabatt = kaufm_runden(lvp - zvp)

    brutto = kaufm_runden(lvp * (1 + _ust / 100))
    betrag_ust = kaufm_runden(brutto - lvp)

    # --- Ausgabe Tabelle ---
    data_vorwaerts = [
        ["Listeneinkaufspreis (LEP)", f"- {format_percent(_l_rabatt)}", format_currency(_lep)],
        ["Liefererrabatt", "", f"- {format_currency(betrag_l_rabatt)}"],
        ["Zieleinkaufspreis (ZEP)", f"- {format_percent(_l_skonto)}", format_currency(zep)],
        ["Liefererskonto", "", f"- {format_currency(betrag_l_skonto)}"],
        ["Bareinkaufspreis (BEP)", "", format_currency(bep)],
        ["+ Bezugskosten", "", f"+ {format_currency(_bezugskosten)}"],
        ["Bezugspreis / Einstandspreis", "", format_currency(bp)],
        ["+ Handlungskostenzuschlag", f"{format_percent(_hkz)}", f"+ {format_currency(betrag_hkz)}"],
        ["Selbstkostenpreis", "", format_currency(skp)],
        ["+ Gewinnzuschlag", f"{format_percent(_gewinn)}", f"+ {format_currency(betrag_gewinn)}"],
        ["Barverkaufspreis (Netto)", "", format_currency(bvp)],
        ["+ Kundenskonto (i.H.)", f"{format_percent(_k_skonto)}", f"+ {format_currency(betrag_k_skonto)}"],
        ["Zielverkaufspreis (ZVP)", "", format_currency(zvp)],
        ["+ Kundenrabatt (i.H.)", f"{format_percent(_k_rabatt)}", f"+ {format_currency(betrag_k_rabatt)}"],
        ["Netto-Listenverkaufspreis", "", format_currency(lvp)],
        ["+ Umsatzsteuer", f"{format_percent(_ust)}", f"+ {format_currency(betrag_ust)}"],
        ["**Brutto-Verkaufspreis**", "", f"**{format_currency(brutto)}**"],
    ]

    df_v = pd.DataFrame(data_vorwaerts, columns=["Position", "Satz", "Wert"])

    st.markdown("### Kalkulationsschema")
    st.table(df_v)

    st.markdown("---")
    kpi1, kpi2 = st.columns(2)
    rohgewinn = kaufm_runden(lvp - bp)
    rohgewinn_quote = (rohgewinn / lvp * 100) if lvp > 0 else 0
    kpi1.metric("Rohgewinn (Spanne)", format_currency(rohgewinn))
    kpi2.metric("Handelsspanne", format_percent(rohgewinn_quote))


# -----------------------------------------------------------------------------
# 4. TAB 2: RÜCKWÄRTSKALKULATION
# -----------------------------------------------------------------------------

with tab2:
    st.header("Vom Verkauf zum Einkauf")
    st.warning("Ermittelt, wie teuer der Einkauf maximal sein darf, um einen Marktpreis zu halten.")

    with st.expander("Eingabeparameter", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Verkaufsziel**")
            target_brutto = st.number_input(
                "Gewünschter Brutto-Verkaufspreis (€)", min_value=0.0, step=1.00, value=None, format="%.2f", key="r_brutto",
                help="Der Endpreis inkl. Steuer, den der Kunde maximal zahlen soll/wird.", placeholder="0.00"
            )
            r_ust = st.number_input(
                "Umsatzsteuer (%)", min_value=0.0, step=1.0, value=None, format="%.2f", key="r_ust",
                help="Gesetzliche Mehrwertsteuer.", placeholder="0.00"
            )
            r_k_rabatt = st.number_input(
                "Kundenrabatt (%)", min_value=0.0, step=0.5, value=None, format="%.2f", key="r_kr",
                help="Eingeplanter Rabatt für den Kunden.", placeholder="0.00"
            )
            r_k_skonto = st.number_input(
                "Kundenskonto (%)", min_value=0.0, step=0.1, value=None, format="%.2f", key="r_ks",
                help="Eingeplanter Skonto für den Kunden.", placeholder="0.00"
            )

        with col2:
            st.markdown("**Interne & Lieferanten Kosten**")
            r_gewinn = st.number_input(
                "Gewinnzuschlag (%)", min_value=0.0, step=1.0, value=None, format="%.2f", key="r_gew",
                help="Gewünschte Gewinnmarge.", placeholder="0.00"
            )
            r_hkz = st.number_input(
                "Handlungskostenzuschlag (%)", min_value=0.0, step=1.0, value=None, format="%.2f", key="r_hkz",
                help="Zuschlag für Gemeinkosten.", placeholder="0.00"
            )
            r_bezugskosten = st.number_input(
                "Bezugskosten (€)", min_value=0.0, step=0.5, value=None, format="%.2f", key="r_bz",
                help="Geschätzte Fracht/Zollkosten.", placeholder="0.00"
            )
            r_l_skonto = st.number_input(
                "Liefererskonto (%)", min_value=0.0, step=0.1, value=None, format="%.2f", key="r_ls",
                help="Skonto, den der Lieferant gewährt.", placeholder="0.00"
            )
            r_l_rabatt = st.number_input(
                "Liefererrabatt (%)", min_value=0.0, step=0.5, value=None, format="%.2f", key="r_lr",
                help="Rabatt, den der Lieferant gewährt.", placeholder="0.00"
            )

    # --- Berechnung (Rückwärts) ---
    _target_brutto = safe_get(target_brutto)
    _r_ust = safe_get(r_ust)
    _r_k_rabatt = safe_get(r_k_rabatt)
    _r_k_skonto = safe_get(r_k_skonto)
    _r_gewinn = safe_get(r_gewinn)
    _r_hkz = safe_get(r_hkz)
    _r_bezugskosten = safe_get(r_bezugskosten)
    _r_l_skonto = safe_get(r_l_skonto)
    _r_l_rabatt = safe_get(r_l_rabatt)

    # 1. Von Brutto zu Netto
    lvp = kaufm_runden(_target_brutto / (1 + _r_ust / 100))
    betrag_ust = kaufm_runden(_target_brutto - lvp)

    # 2. Kundenabzüge
    zvp = kaufm_runden(lvp * (1 - _r_k_rabatt / 100))
    betrag_k_rabatt = kaufm_runden(lvp - zvp)

    bvp = kaufm_runden(zvp * (1 - _r_k_skonto / 100))
    betrag_k_skonto = kaufm_runden(zvp - bvp)

    # 3. Interne Abzüge
    skp = kaufm_runden(bvp / (1 + _r_gewinn / 100))
    betrag_gewinn = kaufm_runden(bvp - skp)

    bp = kaufm_runden(skp / (1 + _r_hkz / 100))
    betrag_hkz = kaufm_runden(skp - bp)

    # 4. Einkauf
    bep = kaufm_runden(bp - _r_bezugskosten)

    if _r_l_skonto < 100:
        zep = kaufm_runden(bep / (1 - _r_l_skonto / 100))
    else:
        zep = 0
    betrag_l_skonto = kaufm_runden(zep - bep)

    if _r_l_rabatt < 100:
        lep = kaufm_runden(zep / (1 - _r_l_rabatt / 100))
    else:
        lep = 0
    betrag_l_rabatt = kaufm_runden(lep - zep)

    data_rueck = [
        ["Brutto-Verkaufspreis", "", format_currency(_target_brutto)],
        ["- Umsatzsteuer", f"{format_percent(_r_ust)}", f"- {format_currency(betrag_ust)}"],
        ["Netto-Listenverkaufspreis", "", format_currency(lvp)],
        ["- Kundenrabatt", f"{format_percent(_r_k_rabatt)}", f"- {format_currency(betrag_k_rabatt)}"],
        ["Zielverkaufspreis", "", format_currency(zvp)],
        ["- Kundenskonto", f"{format_percent(_r_k_skonto)}", f"- {format_currency(betrag_k_skonto)}"],
        ["Barverkaufspreis", "", format_currency(bvp)],
        ["- Gewinnzuschlag (i.H.)", f"{format_percent(_r_gewinn)}", f"- {format_currency(betrag_gewinn)}"],
        ["Selbstkostenpreis", "", format_currency(skp)],
        ["- Handlungskosten (i.H.)", f"{format_percent(_r_hkz)}", f"- {format_currency(betrag_hkz)}"],
        ["Bezugspreis / Einstandspreis", "", format_currency(bp)],
        ["- Bezugskosten", "", f"- {format_currency(_r_bezugskosten)}"],
        ["Bareinkaufspreis", "", format_currency(bep)],
        ["+ Liefererskonto (i.H.)", f"{format_percent(_r_l_skonto)}", f"+ {format_currency(betrag_l_skonto)}"],
        ["Zieleinkaufspreis", "", format_currency(zep)],
        ["+ Liefererrabatt (i.H.)", f"{format_percent(_r_l_rabatt)}", f"+ {format_currency(betrag_l_rabatt)}"],
        ["**Maximaler Listeneinkaufspreis**", "", f"**{format_currency(lep)}**"]
    ]

    df_r = pd.DataFrame(data_rueck, columns=["Position", "Satz", "Wert"])

    st.markdown("### Kalkulationsschema")
    st.table(df_r)


# -----------------------------------------------------------------------------
# 5. TAB 3: DIFFERENZKALKULATION
# -----------------------------------------------------------------------------

with tab3:
    st.header("Gewinnermittlung")
    st.success("Berechnet den tatsächlichen Gewinn, wenn Einkaufs- und Verkaufspreis vom Markt diktiert werden.")

    # --- Eingaben ---
    with st.expander("Eingabeparameter", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Fixe Preise**")
            d_lep = st.number_input("Listeneinkaufspreis (€)", min_value=0.0, step=1.00, value=None, format="%.2f", key="d_lep", help="Gegebener Einkaufspreis laut Liste.", placeholder="0.00")
            d_brutto = st.number_input("Brutto-Verkaufspreis (€)", min_value=0.0, step=1.00, value=None, format="%.2f", key="d_brutto", help="Gegebener Marktpreis (Brutto).", placeholder="0.00")

        with col2:
            st.markdown("**Konditionen**")
            d_l_rabatt = st.number_input("L-Rabatt (%)", min_value=0.0, step=0.5, value=None, format="%.2f", key="d_lr", help="Liefererrabatt.", placeholder="0.00")
            d_l_skonto = st.number_input("L-Skonto (%)", min_value=0.0, step=0.1, value=None, format="%.2f", key="d_ls", help="Liefererskonto.", placeholder="0.00")
            d_bezug = st.number_input("Bezugskosten (€)", min_value=0.0, step=0.5, value=None, format="%.2f", key="d_bz", help="Eingangsfracht/Zoll.", placeholder="0.00")
            d_hkz = st.number_input("Handlungskosten (%)", min_value=0.0, step=1.0, value=None, format="%.2f", key="d_hkz", help="Gemeinkosten.", placeholder="0.00")
            d_k_skonto = st.number_input("K-Skonto (%)", min_value=0.0, step=0.1, value=None, format="%.2f", key="d_ks", help="Kundenskonto.", placeholder="0.00")
            d_k_rabatt = st.number_input("K-Rabatt (%)", min_value=0.0, step=0.5, value=None, format="%.2f", key="d_kr", help="Kundenrabatt.", placeholder="0.00")
            d_ust = st.number_input("USt (%)", min_value=0.0, step=1.0, value=None, format="%.2f", key="d_ust", help="Umsatzsteuer.", placeholder="0.00")

    # --- Berechnung ---
    _d_lep = safe_get(d_lep)
    _d_brutto = safe_get(d_brutto)
    _d_l_rabatt = safe_get(d_l_rabatt)
    _d_l_skonto = safe_get(d_l_skonto)
    _d_bezug = safe_get(d_bezug)
    _d_hkz = safe_get(d_hkz)
    _d_k_skonto = safe_get(d_k_skonto)
    _d_k_rabatt = safe_get(d_k_rabatt)
    _d_ust = safe_get(d_ust)

    # 1. Vorwärts bis Selbstkosten
    d_zep = kaufm_runden(_d_lep * (1 - _d_l_rabatt / 100))
    d_bep = kaufm_runden(d_zep * (1 - _d_l_skonto / 100))
    d_bp = kaufm_runden(d_bep + _d_bezug)
    d_skp = kaufm_runden(d_bp * (1 + _d_hkz / 100))

    # 2. Rückwärts bis Barverkaufspreis
    d_lvp = kaufm_runden(_d_brutto / (1 + _d_ust / 100))
    d_zvp = kaufm_runden(d_lvp * (1 - _d_k_rabatt / 100))
    d_bvp = kaufm_runden(d_zvp * (1 - _d_k_skonto / 100))

    # 3. Differenz
    diff_euro = kaufm_runden(d_bvp - d_skp)
    if d_skp > 0:
        diff_prozent = (diff_euro / d_skp) * 100
    else:
        diff_prozent = 0.0

    # --- Darstellung ---
    st.markdown("### Ergebnis")

    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Selbstkosten", format_currency(d_skp))
    col_res2.metric("Barverkaufspreis (Nettoerlös)", format_currency(d_bvp))

    col_res3.metric(
        "Gewinn / Verlust",
        f"{format_currency(diff_euro)}",
        f"{format_percent(diff_prozent)}",
        delta_color="normal"
    )

    with st.expander("Details anzeigen"):
        st.write(f"Einkaufsweg: LEP {_d_lep}€ -> BP {d_bp}€ -> **SKP {d_skp}€**")
        st.write(f"Verkaufsweg: Brutto {_d_brutto}€ -> LVP {d_lvp}€ -> **BVP {d_bvp}€**")
        if diff_euro >= 0:
            st.success(f"Du machst einen Gewinn von {format_currency(diff_euro)} ({format_percent(diff_prozent)} Aufschlag).")
        else:
            st.error(f"Du machst einen Verlust von {format_currency(diff_euro)}.")
