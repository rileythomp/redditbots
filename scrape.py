import requests
from bs4 import BeautifulSoup
# from time import time

alphabet = 'abcdefghijklmnopqrstuvwxyz'
print('player_list = {')
# count = 0
# start = time()
for letter in alphabet:
    url = f'https://www.basketball-reference.com/players/{letter}/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id='players')
    players = results.find_all('tr')
    for player in players[1:]:
        player_name = player.find(attrs={'data-stat':'player'}).text.lower()
        year_max = player.find(attrs={'data-stat':'year_max'}).text
        if int(year_max) == 2022:
            # count += 1
            print(f'\t"{player_name}": ["{player_name}", "{player_name.split(" ")[-1]}"],')
print('}')
# end = time()
# print(count, end-start)
