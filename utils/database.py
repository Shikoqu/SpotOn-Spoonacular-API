from functools import wraps
import sqlite3

from utils.recipe import Recipe
from utils.tools import ingredients2id


DB_FILE = "recipes.db"


class Database:
    def __init__(self, db_file: str = DB_FILE) -> None:
        self.db_file = db_file
        self.connection: sqlite3.Connection = None
        self.cursor: sqlite3.Cursor = None

    def __enter__(self) -> "Database":
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()
        self.connection.close()

    def ensure_connection(func: callable) -> callable:
        """Decorator to ensure that the database connection is open.

        :param func: The function to be decorated.
        :type func: callable
        :return: Decorated function.
        :rtype: callable
        
        This decorator checks if the `connection` attribute of the `self`
        object is `None`. If it is, it opens a connection to the database
        using the `with` statement and then calls the decorated function
        with the provided arguments and keyword arguments. If the `connection`
        attribute is not `None`, it simply calls the decorated function.
        
        The decorated function should have the first argument be an instance
        of the class that contains the `ensure_connection` method.
        
        Example usage:
        ```
        class Database:
            def __init__(self):
                self.connection = None
            @ensure_connection
            def execute_query(self, query):
                # Execute the query
                pass
        ```
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.connection is None:
                with self:
                    return func(self, *args, **kwargs)
            return func(self, *args, **kwargs)

        return wrapper

    @ensure_connection
    def create_tables(self) -> None:
        """Create the necessary tables in the database if they don't exist."""
        create_recipe_table_query = """
            CREATE TABLE IF NOT EXISTS Recipe (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                source_url TEXT NOT NULL,
                image_type TEXT NOT NULL,
                summary TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                calories_amount INTEGER NOT NULL,
                calories_unit TEXT NOT NULL,
                protein_amount INTEGER NOT NULL,
                protein_unit TEXT NOT NULL,
                carbs_amount INTEGER NOT NULL,
                carbs_unit TEXT NOT NULL
            )
        """
        create_queries_table_query = """
            CREATE TABLE IF NOT EXISTS Queries (
                query_id INTEGER PRIMARY KEY AUTOINCREMENT,
                include_ingredients TEXT NOT NULL,
                exclude_ingredients TEXT NOT NULL
            )
        """
        create_query_recipe_link_table_query = """
            CREATE TABLE IF NOT EXISTS QueryRecipeLink (
                query_id INTEGER,
                recipe_id INTEGER,
                FOREIGN KEY (query_id) REFERENCES Queries (query_id),
                FOREIGN KEY (recipe_id) REFERENCES Recipe (id),
                PRIMARY KEY (query_id, recipe_id)
            )
        """

        self.cursor.execute(create_recipe_table_query)
        self.cursor.execute(create_queries_table_query)
        self.cursor.execute(create_query_recipe_link_table_query)

    @ensure_connection
    def save_recipe(self, recipe: Recipe) -> int:
        query = """
            INSERT OR REPLACE INTO Recipe (
                id, title, source_url,
                image_type, summary, ingredients,
                calories_amount, calories_unit,
                protein_amount, protein_unit,
                carbs_amount, carbs_unit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            recipe.id,
            recipe.title,
            recipe.source_url,
            recipe.image_type,
            recipe.summary,
            ingredients2id(recipe.ingredients),
            recipe.calories["amount"],
            recipe.calories["unit"],
            recipe.protein["amount"],
            recipe.protein["unit"],
            recipe.carbs["amount"],
            recipe.carbs["unit"],
        )
        self.cursor.execute(query, parameters)
        return self.cursor.lastrowid

    @ensure_connection
    def save_query(self, include_ids: set[str], exclude_ids: set[str]) -> int:
        query = """
            INSERT INTO Queries (include_ingredients, exclude_ingredients)
            VALUES (?, ?)
        """
        parameters = (
            ingredients2id(include_ids),
            ingredients2id(exclude_ids),
        )
        self.cursor.execute(query, parameters)
        return self.cursor.lastrowid

    @ensure_connection
    def find_query_id(
        self, include_ingredients: set[str], exclude_ingredients: set[str]
    ) -> int | None:
        """Execute the query to find the query_id in the Queries table."""
        query = """
            SELECT query_id FROM Queries
            WHERE include_ingredients = ? AND exclude_ingredients = ?
        """
        parameters = (
            ingredients2id(include_ingredients),
            ingredients2id(exclude_ingredients),
        )
        self.cursor.execute(query, parameters)
        recipe_id = self.cursor.fetchone()
        return recipe_id[0] if recipe_id else None

    @ensure_connection
    def link_query_with_recipes(self, query_id: int, recipe_ids: int) -> None:
        query = """
            INSERT INTO QueryRecipeLink (query_id, recipe_id)
            VALUES (?, ?)
        """
        for recipe_id in recipe_ids:
            self.cursor.execute(query, (query_id, recipe_id))

    @ensure_connection
    def get_recipes(self, query_id: int) -> list[Recipe]:
        query = """
            SELECT r.id, r.title, r.source_url,
                r.image_type, r.summary, r.ingredients,
                r.calories_amount, r.calories_unit,
                r.protein_amount, r.protein_unit,
                r.carbs_amount, r.carbs_unit
            FROM Recipe r
            INNER JOIN QueryRecipeLink link ON r.id = link.recipe_id
            WHERE link.query_id = ?
        """
        self.cursor.execute(query, (query_id,))
        return [
            Recipe(
                id=row[0],
                title=row[1],
                source_url=row[2],
                image_type=row[3],
                summary=row[4],
                ingredients=set(row[5].replace("-", " ").split("_")),
                calories={"amount": row[6], "unit": row[7]},
                protein={"amount": row[8], "unit": row[9]},
                carbs={"amount": row[10], "unit": row[11]},
            )
            for row in self.cursor
        ]


def memoize_query(func: callable) -> callable:
    """Decorator to memoize the query and its results.

    :param func: The function to be decorated.
    :type func: callable
    :return: The decorated function.
    :rtype: callable

    The wrapped function checks if the query has already been executed by
    checking if the query with the given `include_ingredients` and
    `exclude_ingredients` exists in the database. If it does, it fetches the
    recipes from the database and returns them. Otherwise, it executes the
    query function, saves the query and its result in the database, and
    returns the result.
    
    The wrapped function takes the same arguments as the query function and
    any additional keyword arguments.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Database() as db:
            # Check if the query has already been executed
            include_ingredients, exclude_ingredients = args
            query_id = db.find_query_id(include_ingredients, exclude_ingredients)
            if query_id:
                print("fetching recipes from database")
                return db.get_recipes(query_id)

            # Execute the query
            print("fetching recipes from API")
            result = func(*args, **kwargs)
            query_id = db.save_query(include_ingredients, exclude_ingredients)

            recipe_ids = [db.save_recipe(recipe) for recipe in result]
            db.link_query_with_recipes(query_id, recipe_ids)

            return result

    return wrapper
