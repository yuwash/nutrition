from __future__ import print_function
import os
import os.path
import sys
from appdirs import user_data_dir
from bs4 import BeautifulSoup
import dataset
import requests
from nutrition import MacroFoodNutritionFacts


class LivsmedelsdatabasenNutritionProvider(object):
    """use the Livsmedelsdatabasen API of the Livsmedelsverket"""
    data_path = user_data_dir("nutrition", "yuwash.eu")
    db_path = os.path.join(data_path, "nutrition.db")
    cache_filename_pattern = os.path.join(
        data_path, "livsmedelsdatabasen_{api_method}_{version}")

    api_url = "http://www7.slv.se/apilivsmedel/LivsmedelService.svc/Livsmedel/"
    api_version = "20190101"
    api_url_suffixes = dict(
        naringsvarde="Naringsvarde/",
        klassificering="Klassificering/",
    )
    food_livsmedel = dict(
        number="Nummer",
        name="Namn",
    )
    nutrition_facts_forkortning = dict(
        energy="Enkj",
        fat="Fett",
        saturates="Mfet",
        carbohydrates="Kolh",
        sugars="Mono/disack",
        protein="Prot",
        salt="NaCl",
    )

    def __init__(self):
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
        self.prepare_cache()

    def get_soup(self, api_method):
        with open(self.get_cache_filename(api_method)) as cache_file:
            return BeautifulSoup(cache_file, "xml")

    @classmethod
    def get_basic_food_data(cls, food_soup):
        data = {
            key: food_soup.find(tag_name).string
            for key, tag_name in cls.food_livsmedel.items()
        }
        data["number"] = int(data["number"])
        return data

    @staticmethod
    def get_nutrition_facts_value(food_nutrition_facts_soup):
        raw_value = food_nutrition_facts_soup.find("Varde").string
        return float(
            raw_value.replace(",", ".", 1)  # European format
            .replace("\xa0", "")  # non-breaking space
        )

    def iter_food_nutrition_facts(self):
        soup = self.get_soup("naringsvarde")
        for food_elem in soup("Livsmedel"):
            try:
                nutrition_facts_elem = food_elem.Naringsvarden
            except AttributeError:
                continue
            data = self.get_basic_food_data(food_elem)
            data.update(**{
                key: self.get_nutrition_facts_value(
                    nutrition_facts_elem.find(
                        "Forkortning", string=forkortning).parent)
                for key, forkortning
                in self.nutrition_facts_forkortning.items()
            })
            yield data

    def get_food_nutrition_facts(self, food_name):
        table_name = "food_nutrition_facts"
        table = self.db[table_name]
        entry = table.find_one(name=food_name)
        if entry is None:
            return None
        for attr in {"id", "name", "number"}:
            del entry[attr]
        return MacroFoodNutritionFacts(**entry)

    def get_cache_filename(self, api_method):
        return self.cache_filename_pattern.format(
            api_method=api_method, version=self.api_version)

    def get_full_url(self, api_method):
        return (
            self.api_url
            + self.api_url_suffixes[api_method]
            + self.api_version
        )

    @property
    def db(self):
        return dataset.connect("sqlite:///" + self.db_path)

    def prepare_cache(self):
        created_files = {}
        if os.path.exists(self.db_path):
            return created_files
        for api_method in self.api_url_suffixes:
            cache_filename = self.get_cache_filename(api_method)
            if os.path.exists(cache_filename):
                continue
            response = requests.get(self.get_full_url(api_method))
            if response.status_code != 200:
                soup = BeautifulSoup(response.text, "html.parser")
                print("".join(soup.find("body").strings), file=sys.stderr)
                raise RuntimeError(
                    "API returned {}".format(response.status_code))
            with open(cache_filename, 'wb') as cache_file:
                cache_file.write(response.content)
                created_files[api_method] = cache_filename
        table_name = "food_nutrition_facts"
        table = self.db[table_name]
        table.insert_many(tuple(self.iter_food_nutrition_facts()))
        # doesn’t seem to work without converting it into a list/tuple
        return created_files
