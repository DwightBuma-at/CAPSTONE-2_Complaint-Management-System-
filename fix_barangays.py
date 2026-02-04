import json

# Read the file
with open('davao_city_182_barangays_official.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Remove duplicates while preserving order
seen = set()
unique_barangays = []
for barangay in data['barangays']:
    if barangay not in seen:
        seen.add(barangay)
        unique_barangays.append(barangay)

print(f"Original count: {len(data['barangays'])}")
print(f"Unique count: {len(unique_barangays)}")
print(f"Duplicates removed: {len(data['barangays']) - len(unique_barangays)}")

# If we have exactly 182, save it
if len(unique_barangays) == 182:
    data['barangays'] = unique_barangays
    with open('davao_city_182_barangays_official.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("\n✅ File updated with exactly 182 unique barangays!")
elif len(unique_barangays) < 182:
    print(f"\n⚠️ Need {182 - len(unique_barangays)} more barangays")
    print("Missing barangays need to be added from official sources")
else:
    print(f"\n⚠️ Have {len(unique_barangays)} barangays, need to remove {len(unique_barangays) - 182}")

