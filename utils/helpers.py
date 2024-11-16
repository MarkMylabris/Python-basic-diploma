from typing import Optional, Tuple, List, Dict

def format_data(cards: List[Dict]) -> str:
    """
    Форматировать данные карт для отображения.

    :param cards: Список данных карт
    :return: Отформатированная строка данных
    """
    formatted_data = ""
    for card in cards:
        name = card['name']
        set_name = card['set_name']
        card_type = card['type_line']
        version = card.get('frame_effects', 'Обычная')
        price = card['prices']['usd']
        image_url = card['image_uris']['normal'] if 'image_uris' in card else "Изображение недоступно"
        formatted_data += f"Имя: {name}\nНабор: {set_name}\nТип: {card_type}\nВерсия: {version}\nЦена: ${price}\nИзображение: {image_url}\n\n"
    return formatted_data

def parse_command(command: str) -> Tuple[Optional[str], Optional[str], Optional[int], Optional[str]]:
    """
    Разобрать команду для получения данных.

    :param command: Текст команды
    :return: Кортеж значений (data_choice, filter_choice, amount, name)
    """
    parts = command.split()
    if len(parts) < 4:
        return None, None, None, None

    data_choice = parts[0][1:]
    filter_choice = parts[1]
    try:
        amount = int(parts[2])
    except ValueError:
        return None, None, None, None

    name = ' '.join(parts[3:])

    if data_choice not in ["low", "high"]:
        return None, None, None, None
    if filter_choice not in ["card", "set"]:
        return None, None, None, None

    return data_choice, filter_choice, amount, name

def parse_custom_command(command: str) -> Tuple[Optional[str], Optional[float], Optional[float], Optional[str]]:
    """
    Разобрать пользовательскую команду с диапазоном цен.

    :param command: Текст команды
    :return: Кортеж значений (filter_choice, low_price, high_price, name)
    """
    parts = command.split()
    if len(parts) < 5:
        return None, None, None, None

    filter_choice = parts[1]
    try:
        low_price = float(parts[2])
        high_price = float(parts[3])
    except ValueError:
        return None, None, None, None

    name = ' '.join(parts[4:])

    if filter_choice not in ["card", "set"]:
        return None, None, None, None

    return filter_choice, low_price, high_price, name
