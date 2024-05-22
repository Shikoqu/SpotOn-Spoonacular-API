from datetime import datetime
import json
import requests

from utils.database import Database
from utils.database import memoize_query
from utils.recipe import Recipe

API_URL = "https://api.spoonacular.com/recipes/complexSearch"
API_KEY = "c53f0fb537e74c368bbf0897dd1abc8c"


@memoize_query
def fetch_recipes(
    include_ingredients: set[str],
    exclude_ingredients: set[str],
    *,
    limit: int = 5,
    ignore_pantry: bool = False,
) -> list[Recipe]:
    """Fetches recipes from the Spoonacular API

    :param include_ingredients: A set of ingredients that should be used in the recipes.
    :type include_ingredients: set[str]
    :param exclude_ingredients: A set of ingredients that the recipes must not contain.
    :type exclude_ingredients: set[str]
    :param limit: The number of expected results (between 1 and 100), defaults to 1
    :type limit: int, optional
    :param ignore_pantry: Whether to ignore typical pantry items, such as water, salt, flour, etc., defaults to False
    :type ignore_pantry: bool, optional
    :raises Exception: Error fetching recipes
    :return: API response in form of a list of recipes-dictionaries
    :rtype: list[dict]
    """
    params = {
        "apiKey": API_KEY,
        "ignorePantry": ignore_pantry,
        "includeIngredients": ",".join(include_ingredients),
        "excludeIngredients": ",".join(exclude_ingredients),
        "addRecipeNutrition": True,
        "number": limit,
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()

        return [Recipe.from_api(recipe) for recipe in response.json()["results"]]

    except (requests.exceptions.RequestException, ValueError) as error:
        raise Exception(f"Error fetching recipes: {error}") from error


if __name__ == "__main__":
    print(fetch_recipes(["banana", "strawberries"], ["flour"]))
