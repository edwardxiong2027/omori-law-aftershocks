#!/usr/bin/env python3
"""
USGS Earthquake Data Collection Script
Author: Edward Xiong
Diamond Bar High School, 11th Grade
NHSJS Research Project: Mathematics of Earthquake Aftershocks - Testing Omori's Law

This script collects earthquake data from USGS API to analyze aftershock sequences
and test Omori's Law: n(t) = K / (c + t)^p
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import csv

# USGS API Configuration
BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
RATE_LIMIT_DELAY = 0.5  # Be nice to the API

# Parameters for mainshock selection
MIN_MAINSHOCK_MAGNITUDE = 6.0  # Focus on significant earthquakes
AFTERSHOCK_RADIUS_KM = 100  # Search radius for aftershocks
AFTERSHOCK_DAYS = 30  # Days to track aftershocks


def fetch_earthquakes(
    starttime: str,
    endtime: str,
    minmagnitude: float = None,
    maxmagnitude: float = None,
    latitude: float = None,
    longitude: float = None,
    maxradiuskm: float = None,
    limit: int = 20000
) -> List[Dict]:
    """Fetch earthquakes from USGS API."""
    params = {
        "format": "geojson",
        "starttime": starttime,
        "endtime": endtime,
        "limit": limit,
        "orderby": "time-asc"
    }

    if minmagnitude:
        params["minmagnitude"] = minmagnitude
    if maxmagnitude:
        params["maxmagnitude"] = maxmagnitude
    if latitude and longitude and maxradiuskm:
        params["latitude"] = latitude
        params["longitude"] = longitude
        params["maxradiuskm"] = maxradiuskm

    time.sleep(RATE_LIMIT_DELAY)

    try:
        print(f"  Fetching: {starttime} to {endtime}...", flush=True)
        response = requests.get(BASE_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        features = data.get("features", [])
        print(f"    Found {len(features)} earthquakes", flush=True)
        return features
    except Exception as e:
        print(f"  API Error: {e}", flush=True)
        return []


def parse_earthquake(feature: Dict) -> Dict:
    """Parse earthquake feature into clean dictionary."""
    props = feature.get("properties", {})
    coords = feature.get("geometry", {}).get("coordinates", [0, 0, 0])

    # Convert millisecond timestamp to datetime
    time_ms = props.get("time", 0)
    eq_time = datetime.utcfromtimestamp(time_ms / 1000)

    return {
        "id": feature.get("id", ""),
        "time": eq_time.isoformat(),
        "timestamp": time_ms,
        "magnitude": props.get("mag"),
        "mag_type": props.get("magType", ""),
        "longitude": coords[0],
        "latitude": coords[1],
        "depth_km": coords[2],
        "place": props.get("place", ""),
        "type": props.get("type", "earthquake")
    }


def get_major_earthquakes(start_year: int, end_year: int, min_mag: float = 6.0) -> List[Dict]:
    """Get all major earthquakes in a date range."""
    all_quakes = []

    for year in range(start_year, end_year + 1):
        starttime = f"{year}-01-01"
        endtime = f"{year}-12-31"

        features = fetch_earthquakes(
            starttime=starttime,
            endtime=endtime,
            minmagnitude=min_mag
        )

        for feature in features:
            eq = parse_earthquake(feature)
            if eq["magnitude"] and eq["magnitude"] >= min_mag:
                all_quakes.append(eq)

    return all_quakes


def get_aftershock_sequence(
    mainshock: Dict,
    days: int = 30,
    radius_km: float = 100,
    min_aftershock_mag: float = 2.0
) -> List[Dict]:
    """Get aftershocks following a mainshock."""
    main_time = datetime.fromisoformat(mainshock["time"])
    starttime = (main_time + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")
    endtime = (main_time + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")

    features = fetch_earthquakes(
        starttime=starttime,
        endtime=endtime,
        minmagnitude=min_aftershock_mag,
        latitude=mainshock["latitude"],
        longitude=mainshock["longitude"],
        maxradiuskm=radius_km
    )

    aftershocks = []
    for feature in features:
        eq = parse_earthquake(feature)
        if eq["magnitude"] and eq["magnitude"] < mainshock["magnitude"]:
            # Calculate time since mainshock (in days)
            eq_time = datetime.fromisoformat(eq["time"])
            delta = eq_time - main_time
            eq["days_after_mainshock"] = delta.total_seconds() / 86400
            eq["hours_after_mainshock"] = delta.total_seconds() / 3600
            aftershocks.append(eq)

    return aftershocks


def bin_aftershocks_by_time(aftershocks: List[Dict], bin_hours: float = 1.0) -> List[Dict]:
    """Bin aftershocks by time intervals to calculate rate n(t)."""
    if not aftershocks:
        return []

    max_hours = max(a["hours_after_mainshock"] for a in aftershocks)
    bins = []

    t = 0
    while t < max_hours:
        count = sum(
            1 for a in aftershocks
            if t <= a["hours_after_mainshock"] < t + bin_hours
        )
        rate = count / bin_hours  # Aftershocks per hour

        bins.append({
            "time_start_hours": t,
            "time_end_hours": t + bin_hours,
            "time_midpoint_hours": t + bin_hours / 2,
            "count": count,
            "rate_per_hour": rate
        })
        t += bin_hours

    return bins


def collect_aftershock_sequences(
    mainshocks: List[Dict],
    max_sequences: int = 50
) -> List[Dict]:
    """Collect aftershock sequences for multiple mainshocks."""
    sequences = []

    for i, mainshock in enumerate(mainshocks[:max_sequences]):
        print(f"\n[{i+1}/{min(len(mainshocks), max_sequences)}] Mainshock: M{mainshock['magnitude']:.1f} - {mainshock['place']}", flush=True)
        print(f"    Time: {mainshock['time']}", flush=True)

        aftershocks = get_aftershock_sequence(
            mainshock,
            days=AFTERSHOCK_DAYS,
            radius_km=AFTERSHOCK_RADIUS_KM
        )

        if len(aftershocks) < 10:
            print(f"    Skipping (only {len(aftershocks)} aftershocks)", flush=True)
            continue

        # Bin aftershocks
        binned = bin_aftershocks_by_time(aftershocks, bin_hours=1.0)

        sequence = {
            "mainshock": mainshock,
            "aftershocks": aftershocks,
            "binned_rates": binned,
            "total_aftershocks": len(aftershocks),
            "duration_hours": max(a["hours_after_mainshock"] for a in aftershocks)
        }

        sequences.append(sequence)
        print(f"    Collected {len(aftershocks)} aftershocks over {sequence['duration_hours']:.1f} hours", flush=True)

    return sequences


def save_data(data: Dict, filename: str):
    """Save data to JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nData saved to: {filepath}", flush=True)


