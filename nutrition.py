import enum
import dataclasses
import pint

unit_registry = pint.UnitRegistry()


class NutritionFactsAttr(enum.Enum):
    energy = enum.auto()
    fat = enum.auto()
    saturates = enum.auto()
    carbohydrates = enum.auto()
    sugars = enum.auto()
    protein = enum.auto()
    phosphorous = enum.auto()
    iodine = enum.auto()
    iron = enum.auto()
    calcium = enum.auto()
    potassium = enum.auto()
    magnesium = enum.auto()
    sodium = enum.auto()
    salt = enum.auto()
    selenium = enum.auto()
    zinc = enum.auto()


DEFAULT_UNITS = {
    NutritionFactsAttr.energy: unit_registry.kJ,
    NutritionFactsAttr.fat: unit_registry.g,
    NutritionFactsAttr.saturates: unit_registry.g,
    NutritionFactsAttr.carbohydrates: unit_registry.g,
    NutritionFactsAttr.sugars: unit_registry.g,
    NutritionFactsAttr.protein: unit_registry.g,
    NutritionFactsAttr.phosphorous: unit_registry.mg,
    NutritionFactsAttr.iodine: unit_registry.μg,
    NutritionFactsAttr.iron: unit_registry.mg,
    NutritionFactsAttr.calcium: unit_registry.mg,
    NutritionFactsAttr.potassium: unit_registry.mg,
    NutritionFactsAttr.magnesium: unit_registry.mg,
    NutritionFactsAttr.sodium: unit_registry.mg,
    NutritionFactsAttr.salt: unit_registry.g,
    NutritionFactsAttr.selenium: unit_registry.μg,
    NutritionFactsAttr.zinc: unit_registry.mg,
}


@dataclasses.dataclass
class NutritionFactsField:
    """Nutrition facts attribute data of a food item"""
    attr: NutritionFactsAttr
    raw_value: float
    raw_unit: pint.Unit | None = None

    @property
    def quantity(self) -> pint.Quantity:
        default_unit = DEFAULT_UNITS[self.attr]
        return (
            (self.raw_value * self.raw_unit).to(default_unit)
            if self.raw_unit else self.raw_value * default_unit
        )
        # may raise pint.pint.DimensionalityError if value provided in
        # an incompatible unit
