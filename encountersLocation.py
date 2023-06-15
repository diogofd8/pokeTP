import sys
from tabulate import tabulate
import pokeTP_utils as utils

##

class Encounter:
    def __init__ (self, method, condition_list, pokemon):
        self.method = method
        self.condition_list = condition_list
        self.pokemon = pokemon
        self.min_level = 100
        self.max_level = 0
        self.rate = 0

    def getMethod (self):
        return self.method

    def getCondition (self):
        return self.condition_list

    def getPokemon (self):
        return self.pokemon

    def getRate (self):
        return self.rate

    def addToRate (self, rate):
        self.rate += rate

    def updateLevelMargin (self, min_level, max_level):
        if (min_level < self.min_level):
            self.min_level = min_level
        if (max_level > self.max_level):
            self.max_level = max_level

    def isSameEncounter (self, method, condition_list, pokemon):
        return True if (method == self.method and condition_list == self.condition_list and pokemon == self.pokemon) else False

    def exportConditionsString (self):
        conditions_str = ""
        for condition in self.condition_list:
            conditions_str += f'{condition}, '
        # removing the last ', '
        return conditions_str[:-2]

    def exportLevelRangeString (self):
        level_range_str = f'{self.min_level}-{self.max_level}'
        return level_range_str

##

def selectLocationArea (location_query):
    location_iterator = 0
    locations_list = []

    # Collecting each location that matches the location_query onto a list
    while True:
        results = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/location?offset={location_iterator}&limit=20/')

        # Check if the locations on the list match the location_query
        for location in results['results']:
            if (location_query in location['name']):
                location_entry = {
                        'name': location['name'],
                        'url': location['url']
                    }
                locations_list.append(location_entry)

        # Update the iterator according to the default pokeAPI limit (=20)
        location_iterator += 20

        # Aborts the search when the last batch is reached (there's no next)
        if (results['next'] is None):
            break

    if (not len(locations_list)):
        print(f"Error: couldn't obtain the locations list\nAborting...")
        sys.exit()

    if (len(locations_list) == 1):
        # 35 truncates just the location id from the url
        print(f"Location selected:", locations_list[0]['name'], f"({locations_list[0]['url'][35:-1]})")
        return locations_list[0]['url']

    # If the list has more than one element, the search was not conclusive
    # A list of the matches should be displayed so the user can manually pick a location
    print(f"Ambiguous location name, did you mean?")
    list_iterator = 0
    for location in locations_list:
        list_iterator += 1
        print(f'\t{list_iterator})', location['name'])

    # Input sanity check
    while True:
        selected_location = int(input(f"Please select the desired location [1 - {list_iterator}]: "))

        if (selected_location > 0 and selected_location <= len(locations_list)):
            break
        print(f"Error: your input is outside the allowed selection, please input a number in the following interval: 0 - {list_iterator}\n")

    print(f"Location selected:", locations_list[selected_location-1]['name'], f"({locations_list[selected_location-1]['url'][35:-1]})")
    return locations_list[selected_location-1]['url']


def generateMethodEncounterList ():
    # Generate encounter_method_list
    encounter_method_count = 31
    encounter_method_list = []
    for encounter_method_id in range(1, encounter_method_count):
        response = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/encounter-method/{encounter_method_id}/')
        encounter_method_list.append(response['name'])

    return encounter_method_list


def printEncounterListTable (encounter_method, encounter_list):
    # For each element of the encounter_list, search for matches in
    # the encounter_list and print them in a nice table
    table_title = f"Method: {encounter_method}"
    table_entries_list = [
        ["Pokémon", "Rate", "Levels", "Conditions"]
    ]
    for encounter in encounter_list:
        if (encounter.getMethod() == encounter_method):
            table_entry = [encounter.getPokemon(), f'{encounter.getRate()}%', encounter.exportLevelRangeString(), encounter.exportConditionsString()]
            table_entries_list.append(table_entry)

    if (len(table_entries_list) == 1):
        return

    encounters_table = tabulate(table_entries_list, headers="firstrow", tablefmt="grid")
    table_width = len(encounters_table.split("\n")[0])
    utils.printTableHead(table_title, table_width)
    print(encounters_table)


def generateGameEncounterList (location_area_encounters, game_version):
    # Initialize Encounter List
    encounter_list = []

    # pokeAPI groups encounters in a given location by the game's version_details
    for pokemon_encounter in location_area_encounters:
        version_encounters = pokemon_encounter['version_details']

        # We should only consider the encounters where the 
        # game's version name is the one we are looking for
        for encounters in version_encounters:
            if (encounters['version']['name'] == game_version):
                # A single encounter can have multiple conditions so these should be
                # stored as in list. The other parameters are unique per encounter
                for encounter in encounters['encounter_details']:
                    encounter_pokemon_name = pokemon_encounter['pokemon']['name']
                    encounter_method = encounter['method']['name']
                    encounter_conditions = []
                    for encounter_condition in encounter['condition_values']:
                        encounter_conditions.append(encounter_condition['name'])

                    # Composing the encounter_list by checking if an encounter with
                    # the same pokemon, method and conditions is already on the list
                    # pokeAPI records separate encounter entries for different pokemon
                    # levels which come with different rates, I am grouping those in the
                    # same encounter entry while updating the level margin and adding the rates
                    isItemFound = False
                    for item in encounter_list:
                        if (item.isSameEncounter(encounter_method, encounter_conditions, encounter_pokemon_name)):
                            item.addToRate(encounter['chance'])
                            item.updateLevelMargin(encounter['min_level'], encounter['max_level'])
                            isItemFound = True
                    if (not isItemFound):
                        encounter_entry = Encounter(encounter_method, encounter_conditions, encounter_pokemon_name)
                        encounter_entry.addToRate(encounter['chance'])
                        encounter_entry.updateLevelMargin(encounter['min_level'], encounter['max_level'])
                        encounter_list.append(encounter_entry)

    return encounter_list

##

def main (argv, argc):
    if (argc != 3):
        print(f"Invadid arguments: syntax is {{game_version_name}} {{location_area_query}}")
        sys.exit()

    # game_version = "white"
    # location_area_id = "unova-route-6-area"
    # game_version = "blue"
    # location_area_id = "kanto-route-1-area"
    game_version = argv[1]
    location_query = argv[2]

    # Check game_version query in pokeAPI's game list
    game_version = utils.selectGameName(game_version)

    # Search pokeAPI's location and select the one corresponding to location_query
    location_area_url = selectLocationArea(location_query)

    # Search pokeAPI's location-areas belonging to the selected location
    location_areas_list = utils.getLocationAreasFromLocation(location_area_url)

    # List encounters for each location-area in the location_areas_list
    for location_area in location_areas_list:
        # Parse location-area information from pokeAPI into a data frame
        queried_location_area = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/location-area/{location_area}/')
        location_area_encounters = queried_location_area['pokemon_encounters']

        # Generate encounter_list of a given location in a given game
        encounter_list = generateGameEncounterList(location_area_encounters, game_version)

        # Display error message if encounter_list is empty
        if (not len(encounter_list)):
            print(f"There are no encounters in {location_area} for", game_version)
            continue

        # Sorting the encounter list by rate
        encounter_list = sorted(encounter_list, key=Encounter.getRate, reverse=True)

        # Printing the results
        utils.printFramedTitle(f"Encounters in {location_area}", new_lines=1)
        encounter_method_list = generateMethodEncounterList()
        for encounter_method in encounter_method_list:
            printEncounterListTable(encounter_method, encounter_list)
    return

##

if __name__ == '__main__':
    main(sys.argv, len(sys.argv))