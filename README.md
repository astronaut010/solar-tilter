# ☀️ Multi-Tilt Solar Intelligence

A simulation platform for studying a photovoltaic system consisting of multiple permanently fixed solar panels installed at different tilt angles and connected to a shared battery-storage system.

## Concept

Conventional fixed PV systems generally use the same tilt angle for all modules.

This project investigates an alternative architecture:

Four permanently fixed PV panels are installed at different tilt angles. Because the apparent position of the Sun changes throughout the day, each panel experiences a different irradiance profile.

The generated power is combined and supplied to a shared battery/load system.

## System Architecture

Solar Position
↓
Effective Irradiance
↓
Four Fixed-Tilt PV Modules
↓
Power Generation
↓
Combined PV Output
↓
Battery Model
↓
Load

## Simulation Parameters

The simulator allows the user to configure:

- Location
- Day of year
- Panel rating
- Panel temperature
- Panel azimuth
- Four individual tilt angles
- Battery capacity
- Initial battery SOC
- Load power

## Results

The dashboard provides:

- Individual panel power
- Total PV power
- Daily energy
- Peak power
- Battery state of charge
- Energy distribution
- Unmet load
- Downloadable simulation data

## Research Objective

The initial research question is:

> Can multiple permanently fixed PV panels at different tilt angles provide a more useful energy-generation profile for shared battery storage compared with a conventional same-tilt PV configuration?

## Current Status

This version is a theoretical simulation model.

It uses simplified solar-geometry, irradiance and PV-power equations for initial validation.

Future versions can incorporate:

- Measured solar irradiance
- Real weather datasets
- Detailed PV electrical models
- MPPT models
- Converter losses
- Battery degradation
- Shading analysis
- Economic analysis
- Optimization algorithms
- Experimental hardware validation

## Disclaimer

Simulation results are model-dependent and should not be interpreted as experimental measurements until validated using physical hardware or validated datasets.
