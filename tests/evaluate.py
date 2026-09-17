import json

from dotenv import load_dotenv

from src.decision import make_decision


load_dotenv()


def load_test_cases():
    with open(
        "sample_test_cases.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def main():
    test_cases = load_test_cases()

    correct = 0
    incorrect = 0
    failed = 0

    print("\nAI Decision Evaluation")
    print("=" * 50)

    for case in test_cases:
        expected = case["expected_action"]

        try:
            decision = make_decision(case["message"])

            actual = decision.action
            is_correct = actual == expected

            if is_correct:
                correct += 1
                result = "✓"
            else:
                incorrect += 1
                result = "✗"

            print(f"\n{case['case_id']} {result}")
            print(f"Expected   : {expected}")
            print(f"Actual     : {actual}")
            print(f"Confidence : {decision.confidence}")
            print(f"Sources    : {decision.sources}")

        except Exception as exc:
            failed += 1

            print(f"\n{case['case_id']} ⚠")
            print(f"Expected   : {expected}")
            print(
                f"Error      : "
                f"{type(exc).__name__}: {exc}"
            )

    total = len(test_cases)
    evaluated = correct + incorrect

    print("\n" + "=" * 50)
    print(f"Correct    : {correct}/{total}")
    print(f"Incorrect  : {incorrect}/{total}")
    print(f"Failed     : {failed}/{total}")
    print(f"Evaluated  : {evaluated}/{total}")

    if evaluated > 0:
        accuracy = correct / evaluated * 100
        print(f"Accuracy   : {accuracy:.2f}%")
    else:
        print("Accuracy   : N/A")

    print("=" * 50)
    print("API failures are excluded from accuracy.")


if __name__ == "__main__":
    main()