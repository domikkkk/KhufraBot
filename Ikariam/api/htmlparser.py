from bs4 import BeautifulSoup, Tag
import re
from Ikariam.dataStructure import Attack, Fleets, Troops, Player
from typing import List, Optional, Dict, Union, Tuple


def get_fleet(html):
    soup = BeautifulSoup(html, 'html.parser')
    tab_ships_div = soup.find('div', id='tabShips')
    content = tab_ships_div.find_all('div', class_='contentBox01h')[0]
    tables = content.find_all('table', class_='militaryList') if tab_ships_div else []
    ships_data = {}
    for table in tables:
        header_row = table.find('tr', class_='title_img_row')
        headers = header_row.find_all('div', class_='tooltip') if header_row else []
        ships = [(header.text, header.find_parent('div').get('class')[1][1:]) for header in headers]
        count_row = table.find('tr', class_='count')
        counts = [td.text.strip() for td in count_row.find_all('td')[1:]]
        for (name, ship_id), count in zip(ships, counts):
            ships_data[name] = {'id': ship_id, 'count': count}
    return ships_data


def get_fleet_foreign(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find_all('div', class_='contentBox01h')[0]
    row_troops = content.find_all('td', class_='rowTroop')
    units = []
    for row in row_troops:
        army_buttons = row.find_all('div', class_='fleetbutton')
        for button in army_buttons:
            unit_name = button.get('title')
            unit_count = button.text.strip()
            units.append((unit_name, unit_count))
    return units



def get_date(html):
    script_tag = html.find('script', string=True).get_text()
    match = re.search(r'enddate:\s*(\d+)', script_tag)
    return int(match.group(1))


def clean_whitespace(text):
    return re.sub(r'\s+', ' ', text.strip())


def extract_brackets(content):
    return re.findall(r'\[(.*?)\]', content)


def get_actionRequest(html) -> Optional[str]:
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find("input", {"name": "actionRequest"})
    return tag.get("value")


def get_currentcityId(html) -> Optional[int]:
    pattern = r"currentCityId:\s*(\d+)"
    match = re.search(pattern, html)
    if match:
        city_id = int(match.group(1))
        return city_id


def get_attacks(html) -> List[Attack]:
    soup = BeautifulSoup(html, 'html.parser')
    mainview = soup.find('div', id='mainview')
    table = mainview.find('table', class_="embassyTable")
    attacks = []
    for row in table.find_all('tr')[1:]:
        row: Tag
        if "No members of your alliance are being attacked at the moment." in row.text:
            break
        cells = row.find_all('td')
        date = get_date(cells[0])
        who = Player(*[clean_whitespace(x.text) for x in cells[3].find_all('a', class_="bold")])
        whom = Player(*[clean_whitespace(x.text) for x in cells[4].find_all('a', class_="bold")])
        attack = Attack(date, cells[1].text.strip(), cells[2].text.strip(), who, whom)
        attacks.append(attack)
    return attacks


def get_units(html, land=True) -> Dict[str, Optional[Union[Troops, Fleets]]]:
    soup = BeautifulSoup(html, 'html.parser')
    mainview = soup.find('div', id='mainview')
    tables = mainview.find_all('table', class_="table01 embassyTable troops")
    obj = Troops if land else Fleets
    units = {}
    for table in tables:
        for row in table.find_all('tr')[1:-1]:
            player_name = row.find('td', class_='left').find('a').get_text(strip=True)
            if not player_name in units:
                units[player_name] = []
            for td in row.find_all('td', class_='right'):
                units[player_name].append(int(td.get_text(strip=True).replace(',', '')))
    units = {name: obj(*units[name]) for name in units}
    return units


def get_wonder_lv(html) -> int:
    soup = BeautifulSoup(html, 'html.parser')
    lv = int(soup.find('div', id='currentWonderLevel').get_text(strip=True))
    return lv


def get_transporter_info(html, template) -> Dict[str, int]:
    soup = BeautifulSoup(html, 'html.parser')
    views = soup.find_all('div', class_='tooltip')
    capacities = {}
    for view in views:
        id = view.get("id")
        if "phoenician" in id.lower():
            continue
        info = template.get(id)
        if info:
            text = info.get("text")
            numbers = re.findall(r'\d[\d,]*', text)
            if numbers:
                number = int(numbers[-1].replace(',', ''))
                name = re.search(r'^js_(.+?)Tooltip$', id).group(1)
                capacities[name] = number
    return capacities