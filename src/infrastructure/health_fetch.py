import csv
import re
import requests
from pathlib import Path
from html import unescape

URL = "https://chamoli.gov.in/public-utility-category/hospitals/"

OUTPUT_FILE = Path("data/health/health_facilities.csv")

HEADERS = {
    "User-Agent": "TRINETRA/1.0 disaster monitoring research project"
}


def clean_text(text):
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


print("🌐 Fetching official Chamoli hospital data...")

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

response.raise_for_status()

html = response.text

print("✅ Official page fetched")


# Extract hospital cards from the page
pattern = re.compile(
    r'<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|</main>|</article>)',
    re.IGNORECASE | re.DOTALL
)

matches = pattern.findall(html)

facilities = []

for name_html, content_html in matches:

    name = clean_text(name_html)
    content = clean_text(content_html)

    if not name:
        continue

    # Only keep actual hospital/facility entries
    if not (
        name.upper().startswith("CHC")
        or "HOSPITAL" in name.upper()
        or "AYUSH" in name.upper()
    ):
        continue

    # Extract PIN code
    pin_match = re.search(r"\b(\d{6})\b", content)
    pincode = pin_match.group(1) if pin_match else ""

    # Extract phone number
    phone_match = re.search(
        r"(?:Phone|फोन)\s*:\s*([0-9 -]+)",
        content,
        re.IGNORECASE
    )
    phone = phone_match.group(1).strip() if phone_match else ""

    # Determine facility type
    name_upper = name.upper()

    if name_upper.startswith("CHC"):
        facility_type = "CHC"
    elif "DISTRICT HOSPITAL" in name_upper:
        facility_type = "District Hospital"
    elif "AYUSH" in name_upper:
        facility_type = "AYUSH"
    else:
        facility_type = "Hospital"

    # Remove unwanted repeated spaces
    location_text = content

    facilities.append({
        "facility_name": name,
        "facility_type": facility_type,
        "district": "Chamoli",
        "location": location_text,
        "pincode": pincode,
        "phone": phone,
        "latitude": "",
        "longitude": "",
        "source": URL
    })


# Remove duplicate facility names
unique = {}

for facility in facilities:
    unique[facility["facility_name"]] = facility

facilities = list(unique.values())


if not facilities:
    raise RuntimeError(
        "❌ No hospital records found. Website structure may have changed."
    )


OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

fieldnames = [
    "facility_name",
    "facility_type",
    "district",
    "location",
    "pincode",
    "phone",
    "latitude",
    "longitude",
    "source"
]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(facilities)


print(f"\n🏥 Facilities found: {len(facilities)}")
print(f"💾 Saved to: {OUTPUT_FILE}")

for facility in facilities:
    print(
        f"   • {facility['facility_name']} "
        f"({facility['facility_type']})"
    )