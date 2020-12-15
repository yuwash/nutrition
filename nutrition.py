from pint import UnitRegistry
from pint.quantity import Quantity


def get_eu_default_units():
    units = dict(energy=unit_registry.kJ)
    units["fat"] = \
        units["saturates"] = \
        units["carbohydrates"] = \
        units["sugars"] = \
        units["protein"] = \
        units["salt"] = \
        unit_registry.g
    return units


unit_registry = UnitRegistry()
default_units = get_eu_default_units()


class BaseFoodNutritionFacts(object):
    """Nutrition facts of a food item"""

    def __init__(self, **kwargs):
        self.fields = {
            attr: field
            for attr, field
            in ((attr, getattr(self, attr)) for attr in dir(self))
            if isinstance(field, NutritionFactsField)}
        for key, value in kwargs.items():
            if key in self.fields:
                self.fields[key].value = value


class NutritionFactsField(object):
    def __init__(self, unit, default=None):
        self.unit = unit
        self.value = default

    @property
    def value(self):
        if self.raw_value is None:
            return
        return self.raw_value * self.unit

    @value.setter
    def value(self, value):
        self.original_value = value
        if value is None:
            self.raw_value = None
            return
        if not isinstance(value, Quantity):
            self.raw_value = value
            return
        self.raw_value = value.to(self.unit)
        # may raise pint.pint.DimensionalityError if value provided in
        # an incompatible unit


class MacroFoodNutritionFacts(BaseFoodNutritionFacts):
    energy = NutritionFactsField(default_units["energy"])
    fat = NutritionFactsField(default_units["fat"])
    saturates = NutritionFactsField(default_units["saturates"])
    carbohydrates = NutritionFactsField(default_units["carbohydrates"])
    sugars = NutritionFactsField(default_units["sugars"])
    protein = NutritionFactsField(default_units["protein"])
    salt = NutritionFactsField(default_units["salt"])
