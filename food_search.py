from utils import HtmlBuilder
import utils.api as api

# main-function
def find_food(
    include_ingredients: list[str], exclude_ingredients: list[str] = None
) -> None:
    """Uses Spoonacular API to find recipes with given ingredients.

    :param include_ingredients: A set of ingredients that should be used in the recipes
    :type include_ingredients: list[str]
    :param exclude_ingredients: A set of ingredients that the recipes must not contain, defaults to ["plums"]
    :type exclude_ingredients: list[str], optional
    """
    exclude_ingredients = (
        exclude_ingredients if exclude_ingredients is not None else ["plums"]
    )
    include_ingredients = set([i.lower() for i in include_ingredients])
    exclude_ingredients = set([i.lower() for i in exclude_ingredients])

    recipes = api.fetch_recipes(include_ingredients, exclude_ingredients)
    if not recipes:
        print("No recipes found")
        return

    print(f"Found {len(recipes)} recipes")
    print("Building HTML...")
    html_builder = HtmlBuilder()
    html_builder.save_recipes(recipes, include_ingredients)
    print("Done")


if __name__ == "__main__":
    find_food(["banana", "strawberry"], [])
