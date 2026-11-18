import streamlit as st
import pandas as pd
import numpy as np
import psychrolib

# Initialize Psychrolib (SI default)
psychrolib.SetUnitSystem(psychrolib.SI)

st.set_page_config(
    page_title="DewPoint | Psychrometric Engine",
    page_icon="🍂",
    layout="wide",
)

# --- AUTUMN GEOMETRIC CSS STYLING ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF8F0;
        color: #2D1505;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #C2410C 0%, #B45309 100%);
        color: #FFF8F0;
        padding: 2rem;
        border: 3px solid #78350F;
        box-shadow: 6px 6px 0px #78350F;
        margin-bottom: 2rem;
        border-radius: 0px;
    }
    .metric-card {
        background-color: #FFEDD5;
        border: 2px solid #9A3412;
        padding: 1.2rem;
        box-shadow: 4px 4px 0px #9A3412;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #C2410C;
        color: white;
        border: 2px solid #78350F;
        box-shadow: 3px 3px 0px #78350F;
        border-radius: 0px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #9A3412;
        color: #FFF8F0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- HEADER ---
st.markdown(
    """
    <div class="main-header">
        <h1 style="margin:0; font-size: 2.5rem;">🍂 DewPoint</h1>
        <p style="margin:5px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Advanced Psychrometric Property Solver & Lookup Engine</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR CONFIGURATION ---
st.sidebar.markdown(
    "### ⚙️ Engine Settings & Units"
)
unit_system = st.sidebar.selectbox(
    "Unit System", ["SI (°C, kPa, kg/kg)", "IP (°F, psi, lb/lb)"]
)

if "SI" in unit_system:
    psychrolib.SetUnitSystem(psychrolib.SI)
    temp_unit = "°C"
    pres_unit = "kPa"
    hum_unit = "kg_w / kg_da"
    enthalpy_unit = "kJ / kg_da"
    vol_unit = "m³ / kg_da"
else:
    psychrolib.SetUnitSystem(psychrolib.IP)
    temp_unit = "°F"
    pres_unit = "psi"
    hum_unit = "lb_w / lb_da"
    enthalpy_unit = "BTU / lb_da"
    vol_unit = "ft³ / lb_da"

st.sidebar.markdown("---")
atmos_pres = st.sidebar.number_input(
    f"Atmospheric Pressure ({pres_unit})",
    value=101.325 if "SI" in unit_system else 14.696,
    step=1.0,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size:0.85rem; color:#78350F;'>Designed for Thermodynamic & HVAC Analysis.</p>",
    unsafe_allow_html=True,
)

# --- MAIN INTERACTION TABS ---
tab1, tab2, tab3 = st.tabs(
    [
        "📊 State Point Calculator",
        "📈 Lookup Table Generator",
        "ℹ️ About Psychrometrics",
    ]
)

with tab1:
  st.markdown("### Input Known Parameters")
  input_mode = st.radio(
      "Select Known Pair:",
      [
          "Dry-Bulb & Relative Humidity",
          "Dry-Bulb & Wet-Bulb",
          "Dry-Bulb & Dew-Point",
      ],
      horizontal=True,
  )

  col1, col2 = st.columns(2)

  with col1:
    tdb = st.number_input(
        f"Dry-Bulb Temperature ($T_{{db}}$) [{temp_unit}]",
        value=25.0 if "SI" in unit_system else 77.0,
        step=0.5,
    )

  with col2:
    if input_mode == "Dry-Bulb & Relative Humidity":
      rh_input = st.slider("Relative Humidity (RH)", 0.0, 100.0, 50.0, 1.0)
      rh_frac = rh_input / 100.0
    elif input_mode == "Dry-Bulb & Wet-Bulb":
      twb = st.number_input(
          f"Wet-Bulb Temperature ($T_{{wb}}$) [{temp_unit}]",
          value=20.0 if "SI" in unit_system else 68.0,
          step=0.5,
      )
    else:
      tdp_input = st.number_input(
          f"Dew-Point Temperature ($T_{{dp}}$) [{temp_unit}]",
          value=15.0 if "SI" in unit_system else 59.0,
          step=0.5,
      )

  if st.button("Calculate Properties"):
    try:
      # Perform calculations based on mode
      if input_mode == "Dry-Bulb & Relative Humidity":
        twb = psychrolib.GetTWetBulbFromRelHum(tdb, rh_frac, atmos_pres)
        tdp = psychrolib.GetTDewPointFromRelHum(tdb, rh_frac)
        hum_ratio = psychrolib.GetHumRatioFromRelHum(tdb, rh_frac, atmos_pres)
        enthalpy = psychrolib.GetMoistAirEnthalpy(tdb, hum_ratio)
        density = psychrolib.GetMoistAirDensity(tdb, hum_ratio, atmos_pres)
        v_vol = 1.0 / density if density > 0 else 0
        vapor_p = psychrolib.GetVaporPressureFromRelHum(tdb, rh_frac)

      elif input_mode == "Dry-Bulb & Wet-Bulb":
        rh_frac = psychrolib.GetRelHumFromTWetBulb(tdb, twb, atmos_pres)
        tdp = psychrolib.GetTDewPointFromTWetBulb(tdb, twb, atmos_pres)
        hum_ratio = psychrolib.GetHumRatioFromTWetBulb(tdb, twb, atmos_pres)
        enthalpy = psychrolib.GetMoistAirEnthalpy(tdb, hum_ratio)
        density = psychrolib.GetMoistAirDensity(tdb, hum_ratio, atmos_pres)
        v_vol = 1.0 / density if density > 0 else 0
        vapor_p = psychrolib.GetVaporPressureFromHumRatio(hum_ratio, atmos_pres)

      else:
        rh_frac = psychrolib.GetRelHumFromTDewPoint(tdb, tdp_input)
        twb = psychrolib.GetTWetBulbFromRelHum(tdb, rh_frac, atmos_pres)
        tdp = tdp_input
        hum_ratio = psychrolib.GetHumRatioFromTDewPoint(tdp)
        enthalpy = psychrolib.GetMoistAirEnthalpy(tdb, hum_ratio)
        density = psychrolib.GetMoistAirDensity(tdb, hum_ratio, atmos_pres)
        v_vol = 1.0 / density if density > 0 else 0
        vapor_p = psychrolib.GetVaporPressureFromHumRatio(hum_ratio, atmos_pres)

      st.markdown("### 📋 Computed Psychrometric State")
      r1, r2, r3, r4 = st.columns(4)

      with r1:
        st.markdown(
            f"""<div class="metric-card">
                <b>Relative Humidity</b><br>
                <span style="font-size: 1.5rem; color:#9A3412;">{rh_frac * 100:.2f}</span> %
            </div>""",
            unsafe_allow_html=True,
        )
      with r2:
        st.markdown(
            f"""<div class="metric-card">
                <b>Wet-Bulb Temp ($T_{{wb}}$)</b><br>
                <span style="font-size: 1.5rem; color:#9A3412;">{twb:.2f}</span> {temp_unit}
            </div>""",
            unsafe_allow_html=True,
        )
      with r3:
        st.markdown(
            f"""<div class="metric-card">
                <b>Dew-Point ($T_{{dp}}$)</b><br>
                <span style="font-size: 1.5rem; color:#9A3412;">{tdp:.2f}</span> {temp_unit}
            </div>""",
            unsafe_allow_html=True,
        )
      with r4:
        st.markdown(
            f"""<div class="metric-card">
                <b>Humidity Ratio ($W$)</b><br>
                <span style="font-size: 1.2rem; color:#9A3412;">{hum_ratio:.5f}</span> {hum_unit}
            </div>""",
            unsafe_allow_html=True,
        )

      r5, r6, r7 = st.columns(3)
      with r5:
        st.markdown(
            f"""<div class="metric-card">
                <b>Specific Enthalpy ($h$)</b><br>
                <span style="font-size: 1.4rem; color:#9A3412;">{enthalpy:.2f}</span> {enthalpy_unit}
            </div>""",
            unsafe_allow_html=True,
        )
      with r6:
        st.markdown(
            f"""<div class="metric-card">
                <b>Specific Volume ($v$)</b><br>
                <span style="font-size: 1.4rem; color:#9A3412;">{v_vol:.4f}</span> {vol_unit}
            </div>""",
            unsafe_allow_html=True,
        )
      with r7:
        st.markdown(
            f"""<div class="metric-card">
                <b>Vapor Pressure ($p_v$)</b><br>
                <span style="font-size: 1.4rem; color:#9A3412;">{vapor_p:.2f}</span> {pres_unit}
            </div>""",
            unsafe_allow_html=True,
        )

    except Exception as e:
      st.error(
          f"Calculation error: {e}. Check if the input state is physically"
          " possible."
      )

with tab2:
  st.markdown("### 📈 Range Lookup Table Generator")
  st.markdown(
      "Generate a customized psychrometric table across a temperature range"
      " for a fixed Relative Humidity."
  )

  col_t1, col_t2, col_rh = st.columns(3)
  with col_t1:
    t_min = st.number_input(
        "Min Temp", value=10.0 if "SI" in unit_system else 50.0
    )
  with col_t2:
    t_max = st.number_input(
        "Max Temp", value=40.0 if "SI" in unit_system else 104.0
    )
  with col_rh:
    table_rh = st.slider("Fixed Relative Humidity (%)", 10.0, 100.0, 50.0, 5.0)

  if st.button("Generate Table"):
    temps = np.linspace(t_min, t_max, 10)
    data = []
    for t in temps:
      try:
        rh_f = table_rh / 100.0
        tw = psychrolib.GetTWetBulbFromRelHum(t, rh_f, atmos_pres)
        tdp = psychrolib.GetTDewPointFromRelHum(t, rh_f)
        w = psychrolib.GetHumRatioFromRelHum(t, rh_f, atmos_pres)
        h = psychrolib.GetMoistAirEnthalpy(t, w)
        data.append(
            {
                f"Dry-Bulb ({temp_unit})": round(t, 2),
                "RH (%)": table_rh,
                f"Wet-Bulb ({temp_unit})": round(tw, 2),
                f"Dew-Point ({temp_unit})": round(tdp, 2),
                f"Hum. Ratio ({hum_unit})": round(w, 5),
                f"Enthalpy ({enthalpy_unit})": round(h, 2),
            }
        )
      except:
        continue
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

with tab3:
  st.markdown("### ℹ️ About DewPoint & Psychrometrics")
  st.markdown(
      """
    **DewPoint** is built using rigorous thermodynamic relations established by **Psychrolib** and ASHRAE algorithms. 
    It computes air-water vapor mixture properties essential for chemical engineering, HVAC design, drying operations, and environmental conditioning.
    
    * **Dry-Bulb Temperature ($T_{db}$):** The true thermodynamic temperature of moist air.
    * **Wet-Bulb Temperature ($T_{wb}$):** Temperature measured by a thermometer covered in a water-saturated wick exposed to airflow.
    * **Dew-Point Temperature ($T_{dp}$):** The temperature to which air must be cooled to become saturated with water vapor.
    * **Humidity Ratio ($W$):** Mass of water vapor per unit mass of dry air.
    """,
      unsafe_allow_html=True,
  )
