from evaluator import normalize_text, score_answer, evaluate_items


def test_normalize_text():
    result = normalize_text("  Approved  ")
    assert result == "approved"


def test_exact_match_after_normalization():
    result = score_answer("approved", "Approved")

    assert result["score"] == 1.0
    assert result["reason"] == "Exact match after normalization."


def test_missing_answer_scores_zero():
    result = score_answer("Earth", "")

    assert result["score"] == 0.0


def test_partial_token_overlap():
    result = score_answer("Earth", "Humans live on Earth.")

    assert result["score"] == 1.0


def test_evaluate_items_summary():
    items = [
        {
            "id": "1",
            "reference_answer": "approved",
            "model_answer": "Approved"
        },
        {
            "id": "2",
            "reference_answer": "red",
            "model_answer": "blue"
        }
    ]

    output = evaluate_items(items)

    assert output["summary"]["number_of_items"] == 2
    assert output["summary"]["number_of_exact_matches"] == 1
    assert output["summary"]["number_of_failed_items"] == 1
    assert output["summary"]["average_score"] == 0.5