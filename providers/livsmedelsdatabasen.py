import os.path
from bs4 import BeautifulSoup
import requests
from nutrition import MacroFoodNutritionFacts


class LivsmedelsdatabasenNutritionProvider(object):
    """use the Livsmedelsdatabasen API of the Livsmedelsverket"""
    api_url = "http://www7.slv.se/apilivsmedel/LivsmedelService.svc/Livsmedel/"
    api_version = "20190101"
    api_url_suffixes = dict(
        naringsvarde="Naringsvarde/",
        klassificering="Klassificering/",
    )
    cache_filename_pattern = os.path.expanduser(
        "~/nutrition_livsmedelsdatabasen_{api_method}_{version}")

    def __init__(self):
        self.prepare_cache()

    def get_soup(self, api_method):
        with open(self.get_cache_filename(api_method)) as cache_file:
            return BeautifulSoup(cache_file, "xml")

    def get_food_nutrition_facts(self, food_name):
        soup = self.get_soup("naringvarde")
        nutrition_facts_kwargs = {}  # TODO
        return MacroFoodNutritionFacts(**nutrition_facts_kwargs)

    def get_cache_filename(self, api_method):
        return self.cache_filename_pattern.format(
            api_method=api_method, version=self.api_version)

    def get_full_url(self, api_method):
        return self.url + self.api_url_suffixes[api_method]

    def prepare_cache(self):
        created_files = {}
        for api_method in self.api_url_suffixes:
            cache_filename = self.get_cache_filename(api_method)
            if os.path.exists(cache_filename):
                continue
            response = requests.get(self.get_full_url(api_method))
            with open(cache_filename, 'wb') as cache_file:
                cache_file.write(response.content)
                created_files[api_method] = cache_filename
        return created_files
