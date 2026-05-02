import wikipediaapi
import json

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="MedicalChatbot/1.0 (educational project)"
)

diseases = [
    "Diabetes mellitus",
    "Hypertension",
    "Asthma",
    "Tuberculosis",
    "Malaria",
    "Dengue fever",
    "Pneumonia",
    "Cancer",
    "Migraine",
    "Epilepsy",
    "Hepatitis",
    "COVID-19",
    "Anemia",
    "Arthritis",
    "Heart attack",
    "Stroke",
    "Depression",
    "Anxiety",
    "Obesity",
    "Chickenpox"
]

dataset = []

def clean_text(text):
    return text.replace("\n", " ").replace("==", "").strip()

for disease in diseases:
    page = wiki.page(disease)

    if page.exists():
        content = clean_text(page.summary[:2000])

        dataset.append({
            "title": disease,
            "content": content
        })

        print("Added:", disease)
    else:
        print("Not found:", disease)

with open("medical_wikipedia_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2)

print("Dataset created successfully!")