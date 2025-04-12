import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("Reaction Engineering Interactive Tool")

st.markdown("""
Select a problem type below to interact with batch, CSTR, and PFR reactor design problems from your course. This tool allows you to:
- Adjust system parameters interactively
- Visualize results
- Understand how conversion, flow rate, and reaction rates affect reactor performance
""")

problem_type = st.radio("Select a problem type:", [
    "Batch Reactor: Time to reach target conversion",
    "CSTR Volume Calculation",
    "Levenspiel Plot Analysis: CSTR + PFR in Series"
])

if problem_type == "Batch Reactor: Time to reach target conversion":
    st.subheader("Batch Reactor")
    st.markdown("""
    **Assumptions:**
    - First-order irreversible reaction: \( A \rightarrow B \)
    - Isothermal operation
    - Constant volume reactor
    - Well-mixed system
    - Negligible pressure drop
    """)
    st.latex(r"t = \frac{-\ln(1 - X)}{k}")
    k = st.number_input("Rate constant (1/min)", value=0.23, step=0.01)
    X_target = st.slider("Target conversion (X)", min_value=0.01, max_value=0.99, value=0.99)

    if X_target >= 1.0:
        st.warning("Conversion must be < 1.0")
    else:
        time_required = -np.log(1 - X_target) / k
        st.write(f"Time required: {time_required:.2f} minutes")

elif problem_type == "CSTR Volume Calculation":
    st.subheader("CSTR Volume Calculation")
    st.markdown("""
    **Assumptions:**
    - First-order irreversible reaction
    - Steady-state operation
    - Isothermal, constant flow rate
    - Ideal mixing (concentration inside = exit)
    """)
    st.latex(r"V = \frac{F_{A0} X}{k C_{A0}(1 - X)}")
    F_A0 = st.number_input("Entering molar flow rate F_A0 (mol/min)", value=5.0)
    X_cstr = st.slider("Conversion (CSTR)", min_value=0.01, max_value=0.99, value=0.99)
    v0_cstr = st.number_input("Inlet Volumetric Flow Rate (L/min)", value=10.0)
    k_cstr = st.number_input("Rate constant k (1/min)", value=0.006)

    if X_cstr >= 1.0:
        st.warning("Conversion must be < 1.0")
    else:
        C_A0 = F_A0 / v0_cstr  # mol/L
        V_cstr = (F_A0 * X_cstr) / (k_cstr * C_A0 * (1 - X_cstr))  # Corrected formula
        st.write(f"CSTR volume required: {V_cstr:.2f} L")

elif problem_type == "Levenspiel Plot Analysis: CSTR + PFR in Series":
    st.subheader("CSTR + PFR in Series")
    st.markdown("""
    **Assumptions:**
    - Rate data known as a function of conversion
    - Steady-state operation
    - CSTR: ideal mixing; PFR: plug flow with no axial dispersion
    - Isothermal and constant volumetric flow rate
    """)
    st.latex(r"V_{CSTR} = \frac{F_{A0} X}{-r_A}\quad V_{PFR} = F_{A0} \int_{X_{int}}^{X_{final}} \frac{1}{-r_A} dX")

    st.markdown("**Enter or edit rate data:**")
    default_text = "0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.85\n0.0053,0.0052,0.005,0.0045,0.004,0.0033,0.0025,0.0018,0.00125,0.001"
    rate_input = st.text_area("Paste comma-separated values for X and -rA (two lines)", value=default_text)

    try:
        rows = rate_input.strip().split('\n')
        X_vals = list(map(float, rows[0].split(',')))
        rA_vals = list(map(float, rows[1].split(',')))
        df = pd.DataFrame({"X": X_vals, "-rA": rA_vals})
    except Exception as e:
        st.error("Error parsing rate data. Check formatting.")
        df = pd.DataFrame({"X": [0.0], "-rA": [0.001]})

    FA0 = st.number_input("Molar flow rate for CSTR+PFR system (mol/min)", value=1.0)
    X_int = st.slider("Intermediate conversion (after first reactor)", 0.1, 0.7, 0.3, step=0.1)
    X_final = st.slider("Final conversion (after second reactor)", X_int + 0.1, 0.9, 0.8, step=0.05)

    r_interp = np.interp([X_int], df["X"], df["-rA"])[0]
    V_cstr = FA0 * X_int / r_interp

    X_array = np.array(df["X"])
    r_array = np.array(df["-rA"])
    mask = (X_array >= X_int) & (X_array <= X_final)
    X_sub = X_array[mask]
    r_sub = r_array[mask]
    if len(X_sub) > 1:
        V_pfr = FA0 * np.trapz(1 / r_sub, X_sub)
        st.write(f"CSTR volume (0 to {X_int:.2f}): {V_cstr:.2f} L")
        st.write(f"PFR volume ({X_int:.2f} to {X_final:.2f}): {V_pfr:.2f} L")
    else:
        st.warning("Check interpolation range and rate data.")

    fig, ax = plt.subplots()
    ax.plot(df["X"], 1 / df["-rA"], marker='o')
    ax.set_xlabel("Conversion X")
    ax.set_ylabel("1 / -rA (L/mol-min)")
    ax.set_title("Levenspiel Plot")
    st.pyplot(fig)
