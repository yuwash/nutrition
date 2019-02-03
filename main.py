#!/usr/bin/env python
from argparse import ArgumentParser


def main(food_name, provider_name):
    """
    :food_name: name of food
    :provider_name: name of database provider
    """
    if provider_name == "livsmedelsdatabasen":
        from providers.livsmedelsdatabasen import (
            LivsmedelsdatabasenNutritionProvider)
        provider = LivsmedelsdatabasenNutritionProvider()
    else:
        raise ValueError("No such provider: {}".format(provider_name))
    food = provider.get_food_nutrition_facts(food_name)
    for key, field in food.fields.items():
        print("{}: {}".format(key, field.value))


if __name__ == "__main__":
    argparser = ArgumentParser(description="Shows nutrition data")
    argparser.add_argument("food_name", help="Name of food")
    args = argparser.parse_args()
    main(args.food_name, "livsmedelsdatabasen")
