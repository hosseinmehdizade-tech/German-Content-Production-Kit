"""Self-contained C1 gate regression checks; synthetic data only."""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("c1gate", Path(__file__).with_name("validate_c1_rich_card.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def card():
    return {
        "id": "C1-P01-E001", "front": "der Austausch, -e",
        "meanings": [{"de": "gegenseitiger Austausch", "fa": "تبادل", "en": "exchange"}],
        "examples": [{"de": f"Wir tauschen Gedanken Nummer {i} aus.", "fa": f"ما فکر {i} را مبادله می‌کنیم.", "en": f"We exchange thought {i}."} for i in range(1, 5)],
        "details": [{"title": "Kombinationen", "items": [{"de": "den Austausch fördern", "fa": "تبادل را تقویت کردن", "en": "promote exchange", "source": "course", "teaching_delta": "usable verb-object collocation"}]}],
        "c1_right_review": {key: ({"decision": "VERIFIED_PRESENT"} if key == "Kombinationen" else {"decision": "CLOSED_NO_FORCE", "reason": "no supported useful relation"}) for key in mod.SECTIONS},
        "c1_grammar_review": {"decision": "VERIFIED", "reason": "noun article and plural checked"}
    }


def fails(code, cards):
    return code in {item["code"] for item in mod.validate(cards)["errors"]}


def test_structural_positive_and_negative():
    assert mod.validate([card()])["status"].startswith("STRUCTURAL_PASS")
    for field, code in [("meanings", "MISSING_TYPED_MEANINGS_DE_FA_EN"), ("c1_right_review", "SECTION_NOT_REVIEWED"), ("c1_grammar_review", "GRAMMAR_FORMS_REKTION_NOT_REVIEWED")]:
        sample = card()
        del sample[field]
        assert fails(code, [sample])
    sample = card()
    sample["examples"].pop()
    assert fails("EXACTLY_FOUR_EXAMPLES_REQUIRED", [sample])
    sample = card()
    sample["examples"][0].pop("en")
    assert fails("EXAMPLE_MISSING_DE_FA_EN", [sample])
    sample = card()
    sample["meanings"][0].pop("en")
    assert fails("INCOMPLETE_MEANING", [sample])
    sample = card()
    sample["details"][0]["items"][0]["de"] = sample["examples"][0]["de"]
    assert fails("COMBINATION_EQUALS_EXAMPLE", [sample])
    sample = card()
    sample["details"][0]["items"][0]["de"] = "tauschen Gedanken"
    del sample["details"][0]["items"][0]["source"]
    assert fails("OVERLAPPING_COMBINATION_NEEDS_INDEPENDENT_EVIDENCE", [sample])
    sample = card()
    sample["c1_right_review"]["Antonyme"] = {"decision": "HOLD"}
    assert fails("SECTION_UNRESOLVED_OR_INVALID_DECISION", [sample])
    sample = card()
    del sample["details"][0]["items"][0]["fa"]
    assert fails("SECTION_ITEM_MISSING_DE_FA", [sample])
    sample = card()
    del sample["details"][0]["items"][0]["en"]
    assert fails("COMBINATION_MISSING_EN", [sample])


if __name__ == "__main__":
    test_structural_positive_and_negative()
    print("PASS: synthetic structural positive and negative cases")
