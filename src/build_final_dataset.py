import pandas as pd

print("==============================================")
print("PathSetu - Final Dataset Integration")
print("==============================================")

# ==================================================
# 1. LOAD MAIN ROAD RISK DATA
# ==================================================

print()
print("Loading road risk data...")

risk = pd.read_csv(
    "data/road_risk_explained.csv"
)

latest_date = risk["date"].max()

risk_latest = risk[
    risk["date"] == latest_date
].copy()

print(
    f"Latest risk date: {latest_date}"
)

print(
    f"Road records: {len(risk_latest)}"
)

# ==================================================
# 2. LOAD VILLAGE ISOLATION
# ==================================================

print()
print("Loading village isolation data...")

isolation = pd.read_csv(
    "data/village_isolation.csv"
)

print(
    f"Village records: {len(isolation)}"
)

# ==================================================
# 3. LOAD SUPPLY PRIORITIES
# ==================================================

print()
print("Loading supply priority data...")

supply = pd.read_csv(
    "data/supply_priorities.csv"
)

print(
    f"Supply priority records: {len(supply)}"
)

# ==================================================
# 4. LOAD RISK-AWARE ROUTING
# ==================================================

print()
print("Loading risk-aware routing data...")

routes = pd.read_csv(
    "data/risk_aware_routes.csv"
)

print(
    f"Route records: {len(routes)}"
)

# ==================================================
# 5. LOAD DISASTER SIMULATION
# ==================================================

print()
print("Loading disaster simulation...")

simulation = pd.read_csv(
    "data/disaster_simulation.csv"
)

print(
    f"Simulation records: {len(simulation)}"
)

# ==================================================
# 6. LOAD FIELD REPORTS
# ==================================================

print()
print("Loading field reports...")

field_reports = pd.read_csv(
    "data/field_reports.csv"
)

print(
    f"Field reports: {len(field_reports)}"
)

# ==================================================
# 7. CREATE ROAD-LEVEL SUMMARY
# ==================================================

road_summary = risk_latest[
    [
        "road_u",
        "road_v",
        "road_key",
        "latitude",
        "longitude",
        "elevation_m",
        "slope_degrees",
        "distance_to_nearest_landslide_km",
        "landslides_within_1km",
        "landslides_within_5km",
        "rain_24h",
        "rain_72h",
        "rain_7days",
        "risk_score",
        "risk_level",
        "rainfall_contribution",
        "slope_contribution",
        "landslide_contribution",
        "risk_explanation"
    ]
].copy()

# ==================================================
# 8. ADD FIELD REPORT SUMMARY
# ==================================================

total_reports = len(
    field_reports
)

high_confidence_reports = len(
    field_reports[
        field_reports["report_status"]
        == "HIGH CONFIDENCE"
    ]
)

medium_confidence_reports = len(
    field_reports[
        field_reports["report_status"]
        == "MEDIUM CONFIDENCE"
    ]
)

print()
print("Field report summary:")

print(
    f"Total reports: "
    f"{total_reports}"
)

print(
    f"High-confidence reports: "
    f"{high_confidence_reports}"
)

print(
    f"Medium-confidence reports: "
    f"{medium_confidence_reports}"
)

# ==================================================
# 9. CREATE DATASET SUMMARY TABLE
# ==================================================

summary_data = {
    "dataset": [
        "Road Risk",
        "Village Isolation",
        "Risk-Aware Routes",
        "Supply Priorities",
        "Disaster Simulation",
        "Field Reports"
    ],

    "records": [
        len(risk_latest),
        len(isolation),
        len(routes),
        len(supply),
        len(simulation),
        len(field_reports)
    ]
}

summary = pd.DataFrame(
    summary_data
)

# ==================================================
# 10. ADD GLOBAL FIELD REPORT METRICS
# ==================================================

road_summary[
    "field_reports_total"
] = total_reports

road_summary[
    "field_reports_high_confidence"
] = high_confidence_reports

road_summary[
    "field_reports_medium_confidence"
] = medium_confidence_reports

# ==================================================
# 11. SAVE ROAD-LEVEL FINAL DATASET
# ==================================================

road_output_file = (
    "data/pathsetu_final_road_dataset.csv"
)

road_summary.to_csv(
    road_output_file,
    index=False
)

# ==================================================
# 12. CREATE VILLAGE INTEGRATED DATASET
# ==================================================

print()
print("Building village integrated dataset...")

village_final = isolation.merge(
    supply[
        [
            "village",
            "priority_score",
            "priority_level",
            "recommended_supplies"
        ]
    ],
    on="village",
    how="left"
)

# ==================================================
# 13. ADD ROUTING INFORMATION
# ==================================================

route_columns = [
    "village",
    "normal_distance_km",
    "safe_route_distance_km",
    "extra_distance_percent",
    "normal_average_risk",
    "safe_route_average_risk",
    "normal_max_risk",
    "safe_route_max_risk"
]

available_route_columns = [
    column
    for column in route_columns
    if column in routes.columns
]

village_final = village_final.merge(
    routes[available_route_columns],
    on="village",
    how="left"
)

# ==================================================
# 14. ADD DISASTER IMPACT
# ==================================================

simulation_columns = [
    "village",
    "distance_increase_percent",
    "impact_level"
]

available_simulation_columns = [
    column
    for column in simulation_columns
    if column in simulation.columns
]

village_final = village_final.merge(
    simulation[available_simulation_columns],
    on="village",
    how="left"
)

# ==================================================
# 15. ADD FIELD REPORT COUNT BY LOCATION
# ==================================================

report_counts = (
    field_reports
    .groupby("location")
    .size()
    .reset_index(
        name="field_report_count"
    )
)

report_counts = report_counts.rename(
    columns={
        "location": "village"
    }
)

village_final = village_final.merge(
    report_counts,
    on="village",
    how="left"
)

village_final[
    "field_report_count"
] = village_final[
    "field_report_count"
].fillna(0)

# ==================================================
# 16. SAVE VILLAGE FINAL DATASET
# ==================================================

village_output_file = (
    "data/pathsetu_final_village_dataset.csv"
)

village_final.to_csv(
    village_output_file,
    index=False
)

# ==================================================
# 17. DISPLAY DATASET SUMMARY
# ==================================================

print()
print("==============================================")
print("FINAL DATASET SUMMARY")
print("==============================================")

print()

print(
    summary.to_string(
        index=False
    )
)

# ==================================================
# 18. VILLAGE SUMMARY
# ==================================================

print()
print("==============================================")
print("VILLAGE INTEGRATED SUMMARY")
print("==============================================")

print()

display_columns = [
    "village",
    "isolation_score",
    "isolation_level",
    "priority_score",
    "priority_level",
    "impact_level",
    "field_report_count"
]

available_display_columns = [
    column
    for column in display_columns
    if column in village_final.columns
]

print(
    village_final[
        available_display_columns
    ].to_string(index=False)
)

# ==================================================
# 19. OUTPUT INFORMATION
# ==================================================

print()
print("==============================================")
print("FILES CREATED")
print("==============================================")

print(
    f"Road dataset:"
)

print(
    road_output_file
)

print()

print(
    f"Village dataset:"
)

print(
    village_output_file
)

print()
print("==============================================")
print("FINAL DATASET INTEGRATION COMPLETE")
print("==============================================")