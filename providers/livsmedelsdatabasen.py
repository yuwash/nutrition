from __future__ import print_function
import os
import os.path
import sys
from appdirs import user_data_dir
from bs4 import BeautifulSoup
import dataset
import requests
import nutrition


class LivsmedelsdatabasenNutritionProvider(object):
    """use the Livsmedelsdatabasen API of the Livsmedelsverket"""
    data_path = user_data_dir("nutrition", "yuwash.eu")
    db_path = os.path.join(data_path, "nutrition.db")
    cache_filename_pattern = os.path.join(
        data_path, "livsmedelsdatabasen_{api_method}_{version}")

    api_url = "http://www7.slv.se/apilivsmedel/LivsmedelService.svc/Livsmedel/"
    api_version = "20230101"
    api_url_suffixes = dict(
        naringsvarde="Naringsvarde/",
        klassificering="Klassificering/",
    )
    food_livsmedel = dict(
        number="Nummer",
        name="Namn",
    )
    nutrition_facts_forkortning = {
        nutrition.NutritionFactsAttr.energy: "Ener",
        nutrition.NutritionFactsAttr.fat: "Fett",
        nutrition.NutritionFactsAttr.saturates: "Mfet",
        nutrition.NutritionFactsAttr.carbohydrates: "Kolh",
        nutrition.NutritionFactsAttr.sugars: "Mono/disack",
        nutrition.NutritionFactsAttr.protein: "Prot",
        nutrition.NutritionFactsAttr.phosphorous: "P",
        nutrition.NutritionFactsAttr.iodine: "I",
        nutrition.NutritionFactsAttr.iron: "Fe",
        nutrition.NutritionFactsAttr.calcium: "Ca",
        nutrition.NutritionFactsAttr.potassium: "K",
        nutrition.NutritionFactsAttr.magnesium: "Mg",
        nutrition.NutritionFactsAttr.sodium: "Na",
        nutrition.NutritionFactsAttr.salt: "NaCl",
        nutrition.NutritionFactsAttr.selenium: "Se",
        nutrition.NutritionFactsAttr.zinc: "Zn",
    }

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
    def get_nutrition_facts_value(raw_value):
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
                key.name: self.get_nutrition_facts_value(value_elem.string)
                for key, forkortning
                in self.nutrition_facts_forkortning.items()
                if (
                    parent := next((
                        elem.parent for elem
                        in nutrition_facts_elem.find_all(
                            "Forkortning", string=forkortning)
                        if (value_elem := elem.parent.find("Varde"))
                        and elem.parent.find(
                            "Enhet",
                            string="{:~}".format(nutrition.DEFAULT_UNITS[key])
                        )
                    ), None)
                )
            })
            yield data

    def get_food_nutrition_facts(self, food_name):
        table_name = "food_nutrition_facts"
        table = self.db[table_name]
        entry = table.find_one(name=food_name)
        if entry is None:
            return None
        return {
            attr: nutrition.NutritionFactsField(attr, value)
            for attr in nutrition.NutritionFactsAttr
            if (value := entry.get(attr.name))
        }

    def query_food_names(self, keyword):
        table_name = "food_nutrition_facts"
        table = self.db[table_name]
        entries = table.find(name={"like": "%{}%".format(keyword)})
        return [entry["name"] for entry in entries]

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
        print("Preparing cache {}".format(self.db_path))
        for api_method in self.api_url_suffixes:
            cache_filename = self.get_cache_filename(api_method)
            if os.path.exists(cache_filename):
                continue
            response = requests.get(self.get_full_url(api_method))
            if response.status_code != requests.codes.ok:
                soup = BeautifulSoup(response.text, "html.parser")
                print("".join(soup.find("body").strings), file=sys.stderr)
                raise RuntimeError(
                    "API returned {}".format(response.status_code))
            with open(cache_filename, 'wb') as cache_file:
                cache_file.write(response.content)
                created_files[api_method] = cache_filename
        print("Downloaded. Importing into database…")
        table_name = "food_nutrition_facts"
        table = self.db[table_name]
        table.insert_many(tuple(self.iter_food_nutrition_facts()))
        # doesn’t seem to work without converting it into a list/tuple
        return created_files
