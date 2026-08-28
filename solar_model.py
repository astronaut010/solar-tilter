import numpy as np
import pandas as pd


def solar_position(day_of_year, latitude, longitude=0.0, timezone_offset=5.5):
    """
    Approximate solar position for simulation.

    Returns solar altitude and azimuth for each 5-minute timestep.
    Angles are in degrees.
    """

    minutes = np.arange(0, 24 * 60, 5)
    hour = minutes / 60.0

    # Solar declination approximation
    declination = 23.45 * np.sin(
        np.radians(360 * (284 + day_of_year) / 365)
    )

    # Approximate solar time correction
    b = np.radians(360 * (day_of_year - 81) / 364)

    equation_of_time = (
        9.87 * np.sin(2 * b)
        - 7.53 * np.cos(b)
        - 1.5 * np.sin(b)
    )

    longitude_correction = 4 * (longitude - 82.5)
    solar_time = hour + (equation_of_time + longitude_correction) / 60

    hour_angle = 15 * (solar_time - 12)

    lat = np.radians(latitude)
    dec = np.radians(declination)
    ha = np.radians(hour_angle)

    sin_altitude = (
        np.sin(lat) * np.sin(dec)
        + np.cos(lat) * np.cos(dec) * np.cos(ha)
    )

    altitude = np.degrees(np.arcsin(np.clip(sin_altitude, -1, 1)))

    # Solar azimuth measured clockwise from north
    azimuth = np.degrees(
        np.arctan2(
            np.sin(ha),
            np.cos(ha) * np.sin(lat) - np.tan(dec) * np.cos(lat)
        )
    ) + 180

    return minutes, altitude, azimuth


def clear_sky_irradiance(altitude):
    """
    Simplified clear-sky irradiance model.

    This is intentionally transparent for theoretical validation.
    """

    altitude_rad = np.radians(np.maximum(altitude, 0))

    irradiance = np.where(
        altitude > 0,
        1000 * np.sin(altitude_rad) ** 0.35,
        0
    )

    return np.clip(irradiance, 0, 1000)


def plane_of_array_irradiance(
    global_irradiance,
    solar_altitude,
    solar_azimuth,
    tilt,
    surface_azimuth=180
):
    """
    Approximate irradiance received by a fixed tilted surface.

    surface_azimuth:
        180° = south-facing
    """

    solar_alt = np.radians(solar_altitude)
    solar_az = np.radians(solar_azimuth)

    beta = np.radians(tilt)
    surface_az = np.radians(surface_azimuth)

    cos_incidence = (
        np.sin(solar_alt) * np.cos(beta)
        + np.cos(solar_alt)
        * np.sin(beta)
        * np.cos(solar_az - surface_az)
    )

    cos_incidence = np.maximum(cos_incidence, 0)

    # Approximate direct component
    direct_component = global_irradiance * cos_incidence

    # Simple diffuse component
    diffuse_component = (
        global_irradiance
        * 0.15
        * (1 + np.cos(beta)) / 2
    )

    poa = direct_component + diffuse_component

    return np.maximum(poa, 0)


def pv_power(
    irradiance,
    panel_rating_w,
    temperature=25,
    temperature_coefficient=-0.004
):
    """
    Simplified PV power model.

    panel_rating_w is the rated power at 1000 W/m² and 25°C.
    """

    temperature_factor = 1 + temperature_coefficient * (temperature - 25)

    power = (
        panel_rating_w
        * (irradiance / 1000)
        * temperature_factor
    )

    return np.maximum(power, 0)


def simulate_pv_system(
    latitude,
    longitude,
    day_of_year,
    tilts,
    panel_rating,
    temperature=30,
    surface_azimuth=180,
):
    """
    Simulates four fixed PV panels.
    """

    minutes, altitude, solar_azimuth = solar_position(
        day_of_year,
        latitude,
        longitude
    )

    ghi = clear_sky_irradiance(altitude)

    data = pd.DataFrame({
        "Time": pd.to_datetime(minutes, unit="m", origin="2026-01-01"),
        "Hour": minutes / 60,
        "Solar Altitude": altitude,
        "Solar Azimuth": solar_azimuth,
        "GHI": ghi
    })

    powers = []

    for i, tilt in enumerate(tilts, start=1):

        poa = plane_of_array_irradiance(
            ghi,
            altitude,
            solar_azimuth,
            tilt,
            surface_azimuth
        )

        power = pv_power(
            poa,
            panel_rating,
            temperature
        )

        data[f"Panel {i} Irradiance"] = poa
        data[f"Panel {i} Power"] = power

        powers.append(power)

    data["Total PV Power"] = np.sum(powers, axis=0)

    # Energy generated in each 5-minute interval
    data["Energy Wh"] = data["Total PV Power"] * (5 / 60)

    return data
