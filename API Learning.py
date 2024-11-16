import requests

def parse_command(command):
    """
    Parse the input command to extract parameters.

    Args:
        command (str): The command string entered by the user.

    Returns:
        tuple: A tuple containing data_choice, filter_choice, amount, and name.
               Returns (None, None, None, None) if the command is invalid.
    """
    parts = command.split()
    if len(parts) < 4:
        print("Invalid command format. Please follow the format: /low|high card|set number name")
        return None, None, None, None

    data_choice = parts[0][1:]
    filter_choice = parts[1]
    try:
        amount = int(parts[2])
    except ValueError:
        print("Invalid amount. Please enter a valid number.")
        return None, None, None, None

    name = ' '.join(parts[3:])

    if data_choice not in ["low", "high"]:
        print("Invalid choice for data. Please enter /low or /high.")
        return None, None, None, None
    if filter_choice not in ["card", "set"]:
        print("Invalid choice for filter. Please enter card or set.")
        return None, None, None, None

    return data_choice, filter_choice, amount, name

def get_set_code(set_name):
    """
    Fetch the set code for a given set name from the Scryfall API.

    Args:
        set_name (str): The name of the set.

    Returns:
        str: The set code if found, None otherwise.
    """
    sets_url = "https://api.scryfall.com/sets"
    response = requests.get(sets_url)
    if response.status_code != 200:
        print("Failed to fetch sets data from Scryfall API")
        return None

    sets_data = response.json()
    for set_item in sets_data['data']:
        if set_item['name'].lower() == set_name.lower():
            return set_item['code']
    print(f"Set '{set_name}' not found.")
    return None

def fetch_data(data_choice, filter_choice, amount, name):
    """
    Fetch card data from the Scryfall API based on the user's choices.

    Args:
        data_choice (str): 'low' for lowest prices or 'high' for highest prices.
        filter_choice (str): 'card' to filter by card name or 'set' to filter by set name.
        amount (int): The number of cards to display.
        name (str): The name of the card or set.

    Returns:
        list: A list of card data dictionaries.
    """
    base_url = "https://api.scryfall.com/cards/search"

    if filter_choice == "card":  # Filter by card
        query = f'!"{name}"'
    else:  # Filter by set
        set_code = get_set_code(name)
        if not set_code:
            return []
        query = f'set:{set_code}'

    url = f"{base_url}?q={query}&order=usd"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch data from Scryfall API")
        return []

    data = response.json()
    cards = data.get('data', [])

    if len(cards) == 0:
        print("No cards found.")
        return []

    if filter_choice == "card" and len(cards) == 1:
        oracle_id = cards[0]['oracle_id']
        url = f"https://api.scryfall.com/cards/search?order=usd&q=oracleid:{oracle_id}&unique=prints"
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to fetch data from Scryfall API")
            return []

        data = response.json()
        cards = data.get('data', [])
        while len(cards) < amount and data.get('has_more'):
            response = requests.get(data['next_page'])
            if response.status_code != 200:
                print("Failed to fetch additional data from Scryfall API")
                break
            data = response.json()
            cards.extend(data.get('data', []))

    cards = [card for card in cards if card['prices']['usd'] is not None]

    if data_choice == "low":  # Low price
        sorted_cards = sorted(cards, key=lambda x: float(x['prices']['usd'] or float('inf')))
    else:  # High price
        sorted_cards = sorted(cards, key=lambda x: float(x['prices']['usd'] or 0), reverse=True)

    return sorted_cards[:amount]

def format_data(cards):
    """
    Format card data for display.

    Args:
        cards (list): A list of card data dictionaries.

    Returns:
        str: Formatted card data as a string.
    """
    formatted_data = ""
    for card in cards:
        name = card['name']
        set_name = card['set_name']
        card_type = card['type_line']
        version = card.get('frame_effects', 'Regular')
        price = card['prices']['usd']
        image_url = card['image_uris']['normal'] if 'image_uris' in card else "Image not available"
        formatted_data += f"Name: {name}\nSet: {set_name}\nType: {card_type}\nVersion: {version}\nPrice: ${price}\nImage: {image_url}\n\n"
    return formatted_data

def fetch_and_display_data(command):
    """
    Fetch and display card data based on the user's command.

    Args:
        command (str): The command string entered by the user.
    """
    data_choice, filter_choice, amount, name = parse_command(command)
    if not data_choice or not filter_choice or not amount or not name:
        return
    try:
        cards = fetch_data(data_choice, filter_choice, amount, name)
        if not cards:
            return
        formatted_data = format_data(cards)
        print(formatted_data)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def run_tests():
    """
    Run a series of test commands to demonstrate functionality.
    """
    test_commands = [
        "/low card 3 Black Lotus",
        "/high card 5 Island",
        "/low set 2 Limited Edition Alpha",
        "/high set 10 Battle for Zendikar"
    ]
    for command in test_commands:
        print(f"Executing: {command}")
        fetch_and_display_data(command)
        print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    while True:
        command = input("Enter command (or /test to run tests): ")
        if command == "/test":
            run_tests()
        else:
            fetch_and_display_data(command)
