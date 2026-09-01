from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

BASE_COLUMNS = [
    'id','card_type','domain','category','source','level','lesson','deck','front','back',
    'front_label','back_label','front_lang','back_lang','typing_target','examples','related',
    'opposites','details','custom_fields','tags','notes','order'
]

SEMANTIC_CONTRACT = 'gfp-german-language-content@3.1.3'
RUNTIME_CONTENT_CONTRACT = 'gfp-german-learning-content@1.0.0'
TRANSPORT_PROFILE = 'universal-v2'
PROMPT_VERSION = 'v3.1.5'
VALIDATOR_VERSION = 'v3.1.5'

ENTRY_TYPE_MAP = {
    'verb': 'verb',
    'nomen': 'noun',
    'adjektiv': 'adjective',
    'adverb': 'adverb',
    'praeposition': 'preposition',
    'konnektor': 'conjunction',
    'konjunktion': 'conjunction',
    'pronomen': 'pronoun',
    'artikelwort': 'artikelwort',
    'partikel': 'particle',
    'interjektion': 'interjection',
    'redemittel': 'phrase',
    'phrase': 'phrase',
    'idiom': 'idiom',
    'redewendung': 'idiom',
    'kollokation': 'collocation',
    'nomen_verb_verbindung': 'nvv',
    'satzmuster': 'sentence_pattern',
    'satz': 'sentence',
    'frage_antwort': 'qa',
    'grammatische_struktur': 'grammar_structure',
    'numeral': 'numeral',
    'abkuerzung': 'abbreviation',
    'generic': 'custom',
}

CONNECTION_TITLES = {
    'nvv': 'NVV',
    'collocation': 'Kollokationen',
    'pattern': 'Muster',
    'fixed_expression': 'Feste Wendungen',
    'prepositional_pattern': 'Präpositionale Muster',
    'common_combination': 'Typische Verbindungen',
    'other': 'Verbindungen',
}

