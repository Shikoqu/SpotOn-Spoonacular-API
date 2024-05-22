import json


class Recipe:
    def __init__(
        self,
        id: int,
        title: str,
        source_url: str,
        image_type: str,
        summary: str,
        ingredients: set[str],
        calories: dict[str, int | str],
        protein: dict[str, int | str],
        carbs: dict[str, int | str],
    ) -> None:
        """
        Initialize the Recipe object.

        :param id: The ID of the recipe.
        :type id: int
        :param title: The title of the recipe.
        :type title: str
        :param source_url: The source URL of the recipe.
        :type source_url: str
        :param image_type: The type of the image.
        :type image_type: str
        :param summary: The summary of the recipe.
        :type summary: str
        :param ingredients: The set of ingredients.
        :type ingredients: set[str]
        :param calories: The dictionary of calories information (amount and unit).
        :type calories: dict[str, int | str]
        :param protein: The dictionary of protein information (amount and unit).
        :type protein: dict[str, int | str]
        :param carbs: The dictionary of carbs information (amount and unit).
        :type carbs: dict[str, int | str]
        """
        self.id = id
        self.title = title
        self.source_url = source_url
        self.image_type = image_type
        self.summary = summary
        self.ingredients = ingredients
        self.calories = calories
        self.protein = protein
        self.carbs = carbs

    @staticmethod
    def from_api(api_res: dict) -> "Recipe":
        """Returns the object from an API response

        :param api_res: api response
        :type api_res: dict
        :return: recipe object
        :rtype: Recipe
        """
        if not api_res:
            return

        id: int = api_res.get("id")
        title: str = api_res.get("title")
        source_url: str = api_res.get("sourceUrl")
        image_type: str = api_res.get("imageType")
        summary: str = api_res.get("summary")

        ingredients: set[str] = Recipe._init_ingredients(api_res)
        calories, carbs, protein = Recipe._init_nutrients(api_res)

        return Recipe(
            id,
            title,
            source_url,
            image_type,
            summary,
            ingredients,
            calories,
            protein,
            carbs,
        )

    @staticmethod
    def _init_ingredients(api_res: dict) -> set[str]:
        """Returns ingredients set from api response

        :param api_res: api response
        :type api_res: dict
        :return: set of ingredients
        :rtype: set[str]
        """
        ingredients_list = api_res.get("nutrition", {}).get("ingredients")
        if not ingredients_list:
            return set()
        return {ingredient.get("name") for ingredient in ingredients_list}

    @staticmethod
    def _init_nutrients(api_res: dict) -> tuple[dict, dict, dict]:
        """Returns calories, carbohydrates, protein

        :param api_res: api response
        :type api_res: dict
        :return: calories, carbohydrates, protein
        :rtype: tuple[dict, dict, dict]
        """
        nutrients_dict = {
            nutrient["name"].lower(): nutrient
            for nutrient in api_res.get("nutrition", {}).get("nutrients", [])
        }

        def find_nutrient(name: str) -> dict:
            """Finds and formats nutrient with a given name

            :param name: nutrient name
            :type name: str
            :return: found nutrient dictionary with only amount and unit keys
            :rtype: dict
            """
            nutrient = nutrients_dict.get(name.lower(), {})
            return (
                {
                    key: value
                    for key, value in nutrient.items()
                    if key in ["amount", "unit"]
                }
                if nutrient
                else {}
            )

        calories = find_nutrient("Calories")
        carbohydrates = find_nutrient("Carbohydrates")
        protein = find_nutrient("Protein")

        return calories, carbohydrates, protein

    def get_used_missed_unused_ingredients(
        self, include_ingredients: set[str]
    ) -> tuple[set[str], set[str], set[str]]:
        """Returns used_ingredients, missed_ingredients, unused_ingredients

        :param include_ingredients: ingredients meant to be included (from api query)
        :type include_ingredients: set[str]
        :return: used_ingredients, missed_ingredients, unused_ingredients
        :rtype: tuple[set[str], set[str], set[str]]
        """
        used_ingredients: set[str] = self.ingredients.intersection(include_ingredients)
        missed_ingredients: set[str] = self.ingredients.difference(include_ingredients)
        unused_ingredients: set[str] = include_ingredients.difference(self.ingredients)
        return used_ingredients, missed_ingredients, unused_ingredients

    def image(self, image_size: str = "636x393") -> str:
        """Returns image URL

        :param image_size: desired image size, defaults to "636x393"
        :type image_size: str, optional
        :return: image URL for the recipe
        :rtype: str
        """
        return f"https://img.spoonacular.com/recipes/{self.id}-{image_size}.{self.image_type}"

    