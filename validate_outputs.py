import os
import json
from jsonschema import validate, ValidationError

# Load schema
with open("output_schema.json") as schema_file:
    schema = json.load(schema_file)

output_dir = "output"
errors = []

for filename in os.listdir(output_dir):
    if filename.endswith(".json"):
        with open(os.path.join(output_dir, filename)) as f:
            try:
                data = json.load(f)
                validate(instance=data, schema=schema)
                print(f"✅ {filename} is valid ✅")
            except ValidationError as e:
                print(f"❌ {filename} is INVALID ❌")
                errors.append((filename, str(e)))

if not errors:
    print("\n🎉 All files passed schema validation!")
else:
    print("\n🚨 Some files failed:")
    for name, err in errors:
        print(f"→ {name}: {err}")
