from utils.recipe import Recipe
from utils.tools import get_recommendation, translate_to_pl, ingredients2id


# output-folder
OUTPUT_FOLDER = "output"


class HtmlBuilder:
    def __init__(self) -> None:
        with open("templates/main.html") as f:
            self.html_str = f.read()

    def replace(self, key: str, value: str) -> None:
        """Replaces the given key with the given value in the HTML string.

        :param key: the key to replace
        :type key: str
        :param value: the value to replace the key with
        :type value: str
        """
        self.html_str = self.html_str.replace(key, value)

    def replace_nutrient(self, key: str, nutrient: dict[str : str | int]):
        """Replaces the given nutrients key with nutrient string in the HTML string.

        :param key: nutrients key
        :type key: str
        :param nutrient: nutrient dictionary containing amount and unit keys
        :type nutrient: dict[str : str | int]
        """
        nutrient_str = f"{nutrient['amount']} {nutrient['unit']}"
        self.replace(key, nutrient_str)

    def replace_ingredients(self, key: str, ingredients: list[str]) -> None:
        """Replaces the given ingredients key with ingredients embedded in HTML template in the HTML string.

        :param key: ingredients key
        :type key: str
        :param ingredients: list of ingredient strings
        :type ingredients: list[str]
        """
        translated_ingredients = translate_to_pl(ingredients)
        with open("templates/ingredient.html") as template_file:
            ingredient_template = template_file.read()
            ingredients_html = [
                ingredient_template.replace("$INGREDIENT_EN", ingredient).replace(
                    "$INGREDIENT_PL", translation
                )
                for ingredient, translation in zip(ingredients, translated_ingredients)
            ]
        self.replace(key, "\n".join(ingredients_html))

    def add_recipe(self, recipe: Recipe, included_ingredients: set[str]) -> None:
        """Adds the given recipe to the HTML string.

        Uses recipe HTML template to add the recipe to the HTML string,
        first replacing its placeholders with the appropriate values.

        :param recipe: the recipe to add
        :type recipe: Recipe
        :param included_ingredients: ingredients meant to be included in the recipe (from api query)
        :type included_ingredients: set[str]
        """
        with open("templates/recipe.html") as template_file:
            recipe_template = template_file.read()
            self.replace("$RECIPES", recipe_template)

        used_ingredients, missed_ingredients, _ = (
            recipe.get_used_missed_unused_ingredients(included_ingredients)
        )

        self.replace("$TITLE", recipe.title)
        self.replace("$SOURCE_URL", recipe.source_url)
        self.replace("$IMAGE_URL", recipe.image())
        self.replace("$SUMMARY", recipe.summary)

        self.replace_nutrient("$CALORIES", recipe.calories)
        self.replace_nutrient("$PROTEIN", recipe.protein)
        self.replace_nutrient("$CARBS", recipe.carbs)

        print(".", end="", flush=True)
        self.replace_ingredients("$USED_INGREDIENTS", list(used_ingredients))
        print(".", end="", flush=True)
        self.replace_ingredients("$MISSED_INGREDIENTS", list(missed_ingredients))
        print(".", end="", flush=True)

    def save_recipes(
        self, recipes: list[Recipe], include_ingredients: set[str]
    ) -> None:
        """Replaces the placeholder $RECIPES in the HTML string with the given recipes.

        Uses the recipe HTML template to add the recipes to the HTML string,
        first replacing its placeholders with the appropriate values.

        :param recipes: list of recipes to add to the HTML string
        :type recipes: list[Recipe]
        :param include_ingredients: ingredients meant to be included in the recipe (from api query)
        :type include_ingredients: set[str]
        """
        recommended_recipe = get_recommendation(recipes)

        self.replace("$RECOMMENDED_TITLE", recommended_recipe.title)
        self.replace("$RECOMMENDED_SOURCE_URL", recommended_recipe.source_url)

        self.replace_nutrient("$RECOMMENDED_CARBS", recommended_recipe.carbs)
        self.replace_nutrient("$RECOMMENDED_PROTEIN", recommended_recipe.protein)

        [self.add_recipe(recipe, include_ingredients) for recipe in recipes]
        self.replace("$RECIPES", "")
        print(".")

        title = ingredients2id(include_ingredients)
        print(f"Saving HTML to {OUTPUT_FOLDER}/{title}.html")
        self.save_to_file(f"{OUTPUT_FOLDER}/{title}.html")

    def save_to_file(self, file_path: str) -> None:
        """Saves the HTML string to the given file path.

        :param file_path: path to save the HTML string to
        :type file_path: str
        """
        with open(file_path, "w") as f:
            f.write(self.html_str)
