# SpotOn-Spoonacular-API

As a young entrepreneur you want to create a new startup in food and health space.
You want to create a product that would help people avoid wasting food while maintaining healthy lifestyle.

Your task is to write a program that given list of ingredients in the fridge would generate a list of meals(max 5) that can be prepared with minimal number of missing ingredients.
Each meal should be displayed with it’s name, picture, list of ingredients already present, list of missing ingredients, carbs, proteins and calories.
With each meal you want to return information about its composition and suggest what to prepare (min carbs, max proteins).

You can use `https://spoonacular.com/food-api/` or any other API.
Entrypoint of a program should be placed in a file named `food_search.py` and function executed there should have name `find_food` and as arguments take:
- list of ingredients to include (eg. `[‘tomatoes’, ‘eggs’, ‘pasta’]`)
- list of ingredients to exclude (eg. `[‘plums’]`) - by default we exclude all meals with `plums`
Names of missing products should be displayed in Polish and English, side by side- for translation you can use https://github.com/terryyin/translate-python or any other tool you find suitable.

Please store list of ingredients(already present and missing separately) and resulting meals data in a local database(SQLite) and use it instead of the API if someone wants to find meals with the same input as before.
Output of the program should be saved as HTML page named in such a scheme: `ingredient1_ingredient2_...ingredientN.html` - ingredient[1-N] are normalized(lowercase, without spaces and special characters, matching regex `[a-zA-Z0-9_-]+`) names of ingredients to be included.
Output HTML file doesn’t need to have any styling- however each recipe should be visually separated from any other.
Any dependencies should be listed in `requirements.txt` file.

## Usage instructions

### Prerequisites
All prerequisites are listed in [`requirements`](requirements.txt) file.

```bash
pip install -r requirements.txt
```

### Output folder
By default resulting HTML files are saved in output folder.
It is possible to change this behavior by modifying [`OUTPUT_FOLDER`](utils/html_builder.py#output-folder) constant in [`html_builder`](utils/html_builder.py) file.

```bash
mkdir output
```

### Running the script
The mos important function [`find_food`](food_search.py#main-function) is placed in [`food_search`](food_search.py) file.

To receive **personalized** recipes just _for your fridge_ simply run the function by providing ingredients list that are in your fridge as firs parameter and optionally what ingredients you definitely don't want to eat as second argument:

```python
in_my_fridge = ["carrot", "chicken", "onion"]
do_not_like = ["potatoes"]

find_food(in_my_fridge, do_not_like)
```

Your personalized list of recipes is saved in the HTML file ready to be displayed under the name of search ingredients connected with `_`.

