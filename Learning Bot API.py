import requests
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Your Telegram bot token
TOKEN = '6939572912:AAFwjZU6485eRyyPXHQMf462IkU-F-qX0CQ'

def parse_command(command):
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

def get_set_code(set_name):
    sets_url = "https://api.scryfall.com/sets"
    response = requests.get(sets_url)
    if response.status_code != 200:
        return None

    sets_data = response.json()
    for set_item in sets_data['data']:
        if set_item['name'].lower() == set_name.lower():
            return set_item['code']
    return None

def fetch_data(data_choice, filter_choice, amount, name):
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

    cards = [card for card in cards]

    if data_choice == "low":
        sorted_cards = sorted(cards, key=lambda x: float(x['prices']['usd'] or float('inf')))
    else:
        sorted_cards = sorted(cards, key=lambda x: float(x['prices']['usd'] or 0), reverse=True)

    return sorted_cards[:amount]

def format_data(cards):
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

def fetch_and_display_data(update: Update, context: CallbackContext):
    command = update.message.text
    data_choice, filter_choice, amount, name = parse_command(command)
    if not data_choice or not filter_choice or not amount or not name:
        update.message.reply_text("Invalid command format. Please follow the format: /low|high card|set number name")
        return
    try:
        cards = fetch_data(data_choice, filter_choice, amount, name)
        if not cards:
            update.message.reply_text("No cards found.")
            return
        formatted_data = format_data(cards)
        update.message.reply_text(formatted_data, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def run_tests(update: Update, context: CallbackContext):
    test_commands = [
        "/low card 3 Black Lotus",
        "/high card 5 Island",
        "/low set 2 Limited Edition Alpha",
        "/high set 10 Battle for Zendikar"
    ]
    for command in test_commands:
        update.message.reply_text(f"Executing: {command}")
        data_choice, filter_choice, amount, name = parse_command(command)
        if data_choice and filter_choice and amount and name:
            cards = fetch_data(data_choice, filter_choice, amount, name)
            if cards:
                formatted_data = format_data(cards)
                update.message.reply_text(formatted_data, parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text("No cards found.")
        else:
            update.message.reply_text("Invalid command format.")

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('test', run_tests))
    dispatcher.add_handler(CommandHandler(['low', 'high'], fetch_and_display_data))

    updater.start_polling()
    updater.idle()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I'm a Scryfall bot. You can use commands like /low or /high to search for card prices.")

if __name__ == "__main__":
    main()
