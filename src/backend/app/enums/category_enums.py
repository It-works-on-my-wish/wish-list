from enum import Enum

class PredefinedCategory(str, Enum):
    COSMETICS = "Cosmetics"
    CLOTHING = "Clothing"
    TECHNOLOGY = "Technology"
    KITCHEN = "Kitchen Utensils"


"""
for category in PredefinedCategory:
    print(category.name)   # COSMETICS
    print(category.value)  # Cosmetics

you can use the above code to access the enums and their values
"""