CORE_LABELS = {
    'present_3sg': 'Präsens (3. Sg.)',
    'preterite_3sg': 'Präteritum',
    'perfect': 'Perfekt',
    'participle_ii': 'Partizip II',
    'participle_i': 'Partizip I',
    'auxiliary': 'Hilfsverb',
    'article': 'Artikel',
    'singular': 'Singular',
    'plural': 'Plural',
    'comparative': 'Komparativ',
    'superlative': 'Superlativ',
}


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def clean_cell(value: Any) -> str:
    if value is None:
        return ''
    text = str(value)
    return ' '.join(text.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').split())


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    return [text] if text else []


def profile_language(profile: dict[str, Any], which: str, fallback: str) -> str:
    langs = profile.get('languages') or {}
    if which == 'source':
        node = langs.get('source') or {}
        return str(node.get('lang') or fallback)
    translations = langs.get('translations') or []
    preferred = next((x for x in translations if str(x.get('lang') or '').lower().startswith('fa')), None)
    if preferred:
        return str(preferred.get('lang'))
    if translations:
        return str(translations[0].get('lang') or fallback)
    return fallback


def presentation_examples(unit: dict[str, Any]) -> list[dict[str, Any]]:
    german: list[dict[str, Any]] = []
    english: list[dict[str, Any]] = []
    for ex in sorted(unit.get('examples') or [], key=lambda x: int(x.get('order') or 0)):
        text = str(ex.get('text') or '').strip()
        lang = str(ex.get('lang') or 'de-DE').strip() or 'de-DE'
        if text:
            german.append({'text': text, 'lang': lang, 'role': 'example', 'label': str(ex.get('id') or ''), 'order': 0})
        for tr in ex.get('translations') or []:
            tr_lang = str(tr.get('lang') or '').strip()
            tr_text = str(tr.get('text') or '').strip()
            if tr_text and tr_lang.lower().startswith('en'):
                english.append({'text': tr_text, 'lang': tr_lang, 'role': 'example', 'label': f"translation:{ex.get('id','')}", 'order': 0})
                break
    out = german + english
    for i, item in enumerate(out, 1):
        item['order'] = i
    return out


def extract_related(unit: dict[str, Any]) -> tuple[list[str], list[str]]:
    details = unit.get('details') or {}
    core = unit.get('core') or {}
    synonyms = as_list(details.get('synonyms')) or as_list(core.get('synonyms'))
    antonyms = as_list(details.get('antonyms')) or as_list(core.get('antonyms'))
    return synonyms, antonyms


def readable_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [clean_cell(x) for x in value if clean_cell(x)]
    if isinstance(value, dict):
        return [f'{k}: {clean_cell(v)}' for k, v in value.items() if clean_cell(v)]
    if isinstance(value, bool):
        return ['ja' if value else 'nein']
    text = clean_cell(value)
    return [text] if text else []


def build_details(unit: dict[str, Any]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    core = unit.get('core') or {}
    details = unit.get('details') or {}

    form_items = []
    for key, label in CORE_LABELS.items():
        if key in core and core[key] not in (None, '', []):
            vals = readable_value(core[key])
            if vals:
                form_items.extend([f'{label}: {v}' for v in vals])
    if form_items:
        sections.append({'title': 'Formen', 'items': form_items})

    if details.get('rection'):
        sections.append({'title': 'Rektion', 'items': readable_value(details.get('rection'))})

    excluded = {'rection', 'synonyms', 'antonyms'}
    for key, value in details.items():
        if key in excluded or value in (None, '', [], {}):
            continue
        title = key.replace('_', ' ').strip().title()
        items = readable_value(value)
        if items:
            sections.append({'title': title, 'items': items})

    grouped: dict[str, list[str]] = {}
    for conn in unit.get('connections') or []:
        text = clean_cell(conn.get('text'))
        kind = str(conn.get('kind') or 'other')
        if text:
            grouped.setdefault(kind, []).append(text)
    for kind, items in grouped.items():
        sections.append({'title': CONNECTION_TITLES.get(kind, 'Verbindungen'), 'items': items})

    return sections


def build_custom_fields(unit: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    ctype = str(unit.get('type') or 'generic')
    core = unit.get('core') or {}
    details = unit.get('details') or {}
    custom: dict[str, Any] = {
        'entry_type': ENTRY_TYPE_MAP.get(ctype, ctype),
        'canonical_entry_type': ctype,
        'learning_unit_id': unit.get('id'),
        'semantic_identity': unit.get('id'),
        'german_learning_contract': RUNTIME_CONTENT_CONTRACT,
        'semantic_contract': SEMANTIC_CONTRACT,
        'source_profile_id': profile.get('profile_id'),
        'german_definition': unit.get('definition_de', ''),
        'english': unit.get('english_gloss', ''),
        'direction_policy': 'language-pair',
        'canonical_unit': unit,
    }
    if ctype == 'verb':
        custom.update({
            'present': core.get('present_3sg', ''),
            'preterite': core.get('preterite_3sg', ''),
            'perfect': core.get('perfect', ''),
            'participle_ii': core.get('participle_ii', ''),
            'auxiliary': core.get('auxiliary', ''),
            'reflexive': core.get('reflexive', False),
            'is_reflexive': core.get('reflexive', False),
            'is_separable': str(core.get('separability') or '') == 'separable',
            'rection': '; '.join(as_list(details.get('rection'))),
            'typingCore': unit.get('headword', ''),
            'typingStandard': unit.get('headword', ''),
            'typingTargetLang': profile_language(profile, 'source', 'de-DE'),
            'typingTargetDir': 'ltr',
            'typingTargetLabel': 'Wort',
        })
    return custom


def unit_to_row(unit: dict[str, Any], profile: dict[str, Any]) -> dict[str, str]:
    dataset = profile.get('dataset') or {}
    metadata = unit.get('metadata') or {}
    front_lang = profile_language(profile, 'source', 'de-DE')
    back_lang = profile_language(profile, 'target', 'fa-IR')
    related, opposites = extract_related(unit)
    custom = build_custom_fields(unit, profile)
    row = {
        'id': unit.get('id', ''),
        'card_type': 'de-vocabulary',
        'domain': 'German',
        'category': unit.get('type', ''),
        'source': dataset.get('title') or dataset.get('id') or metadata.get('dataset_id', ''),
        'level': profile.get('cefr', ''),
        'lesson': metadata.get('lesson', ''),
        'deck': metadata.get('deck', ''),
        'front': unit.get('headword', ''),
        'back': unit.get('persian_meaning', ''),
        'front_label': 'Deutsch',
        'back_label': 'فارسی' if back_lang.lower().startswith('fa') else back_lang,
        'front_lang': front_lang,
        'back_lang': back_lang,
        'typing_target': 'front-core',
        'examples': compact_json(presentation_examples(unit)),
        'related': compact_json(related),
        'opposites': compact_json(opposites),
        'details': compact_json(build_details(unit)),
        'custom_fields': compact_json(custom),
        'tags': '; '.join(metadata.get('tags') or []),
        'notes': '',
        'order': metadata.get('unit_order', ''),
    }
    return {k: clean_cell(row.get(k, '')) for k in BASE_COLUMNS}


def write_tsv(dataset: dict[str, Any], profile: dict[str, Any], output: Path) -> None:
    rows = [unit_to_row(unit, profile) for unit in dataset.get('learning_units') or []]
    lines = ['\t'.join(BASE_COLUMNS)]
    for row in rows:
        lines.append('\t'.join(row[k] for k in BASE_COLUMNS))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\ufeff' + '\n'.join(lines) + '\n', encoding='utf-8')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_metadata(output_tsv: Path, metadata_path: Path, build_id: str) -> None:
    obj = {
        'artifact_type': 'gfp-data-build-metadata',
        'metadata_version': '1.0',
        'prompt_version': PROMPT_VERSION,
        'validator_version': VALIDATOR_VERSION,
        'data_build_id': build_id,
        'schema_profile': TRANSPORT_PROFILE,
        'data_file': output_tsv.name,
        'data_sha256': sha256_file(output_tsv),
        'note': f'Semantic source {SEMANTIC_CONTRACT}; runtime content {RUNTIME_CONTENT_CONTRACT}',
    }
    metadata_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    ap = argparse.ArgumentParser(description='Build Flashcards Pro Universal-v2 TSV from gfp-german-language-content canonical JSON.')
    ap.add_argument('--dataset', required=True, type=Path)
    ap.add_argument('--profile', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--metadata', type=Path)
    ap.add_argument('--build-id', default='gfp-content-build-v3.1.5')
    args = ap.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding='utf-8'))
    profile = json.loads(args.profile.read_text(encoding='utf-8'))
    if dataset.get('contract_version') != '3.1.3':
        raise SystemExit(f"dataset contract_version must be 3.1.3, got {dataset.get('contract_version')!r}")
    write_tsv(dataset, profile, args.output)
    if args.metadata:
        write_metadata(args.output, args.metadata, args.build_id)
    print(json.dumps({'status': 'PASS', 'rows': len(dataset.get('learning_units') or []), 'output': str(args.output), 'metadata': str(args.metadata) if args.metadata else None}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
