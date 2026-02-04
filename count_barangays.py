import json

with open('davao_city_182_barangays_official.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total barangays: {len(data['barangays'])}")
print(f"\nExpected: 182")
print(f"Actual: {len(data['barangays'])}")
print(f"Difference: {182 - len(data['barangays'])}")

if len(data['barangays']) == 182:
    print("\n✅ Perfect! Exactly 182 barangays!")
else:
    print(f"\n⚠️ Need to adjust by {182 - len(data['barangays'])} barangays")

