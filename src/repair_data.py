import json

OUTPUT_FILE = "data/zone_dictionary.json"

# These are the actual numeric codes in your map
valid_zones = ["2", "1", "0", "4", "201", "202", "101", "6", "5"]

repair_data = {}

for zone in valid_zones:
    repair_data[zone] = f"""
    ### 🚧 Placeholder Data for Zone {zone}
    *(Real AI summary unavailable due to API Quota Limit)*
    
    **1. Permitted Uses:**
    * Detached house
    * Semi-detached house
    * Laneway Suite
    
    **2. Physical Rules:**
    * Max Height: 10.0m
    * Coverage: 35%
    
    **3. Prohibitions:**
    * Commercial usage
    * Industrial manufacturing
    """

print(f"🔧 Repairing {OUTPUT_FILE} with placeholders...")

with open(OUTPUT_FILE, "w") as f:
    json.dump(repair_data, f, indent=4)

print("✅ Success! File repaired. You can now run the app.")