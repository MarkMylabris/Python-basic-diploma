import requests
from typing import List, Optional, Dict


def get_set_code(set_name: str) -> Optional[str]:
    """
    Получить код набора по его имени.

    :param set_name: Имя набора
    :return: Код набора или None, если не найден
    """
    sets_url = "https://api.scryfall.com/sets"
    response = requests.get(sets_url)
    if response.status_code != 200:
        return None

    sets_data = response.json()
    for set_item in sets_data['data']:
        if set_item['name'].lower() == set_name.lower():
            return set_item['code']
    return None


def fetch_data(data_choice: Optional[str], filter_choice: str, amount: int, name: str,
               low_price: Optional[float] = None, high_price: Optional[float] = None) -> List[Dict]:
    """
    Получить данные карт с сайта Scryfall.

    :param data_choice: Порядок данных (low/high)
    :param filter_choice: Фильтр (card/set)
    :param amount: Количество карт
    :param name: Имя карты или набора
    :param low_price: Нижняя граница цены (опционально)
    :param high_price: Верхняя граница цены (опционально)
    :return: Список данных карт
    """
    base_url = "https://api.scryfall.com/cards/search"

    if filter_choice == "card":
        query = f'!"{name}"'
    else:
        set_code = get_set_code(name)
        if not set_code:
            return []
        query = f'set:{set_code}'

    url = f"{base_url}?q={query}&order=usd"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    cards = data.get('data', [])

    if len(cards) == 0:
        return []

    if filter_choice == "card" and len(cards) == 1:
        oracle_id = cards[0]['oracle_id']
        url = f"https://api.scryfall.com/cards/search?order=usd&q=oracleid:{oracle_id}&unique=prints"
        response = requests.get(url)
        if response.status_code != 200:
            return []

        data = response.json()
        cards = data.get('data', [])
        while len(cards) < amount and data.get('has_more'):
            response = requests.get(data['next_page'])
            if response.status_code != 200:
                break
            data = response.json()
            cards.extend(data.get('data', []))

    print(f"Fetched {len(cards)} cards before applying price filter")

    if low_price is not None and high_price is not None:
        cards = [card for card in cards if
                 card['prices']['usd'] is not None and low_price <= float(card['prices']['usd']) <= high_price]

    print(f"Filtered {len(cards)} cards within the price range {low_price} - {high_price}")

    if data_choice:
        if data_choice == "low":
            sorted_cards = sorted(cards, key=lambda x: float(x['prices']['usd'] or float('inf')))
        else:
            sorted_cards = sorted(cards, key=lambda x: float(x['prices']['usd'] or 0), reverse=True)
        return sorted_cards[:amount]

    return cards
