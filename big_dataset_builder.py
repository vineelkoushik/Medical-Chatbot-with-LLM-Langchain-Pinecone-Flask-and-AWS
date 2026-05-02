import wikipediaapi
import json
import time
from tqdm import tqdm

# ---------------- WIKIPEDIA SETUP ---------------- #
wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="MedicalChatbot/1.0 (educational project)"
)

# ---------------- MEDICAL CATEGORIES ---------------- #
categories = [
    "Category:Diseases and disorders",
    "Category:Infectious diseases",
    "Category:Respiratory diseases",
    "Category:Cardiovascular diseases",
    "Category:Neurological disorders",
    "Category:Skin conditions",
    "Category:Cancers",
    "Category:Genetic diseases"
]

# ---------------- GET PAGE NAMES ---------------- #
def get_pages_from_category(cat_name):
    try:
        category = wiki.page(cat_name)
        if category.exists():
            return list(category.categorymembers.keys())
    except:
        return []
    return []

print("📦 Collecting disease names...")

disease_names = set()

for cat in categories:
    pages = get_pages_from_category(cat)
    disease_names.update(pages)

disease_names = list(disease_names)

print(f"🔎 Total pages found: {len(disease_names)}")

# ---------------- DATA STORAGE ---------------- #
dataset = set()

def clean(text):
    return text.replace("\n", " ").strip()

# ---------------- SCRAPING LOOP (SAFE) ---------------- #
print("📄 Fetching medical summaries safely...")

for name in tqdm(disease_names[:1500]):

    try:
        page = wiki.page(name)

        # check existence safely
        if not page.exists():
            continue

        summary = page.summary

        # filter useless pages
        if summary and len(summary) > 200:
            dataset.add((name, clean(summary[:1500])))

    except Exception as e:
        print(f"⚠️ Skipped {name}")
        time.sleep(2)  # cooldown after failure
        continue

    # IMPORTANT: prevent Wikipedia ban
    time.sleep(1.2)

# ---------------- FINAL CLEANING ---------------- #
final_data = []

for name, content in dataset:
    final_data.append({
        "title": name,
        "content": content
    })

# ---------------- SAVE FILE ---------------- #
with open("medical_1000_dataset.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2)

print(f"✅ Dataset created successfully! Total records: {len(final_data)}")