def save_summary_csv(sequences: List[Dict], filename: str):
    """Save summary data to CSV."""
    filepath = os.path.join(os.path.dirname(__file__), filename)

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'mainshock_id', 'mainshock_mag', 'mainshock_depth_km',
            'mainshock_lat', 'mainshock_lon', 'mainshock_time',
            'mainshock_place', 'total_aftershocks', 'duration_hours'
        ])

        for seq in sequences:
            ms = seq["mainshock"]
            writer.writerow([
                ms["id"], ms["magnitude"], ms["depth_km"],
                ms["latitude"], ms["longitude"], ms["time"],
                ms["place"], seq["total_aftershocks"], seq["duration_hours"]
            ])

    print(f"Summary CSV saved to: {filepath}", flush=True)


def main():
    """Main data collection function."""
    print("=" * 60, flush=True)
    print("USGS EARTHQUAKE DATA COLLECTION", flush=True)
    print("NHSJS Research Project - Edward Xiong", flush=True)
    print("Testing Omori's Law on Aftershock Sequences", flush=True)
    print("=" * 60, flush=True)

    # Collect major earthquakes from recent years
    print("\n--- Fetching Major Earthquakes (M6.0+) ---", flush=True)
    mainshocks = get_major_earthquakes(
        start_year=2020,
        end_year=2025,
        min_mag=MIN_MAINSHOCK_MAGNITUDE
    )
    print(f"\nTotal major earthquakes found: {len(mainshocks)}", flush=True)

    # Collect aftershock sequences
    print("\n--- Collecting Aftershock Sequences ---", flush=True)
    sequences = collect_aftershock_sequences(mainshocks, max_sequences=40)

    # Save data
    output_data = {
        "collection_date": datetime.now().isoformat(),
        "parameters": {
            "min_mainshock_magnitude": MIN_MAINSHOCK_MAGNITUDE,
            "aftershock_radius_km": AFTERSHOCK_RADIUS_KM,
            "aftershock_days": AFTERSHOCK_DAYS
        },
        "sequences": sequences
    }

    save_data(output_data, "earthquake_data.json")
    save_summary_csv(sequences, "sequence_summary.csv")

    # Summary
    print("\n" + "=" * 60, flush=True)
    print("COLLECTION SUMMARY", flush=True)
    print("=" * 60, flush=True)
    print(f"Mainshocks analyzed: {len(sequences)}", flush=True)
    total_aftershocks = sum(s["total_aftershocks"] for s in sequences)
    print(f"Total aftershocks collected: {total_aftershocks}", flush=True)
    avg_aftershocks = total_aftershocks / len(sequences) if sequences else 0
    print(f"Average aftershocks per sequence: {avg_aftershocks:.1f}", flush=True)


if __name__ == "__main__":
    main()
