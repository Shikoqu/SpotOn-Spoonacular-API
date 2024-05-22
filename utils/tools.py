import re
from translate import Translator
from utils.recipe import Recipe


pl_translator = Translator(to_lang="pl")


def translate_to_pl(words: str | list[str]) -> str | list[str]:
    """Translates words to polish.

    :param words: words in form of a string or list of strings
    :type words: str | list[str]
    :raises ValueError: Unsupported type (support only string or list of strings)
    :return: Translated words in exact form as input
    :rtype: str | list[str]
    """
    match words:
        case str():
            return pl_translator.translate(words)
        case list():
            return translate_to_pl(",".join(words)).split(",")
        case _:
            raise ValueError(f"Unsupported type: {type(words)}")


def ingredients2id(ingredients: set[str]) -> str:
    """Generates ingredients id from ingredients.

    :param ingredients: set of ingredients
    :type ingredients: set[str]
    :return: ingredients id - alphabetically sorted, normalized ingredients names joined with "_"
    :rtype: str
    """

    def normalize(ingredient):
        return re.sub(r"[^a-zA-Z0-9_-]", "", ingredient.lower().replace(" ", "-"))

    title = "_".join(sorted([normalize(i) for i in list(ingredients)]))
    return title


def get_recommendation(recipes: list[Recipe]) -> Recipe:
    """Returns index of the best recipe in the list (min carbs, max protein).

    :param recipes: list of recipes
    :type recipes: list[Recipe]
    :return: index of the best recipe in the list
    :rtype: int
    """
    return min(recipes, key=lambda r: (r.carbs["amount"], -r.protein["amount"]))


if __name__ == "__main__":
    words = ["banana", "strawberries", "flour", "milk", "eggs", "chocolate"]
    print(translate_to_pl(words))
    sentence = "I like bananas and strawberries"
    print(translate_to_pl(sentence))
