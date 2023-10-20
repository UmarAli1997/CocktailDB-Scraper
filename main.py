import requests
import json

class CocktailDB:
    def __init__(self):
        self.url = 'https://www.thecocktaildb.com/api/json/v1/1/search.php'
        self.data = requests.Response()
        self.search_query = {}


    def __make_query(self, cocktail_name):
        self.search_query = {'s': cocktail_name}


    def make_request(self, query):
        self.__make_query(query)
        self.data = requests.get(self.url, params=self.search_query)


    def check_status_code(self) -> bool:
        # Check status code and if it is not 200 then raise an exception and return False
        if self.data.status_code != requests.codes.ok:
            self.data.raise_for_status()
            return False
        return True


    def __dump_json(self, data, file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    def __find_cocktail(self, list_of_cocktails):
        try:
            for cocktail in list_of_cocktails:
                # If the cocktail name is not in the string then take the first response as it might be the most correct
                if self.search_query['s'].capitalize() in cocktail['strDrink']:
                    cocktail_name = cocktail['strDrink'].replace(" ", "")

                    # Searching for the entry with the exact name and cleansing the data
                    if self.search_query['s'].capitalize().replace(" ", "") == cocktail_name:
                        cocktail_dict = self.__cleanse_data(cocktail)
                        return cocktail_dict

                # If the correct spelling of the search query isn't found, return the first result from the response
                else:
                    first_cocktail = list_of_cocktails[0]
                    cocktail_dict = self.__cleanse_data(first_cocktail)
                    return cocktail_dict

        # If no cocktails were in the response then raise an error
        except TypeError as e:
            print("No cocktails found. Try again.")
            return False


    def __cleanse_data(self, cocktail):
        cocktail_id = cocktail['idDrink']
        cocktail_name = cocktail['strDrink']
        cocktail_category = cocktail['strCategory']
        cocktail_alcoholic = cocktail['strAlcoholic']
        cocktail_glass = cocktail['strGlass']
        cocktail_instructions = cocktail['strInstructions']
        cocktail_thumbnail = cocktail['strDrinkThumb']
        cocktail_date_modified = cocktail['dateModified']

        # Uses list comprehension to create a list of 'strIngredients1, strIngredients2...' then iterates through the
        # ingredients from the response and stores them to a list
        cocktail_ingredients = [cocktail[ingredient] for ingredient in [f"strIngredient{i}" for i in range(1, 16)]]
        cocktail_measures = [cocktail[measure] for measure in [f"strMeasure{i}" for i in range(1, 16)]]
        
        # Dictionary comprehension to store the ingredients and their measures together
        ingredients_dict = {ingredient: measure for ingredient, measure in zip(cocktail_ingredients, cocktail_measures)}
        # Removes None key otherwise return the original dictionary
        ingredients_dict.pop(None, ingredients_dict)

        cocktail_dict = {'id': cocktail_id, \
                            'name': cocktail_name, \
                            'category': cocktail_category, \
                            'alcoholic': cocktail_alcoholic, \
                            'glass': cocktail_glass, \
                            'instructions': cocktail_instructions, \
                            'thumbnail': cocktail_thumbnail, \
                            'ingredients': ingredients_dict, \
                            'dateModified': cocktail_date_modified}
        return cocktail_dict


    def save_request_as_json(self):
        # Convert response to dictionary to parse
        list_of_cocktails = self.data.json()

        # Unpack nested list
        [list_of_cocktails] = list_of_cocktails.values()

        # Get cocktail from response data
        cocktail_dict = self.__find_cocktail(list_of_cocktails)

        if cocktail_dict == False:
            pass
        else:
            self.__dump_json(cocktail_dict, 'cocktail.json')
            print("Cocktail returned as json")


def main():
    cocktail = CocktailDB()
    print("Use Ctrl+C or type 'exit' to exit the program")

    while True:
        query = input("Search cocktail by name: ")
        if query.lower() == 'exit':
            exit()

        else:
            cocktail.make_request(query)
            if cocktail.check_status_code() == False:
                print("There has been an error with the server response")
                break

            cocktail.save_request_as_json()


if __name__ == '__main__':
    main()