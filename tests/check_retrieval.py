import json
import os

from dotenv import load_dotenv
from google import genai

from src.retrieval import retrieve_relevant_chunks


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

with open(
    "sample_test_cases.json",
    "r",
    encoding="utf-8"
) as file:
    test_cases = json.load(file)


for case in test_cases:

    print("\n" + "=" * 60)
    print(case["case_id"])
    print(case["message"])
    print("=" * 60)

    results = retrieve_relevant_chunks(
        case["message"],
        client,
        top_k=3
    )

    for index, result in enumerate(results, start=1):

        print(
            f"{index}. "
            f"{result['source']} "
            f"→ {result['score']:.4f}"
        )