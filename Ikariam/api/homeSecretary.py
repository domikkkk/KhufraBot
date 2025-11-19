from Ikariam.api.session import IkaBot, ensure_action_request
from Ikariam.dataStructure import EMBASSY, CITY_VIEW, Resource
from typing import Dict
import re
import json
from dataclasses import asdict
import asyncio
from datetime import datetime, timedelta


def ensure_embassy(func):
    def wrapper(self, *args, **kwargs):
        if self.embassy_position == -1:
            if not self.find_embassy():
                raise ValueError("Nie znaleziono ambasady!")
        return func(self, *args, **kwargs)
    return wrapper


class HomeSecretary(IkaBot):
    def __init__(self, gf_token, nick):
        super().__init__(gf_token, nick)
        self.embassy_position: int = -1
    
    @ensure_action_request
    def find_embassy(self) -> bool:
        ids = list(self.dict_of_cities.keys())
        for id in ids:
            if not self.dict_of_cities[id].is_own:
                continue
            self.change_city(id)
            position = self.find_building(EMBASSY)
            if len(position) != 0:
                self.embassy_position = position[0] # at most one embassy in city
                return True
        return False

    @ensure_embassy
    def get_Ally_resources(self):
        data = {
            "view": "embassyHomeSecretaryMembers",
            "cityId": self.current_city_id,
            "position": self.embassy_position,
            "backgroundView": CITY_VIEW,
            "activeTab": "tabEmbassy",
            "currentCityId": self.current_city_id,
            "templateView": "embassy",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        if self._send_request(data, get_html=True):
            return self.updateTemplateData
    
    def get_resources(self) -> Dict[str, Resource]:
        data = self.get_Ally_resources()
        resources = {}
        regex = re.compile(r"\.avatar(\d+)\s*\.(\w+)$")
        for key, value in data.items():
            match = regex.search(key)
            if not match:
                continue
            avatar_id, resource = match.groups()
            if resource == "resource":
                resource = "wood"
            if not avatar_id in resources:
                resources[avatar_id] = {}
            if isinstance(value, dict):
                if "tooltip" in value:
                    resources[avatar_id][resource] = int(value["tooltip"].replace(",", ""))
                else:
                    resources[avatar_id][resource] = value.get("text")
            else:
                resources[avatar_id][resource] = value
        return {avatar_id: Resource(**resources[avatar_id]) for avatar_id in resources}

    def save_to_file(self, filename, resources: Dict[str, Dict[str, str|int]]):
        with open(filename, 'r') as f:
            data = json.load(f)
        date = datetime.now().date()
        if not date in data:
            data[date] = resources
            with open(filename, "w") as f:
                json.dump(date, filename, indent=4)

    async def task_every_day(self):
        while True:
            now = datetime.now()
            target = now.replace(hour=0, minute=5, second=0, microsecond=0)
            if now >= target:
                target += timedelta(days=1)

            # ile sekund czekać
            wait_seconds = (target - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            # wykonujemy zadanie
            resources = self.get_resources()
            resources_dict = {avatar_id: asdict(resources[avatar_id]) for avatar_id in resources}
            self.save_to_file("pomiary.json", resources_dict)
