import requests

def read_config(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        apiToken = lines[0].strip()
        chatID = lines[1].strip()
    return apiToken, chatID


def send_to_telegram(message):
    config_file_path = 'config.txt'
    apiToken, chatID = read_config(config_file_path)

    print(apiToken)
    print(chatID)
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    for msg in message:
        try:
            requests.post(apiURL, json={'chat_id': chatID, 'text': msg})
        except Exception as e:
            print(e)



