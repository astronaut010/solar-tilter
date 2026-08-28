import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from solar_model import simulate_pv_system
from battery_model import simulate_battery


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Multi-Tilt Solar Intelligence",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# CUSTOM UI
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main {
        background: #f6f8fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    .hero {
        padding: 30px 35px;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1f2937 55%,
            #374151 100%
        );
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        font-size: 42px;
        margin-bottom: 8px;
        font-weight: 750;
    }

    .hero p {
        color: #d1d5db;
        font-size: 17px;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 10px;
        color: #111827;
    }

    .info-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.04);
    }

    .metric-label {
        color: #6b7280;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #111827;
        font-size: 28px;
        font-weight: 750;
    }

    .tag {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #eef2ff;
        color: #3730a3;
        font-size: 12px;
        font-weight: 700;
        margin-right: 5px;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        font-size: 13px;
        margin-top: 50px;
        padding: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>☀️ Multi-Tilt Solar Intelligence</h1>
        <p>
        Simulation platform for evaluating multiple permanently fixed
        photovoltaic orientations against a conventional fixed-angle array.
        </p>
        <br>
        <span class="tag">PV SYSTEM MODEL</span>
        <span class="tag">BATTERY STORAGE</span>
        <span class="tag">SOLAR GEOMETRY</span>
        <span class="tag">THEORETICAL VALIDATION</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.markdown("## ⚙️ Simulation Setup")
st.sidebar.caption("Configure the theoretical PV system.")

latitude = st.sidebar.number_input(
    "Latitude (°)",
    min_value=-60.0,
    max_value=60.0,
    value=10.0,
    step=0.1
)

longitude = st.sidebar.number_input(
    "Longitude (°)",
    min_value=-180.0,
    max_value=180.0,
    value=78.0,
    step=0.1
)

day_of_year = st.sidebar.slider(
    "Day of Year",
    1,
    365,
    172
)

st.sidebar.markdown("---")

panel_rating = st.sidebar.number_input(
    "Panel Rating (W)",
    min_value=10,
    max_value=1000,
    value=100,
    step=10
)

temperature = st.sidebar.slider(
    "Panel Temperature (°C)",
    10,
    70,
    30
)

surface_azimuth = st.sidebar.slider(
    "Panel Azimuth (°)",
    0,
    359,
    180
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📐 Fixed Panel Tilts")

tilt1 = st.sidebar.slider("Panel 1 — β₁", 0, 90, 10)
tilt2 = st.sidebar.slider("Panel 2 — β₂", 0, 90, 25)
tilt3 = st.sidebar.slider("Panel 3 — β₃", 0, 90, 40)
tilt4 = st.sidebar.slider("Panel 4 — β₄", 0, 90, 55)

tilts = [tilt1, tilt2, tilt3, tilt4]

st.sidebar.markdown("---")

battery_capacity = st.sidebar.number_input(
    "Battery Capacity (kWh)",
    min_value=0.1,
    max_value=50.0,
    value=2.0,
    step=0.1
)

initial_soc = st.sidebar.slider(
    "Initial Battery SOC (%)",
    0,
    100,
    30
)

load_power = st.sidebar.number_input(
    "Constant Load (W)",
    min_value=0,
    max_value=5000,
    value=100,
    step=10
)


# ---------------------------------------------------------
# SIMULATION BUTTON
# ---------------------------------------------------------

run = st.sidebar.button(
    "▶ RUN SIMULATION",
    use_container_width=True
)


# Run automatically first time
if "has_run" not in st.session_state:
    st.session_state.has_run = True
    run = True


# ---------------------------------------------------------
# SIMULATION
# ---------------------------------------------------------

if run:

    with st.spinner("Running solar and battery simulation..."):

        data = simulate_pv_system(
            latitude=latitude,
            longitude=longitude,
            day_of_year=day_of_year,
            tilts=tilts,
            panel_rating=panel_rating,
            temperature=temperature,
            surface_azimuth=surface_azimuth
        )

        load_array = np.full(
            len(data),
            load_power
        )

        battery = simulate_battery(
            pv_power=data["Total PV Power"].values,
            load_power=load_array,
            battery_capacity_kwh=battery_capacity,
            initial_soc=initial_soc
        )

        data["Battery SOC"] = battery["SOC"]
        data["Battery Power"] = battery["Battery Power"]
        data["Unmet Load Wh"] = battery["Unmet Load"]


    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    total_energy = data["Energy Wh"].sum() / 1000

    peak_power = data["Total PV Power"].max()

    final_soc = data["Battery SOC"].iloc[-1]

    unmet_energy = data["Unmet Load Wh"].sum() / 1000

    panel_energy = [
        (
            data[f"Panel {i} Power"] * (5 / 60)
        ).sum() / 1000
        for i in range(1, 5)
    ]

    st.markdown(
        '<div class="section-title">System Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Daily PV Energy",
            f"{total_energy:.2f} kWh"
        )

    with c2:
        st.metric(
            "Peak PV Power",
            f"{peak_power:.0f} W"
        )

    with c3:
        st.metric(
            "Final Battery SOC",
            f"{final_soc:.1f}%"
        )

    with c4:
        st.metric(
            "Unmet Load",
            f"{unmet_energy:.2f} kWh"
        )


    # -----------------------------------------------------
    # PANEL CONFIGURATION
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Fixed Panel Configuration</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    for i, (col, tilt, energy) in enumerate(
        zip(cols, tilts, panel_energy),
        start=1
    ):
        with col:
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="metric-label">PANEL {i}</div>
                    <div class="metric-value">β = {tilt}°</div>
                    <p>
                    Daily energy<br>
                    <strong>{energy:.3f} kWh</strong>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )


    # -----------------------------------------------------
    # POWER GRAPH
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">PV Power Profile</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    for i in range(1, 5):

        fig.add_trace(
            go.Scatter(
                x=data["Hour"],
                y=data[f"Panel {i} Power"],
                mode="lines",
                name=f"Panel {i} — {tilts[i-1]}°",
                line=dict(width=2)
            )
        )

    fig.add_trace(
        go.Scatter(
            x=data["Hour"],
            y=data["Total PV Power"],
            mode="lines",
            name="Total PV Power",
            line=dict(width=4, dash="dash")
        )
    )

    fig.update_layout(
        height=480,
        xaxis_title="Time of Day (hours)",
        yaxis_title="Power (W)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -----------------------------------------------------
    # BATTERY GRAPH
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Battery Behaviour</div>',
        unsafe_allow_html=True
    )

    fig_battery = go.Figure()

    fig_battery.add_trace(
        go.Scatter(
            x=data["Hour"],
            y=data["Battery SOC"],
            mode="lines",
            name="Battery SOC",
            fill="tozeroy",
            line=dict(width=3)
        )
    )

    fig_battery.update_layout(
        height=400,
        xaxis_title="Time of Day (hours)",
        yaxis_title="State of Charge (%)",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_battery,
        use_container_width=True
    )


    # -----------------------------------------------------
    # TOTAL POWER
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Energy Distribution</div>',
        unsafe_allow_html=True
    )

    energy_df = pd.DataFrame({
        "Panel": [
            f"Panel 1 ({tilt1}°)",
            f"Panel 2 ({tilt2}°)",
            f"Panel 3 ({tilt3}°)",
            f"Panel 4 ({tilt4}°)"
        ],
        "Energy (kWh)": panel_energy
    })

    fig_energy = go.Figure(
        data=[
            go.Bar(
                x=energy_df["Panel"],
                y=energy_df["Energy (kWh)"],
                text=[
                    f"{x:.3f} kWh"
                    for x in panel_energy
                ],
                textposition="outside"
            )
        ]
    )

    fig_energy.update_layout(
        height=400,
        yaxis_title="Energy (kWh)",
        xaxis_title="PV Module",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_energy,
        use_container_width=True
    )


    # -----------------------------------------------------
    # DATA TABLE
    # -----------------------------------------------------

    with st.expander("📊 View Simulation Data"):

        display_columns = [
            "Hour",
            "Solar Altitude",
            "GHI",
            "Panel 1 Power",
            "Panel 2 Power",
            "Panel 3 Power",
            "Panel 4 Power",
            "Total PV Power",
            "Battery SOC"
        ]

        st.dataframe(
            data[display_columns].round(3),
            use_container_width=True,
            height=400
        )

        csv = data.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download Simulation CSV",
            csv,
            "multi_tilt_simulation_results.csv",
            "text/csv",
            use_container_width=True
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Multi-Tilt Solar Intelligence · Theoretical Simulation Platform<br>
        Designed for research, comparison and prototype validation.
    </div>
    """,
    unsafe_allow_html=True
)
