import numpy as np


def simulate_battery(
    pv_power,
    load_power,
    battery_capacity_kwh=2.0,
    initial_soc=30.0,
    charge_efficiency=0.95,
    discharge_efficiency=0.95,
    max_charge_power=5000,
    max_discharge_power=5000,
    timestep_minutes=5,
):
    """
    Simple battery energy-flow model.

    SOC is maintained between 0% and 100%.
    """

    battery_energy_wh = (
        battery_capacity_kwh * 1000 * initial_soc / 100
    )

    max_energy_wh = battery_capacity_kwh * 1000

    soc_values = []
    battery_power_values = []
    energy_to_load_values = []
    curtailed_values = []
    unmet_load_values = []

    dt_hours = timestep_minutes / 60

    for pv, load in zip(pv_power, load_power):

        pv_energy = pv * dt_hours
        load_energy = load * dt_hours

        if pv_energy >= load_energy:

            surplus = pv_energy - load_energy

            charge_energy = min(
                surplus,
                max_charge_power * dt_hours,
                (max_energy_wh - battery_energy_wh)
                / charge_efficiency
            )

            battery_energy_wh += charge_energy * charge_efficiency

            curtailed = max(surplus - charge_energy, 0)

            energy_to_load = load_energy
            unmet = 0

            battery_power = charge_energy / dt_hours

        else:

            deficit = load_energy - pv_energy

            available_from_battery = min(
                battery_energy_wh,
                max_discharge_power * dt_hours
                * discharge_efficiency
            )

            battery_used = min(
                deficit / discharge_efficiency,
                available_from_battery
            )

            battery_energy_wh -= battery_used

            delivered = battery_used * discharge_efficiency

            energy_to_load = pv_energy + delivered

            unmet = max(load_energy - energy_to_load, 0)

            curtailed = 0

            battery_power = -battery_used / dt_hours

        soc = (
            battery_energy_wh / max_energy_wh
        ) * 100

        soc_values.append(np.clip(soc, 0, 100))
        battery_power_values.append(battery_power)
        energy_to_load_values.append(energy_to_load)
        curtailed_values.append(curtailed)
        unmet_load_values.append(unmet)

    return {
        "SOC": np.array(soc_values),
        "Battery Power": np.array(battery_power_values),
        "Energy To Load": np.array(energy_to_load_values),
        "Curtailed Energy": np.array(curtailed_values),
        "Unmet Load": np.array(unmet_load_values),
    }
