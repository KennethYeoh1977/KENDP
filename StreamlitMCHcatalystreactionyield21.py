import streamlit as st
import matplotlib.pyplot as plt
import math

# Function to calculate temperature factor using the Arrhenius equation
def temperature_factor(T):
    """Arrhenius equation for temperature sensitivity."""
    A = 1e5  # Arbitrary pre-exponential factor
    Ea = 60700  # Activation energy in J/mol catalyst is Pt/TiO2 (citation)
    R = 8.314  # Gas constant in J/(mol·K)
    T_k = T + 273.15  # Convert °C to Kelvin
    return A * math.exp(-Ea / (R * T_k))

# Function to calculate pressure factor based on equilibrium constant
def pressure_factor(P):
    """Pressure sensitivity based on equilibrium constant."""
    P_standard = 1  # Standard pressure in bar
    return P_standard / P if P > 0 else 1  # Favor lower pressures

# Streamlit App Title
st.title("MCH to Hydrogen Yield Simulation")

# User Inputs
target_h2_yield = st.number_input("Enter the target cumulative yield of H2 in kg", value=5000)  # Target cumulative yield of H2 in kg
mch_flow_rate = st.number_input("Enter the increment of MCH added each hour in kg", value=1000)  # Increment of MCH added each hour in kg
temperature = st.number_input("Enter the temperature in °C for Pt based catalyst ie. Pt/Al2O3, Pt/TiO2 ", value=300)  # Set temperature in °C for each reaction step
pressure = st.number_input("Enter the pressure, barg (assumed constant)", value=1)  # Assume constant pressure for simplicity
max_yield_ratio = 0.0616  # Max H2 yield per kg of MCH (theoretical)

# Selectivity, Conversion Rates, and Recycling Rate
selectivity = st.number_input("Enter the selectivity rate (0-1)", value=0.99)  # Selectivity rate (99%)
conversion_rate = st.number_input("Enter the conversion rate (0-1)", value=0.85)  # Conversion rate (85%)
recycling_rate = st.number_input("Enter the recycling rate (0-1)", value=0.8)  # Recycling rate (80%)

# Yield factors and constants for cumulative yield function
a = max_yield_ratio * selectivity * conversion_rate  # Yield factor
b = 0.0  # Constant for initial yield or inefficiencies

# Initialize variables
cumulative_h2_yield = 0  # Cumulative yield of H2
total_mch_used = 0  # Total MCH used in kg
remaining_mch = mch_flow_rate * (1 - recycling_rate)  # Initial remaining MCH after recycling
iterations = 0  # Count of iterations

# Lists for storing iteration data
mch_usage = []
h2_yields = []
remaining_mch_list = []
efficiency_list = []

# Define the hydrogen yield function with temperature and pressure effects
def simulate_yield(mch_used, T, P):
    temp_effect = temperature_factor(T)
    pressure_effect = pressure_factor(P)
    yield_with_factors = a * mch_used * temp_effect * pressure_effect + b
    return yield_with_factors

# Iterative loop to reach target cumulative H2 yield
while cumulative_h2_yield < target_h2_yield:
    iterations += 1
    
    # Calculate current total MCH used
    total_mch_used += mch_flow_rate
    
    # Calculate hydrogen yield based on the defined relationship
    h2_yield_current = simulate_yield(total_mch_used, temperature, pressure)
    
    # Update cumulative hydrogen yield considering conversion and selectivity
    effective_conversion_rate = selectivity * conversion_rate
    h2_yield_current *= effective_conversion_rate
    
    # Update cumulative values and remaining MCH after recycling
    cumulative_h2_yield += h2_yield_current
    
    remaining_mch += mch_flow_rate * (1 - recycling_rate)
    
    # Calculate efficiency for this iteration
    efficiency_current = h2_yield_current / mch_flow_rate if mch_flow_rate > 0 else 0
    
    # Append data for plotting and tracking
    mch_usage.append(total_mch_used)
    h2_yields.append(cumulative_h2_yield)
    remaining_mch_list.append(remaining_mch)
    efficiency_list.append(efficiency_current)

# Plotting results using Matplotlib and displaying them in Streamlit using `st.pyplot`
plt.figure(figsize=(12, 8))

# Cumulative H₂ Yield Plot
plt.subplot(3, 1, 1)
plt.plot(mch_usage, h2_yields, marker="o", color="blue", label="Cumulative H₂ Yield")
plt.axhline(y=target_h2_yield, color="red", linestyle="--", label="Target H₂ Yield")
plt.xlabel("Total MCH Used (kg)")
plt.ylabel("Cumulative H₂ Yield (kg)")
plt.title("Cumulative Hydrogen Yield vs. Total MCH Usage")
plt.legend()
plt.grid(True)

# Remaining MCH Plot
plt.subplot(3, 1, 2)
plt.plot(mch_usage, remaining_mch_list, marker="o", color="green", label="Remaining MCH")
plt.xlabel("Total MCH Used (kg)")
plt.ylabel("Remaining MCH (kg)")
plt.title("Remaining MCH vs. Total MCH Usage")
plt.legend()
plt.grid(True)

# Efficiency Plot
plt.subplot(3, 1, 3)
plt.plot(mch_usage, efficiency_list, marker="o", color="orange", label="Yield Efficiency")
plt.xlabel("Total MCH Used (kg)")
plt.ylabel("Yield Efficiency (kg H₂/kg MCH)")
plt.title("Yield Efficiency vs. Total MCH Usage")
plt.legend()
plt.grid(True)

plt.tight_layout()

# Display the plots in Streamlit using Matplotlib's `pyplot` interface.
st.pyplot(plt)
