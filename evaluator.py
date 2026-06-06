import argparse
import json
import re
import sys

## normalization text
def normalize_text(text):
    return re.sub(r"\s+", " ", text.strip().lower())
## tokenization text
def tokenize(text):
    normalized = normalize_text(text)
    return set(re.findall(r"[a-z0-9]+", normalized))
## Scoring function

def score_answer(reference_answer, model_answer):
    if reference_answer is None or model_answer is None:
        return {
            "score": 0.0,
            "reason": "Missing reference or model answer."
        }

    reference = normalize_text(str(reference_answer))
    model = normalize_text(str(model_answer))

    if reference == "" or model == "":
        return {
            "score": 0.0,
            "reason": "Empty reference or model answer."
        }

    if reference == model:
        return {
            "score": 1.0,
            "reason": "Exact match after normalization."
        }

    reference_tokens = tokenize(reference)
    model_tokens = tokenize(model)

    matched_tokens = reference_tokens.intersection(model_tokens)

    if len(reference_tokens) == 0 or len(model_tokens) == 0:
        return {
            "score": 0.0,
            "reason": "No comparable tokens found."
        }

    score = len(matched_tokens) / len(reference_tokens)

    if score == 0:
        reason = "No token overlap with reference answer."
    else:
        reason = f"Partial match: {len(matched_tokens)} of {len(reference_tokens)} reference token(s) matched."

    return {
        "score": round(score, 3),
        "reason": reason
    }

## evaluation
def evaluate_items(items):
    results = []
    total_score = 0.0
    exact_matches = 0
    failed_items = 0

    for index, item in enumerate(items):
        item_id = str(item.get("id", index + 1))

        result = score_answer(
            item.get("reference_answer"),
            item.get("model_answer")
        )

        score = result["score"]
        total_score += score

        if score == 1.0:
            exact_matches += 1

        if score == 0.0:
            failed_items += 1

        results.append({
            "id": item_id,
            "score": score,
            "reason": result["reason"]
        })

    number_of_items = len(items)

    if number_of_items == 0:
        average_score = 0.0
    else:
        average_score = total_score / number_of_items

    return {
        "items": results,
        "summary": {
            "average_score": round(average_score, 3),
            "number_of_items": number_of_items,
            "number_of_exact_matches": exact_matches,
            "number_of_failed_items": failed_items
        }
    }
def load_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError("Input file is not valid JSON.")

    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of evaluation items.")

    return data

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate AI assistant answers against reference answers."
    )

    parser.add_argument(
        "input_file",
        help="Path to the JSON input file."
    )

    args = parser.parse_args()

    try:
        items = load_json_file(args.input_file)
        output = evaluate_items(items)
        print(json.dumps(output, indent=2))
        return 0

    except ValueError as error:
        print(json.dumps({"error": str(error)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())