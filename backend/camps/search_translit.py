"""Russian → English query expansion for camp search.

User types "Бали" → backend also searches for "Bali" (and vice-versa).
Covers country and popular region/city names that appear in our DB.
"""

RU_TO_EN = {
    # countries
    'бали': 'Bali',
    'индонезия': 'Indonesia',
    'португалия': 'Portugal',
    'марокко': 'Morocco',
    'морокко': 'Morocco',
    'шри-ланка': 'Sri Lanka',
    'шри ланка': 'Sri Lanka',
    'шри': 'Sri Lanka',
    'испания': 'Spain',
    'россия': 'Russia',
    'коста-рика': 'Costa Rica',
    'коста рика': 'Costa Rica',
    'мальдивы': 'Maldives',
    'таиланд': 'Thailand',
    # regions / cities
    'ломбок': 'Lombok',
    'эрисейра': 'Ericeira',
    'эрисера': 'Ericeira',
    'пенише': 'Peniche',
    'пеничи': 'Peniche',
    'тагазут': 'Taghazout',
    'тамрахт': 'Tamraght',
    'лагос': 'Lagos',
    'мадейра': 'Madeira',
    'фуэртевентура': 'Fuerteventura',
    'лансароте': 'Lanzarote',
    'тенерифе': 'Tenerife',
    'канары': 'Canary',
    'канарские острова': 'Canary Islands',
    'камчатка': 'Kamchatka',
    'калининград': 'Kaliningrad',
    'велигама': 'Weligama',
    'тамариндо': 'Tamarindo',
    'гуанакасте': 'Guanacaste',
    'каскайс': 'Cascais',
    'алгарве': 'Algarve',
    'порту': 'Porto',
}


def expand_query(query: str) -> list[str]:
    """Return [original_query, english_synonym?] — list with 1 or 2 items."""
    if not query:
        return []
    variants = [query]
    key = query.strip().lower()
    en = RU_TO_EN.get(key)
    if en and en.lower() != key:
        variants.append(en)
    return variants
