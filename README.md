# nutrition
python library for nutritional information 

Support for the first backend using the CC-BY 4.0-licensed
[livsmidelsdatabasen](https://www.livsmedelsverket.se/om-oss/psidata/livsmedelsdatabasen)
is implemented.
It works by downloading XML files and importing it into a local SQLite
database for faster querying.
Use Swedish food names for querying.
The main application just lists data for a food item.
More useful features to be hopefully implemented in future.

Example:

```
$ python main.py Pumpa
energy: 109.0 kJ
fat: 0.1 g
carbohydrates: 4.4 g
sugars: 2.7 g
protein: 1.0 g
phosphorous: 44.0 mg
iron: 0.8 mg
calcium: 21.0 mg
potassium: 340.0 mg
magnesium: 12.0 mg
sodium: 1.0 mg
zinc: 0.1 mg
```

It has a rudimentary search capability when no exact match was found:

```
$ python main.py Vetem
food 'Vetem' not found
Did you mean:
Bovetemjöl
Vetemjöl fullkorn grahamsmjöl
Vetemjöl bagerivetemjöl
Vetemjöl
Vetemjöl durum
Bovetemjöl grovt
```
