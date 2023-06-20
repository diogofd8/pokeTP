import os
import sys
import requests
import json
from tabulate import tabulate

##

DEBUG_MODE = True

def toggleDebugMode (debug_flag):
    global DEBUG_MODE
    DEBUG_MODE = debug_flag
    return


def debugPrint (message, debug = True):
    if (debug):
        print(message)
    return


def queryPokeAPI (url, cache = True, checkCache = True):
    # Cached directory
    api_directory = url[26:-1]   # 26 truncates 'https://pokeapi.co/api/v2/'
    if (api_directory.find('?')):
        # If a '?' is in the url, it means the query will return a partial response
        api_directory = api_directory.replace('?', '/partial').replace('offset=', '_').replace('limit=', '')
    cache_fullPath = f'pokeAPICache/{api_directory}.json'

    if (checkCache and os.path.exists(cache_fullPath)):
            with open(cache_fullPath, 'r') as cached_file:
                return json.load(cached_file)

    response = requests.get(url)
    if response.status_code != 200:
        debugPrint(f"Error: {response.status_code}", DEBUG_MODE)
        sys.exit()

    # Convert response into json
    response = response.json()

    if not cache:
        return response

    # Create directory and cache the response
    cache_directory = os.path.dirname(cache_fullPath)
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)

    with open(cache_fullPath, 'w') as file:
        json.dump(response, file, indent=4)

    return response


def selectPokemonSpecies (pokemon_query):
    pokemon_data_iterator = 0

    # Querying pokemon species to list all the possible species with the given name (region forms, etc)
    results = queryPokeAPI(f'https://pokeapi.co/api/v2/pokemon-species/{pokemon_query}/')

    variant_list = []
    for variant in results['varieties']:
        variant_list.append(variant['pokemon']['name'])

    if (len(variant_list) == 1):
        return variant_list[0]

    # This pokemon has more than one variant
    # A list of the variants should be displayed so the user can manually pick the desired one
    print(f"{pokemon_query} has more than one variant.")
    list_iterator = 0
    for variant in variant_list:
        list_iterator += 1
        print(f'\t{list_iterator})', variant)

    # Input sanity check
    while True:
        selected_variant = int(input(f"Please select the desired variant [1 - {list_iterator}]: "))

        if (selected_variant > 0 and selected_variant <= len(variant_list)):
            break
        print(f"Error: your input is outside the allowed selection, please input a number in the following interval: 0 - {list_iterator}\n")

    debugPrint(f"Selected pokémon: {variant_list[selected_variant-1]}", DEBUG_MODE)
    return variant_list[selected_variant-1]


def selectGameName (game_query):
    game_area_iterator = 0
    games_list = []

    # Collecting each game that matches the game_query onto a list
    while True:
        results = queryPokeAPI(f'https://pokeapi.co/api/v2/version?offset={game_area_iterator}&limit=20/')

        # Check if the games on the list match the game_query
        for result in results['results']:
            if (game_query in result['name']):
                games_list.append(result['name'])

        # Update the iterator according to the default pokeAPI limit (=20)
        game_area_iterator += 20

        # Aborts the search when the last batch is reached (there's no next)
        if (results['next'] is None):
            break

    if (not len(games_list)):
        debugPrint(f"Error: couldn't find a game that matches the argument: {game_query}\nAborting...", DEBUG_MODE)
        sys.exit()

    if (len(games_list) == 1):
        debugPrint(f"Game selected: {games_list[0]}", DEBUG_MODE)
        return games_list[0]

    # If the list has more than one element, the search was not conclusive
    # A list of the matches should be displayed so the user can manually pick a game
    print(f"Ambiguous game name, did you mean?")
    list_iterator = 0
    for game in games_list:
        list_iterator += 1
        print(f'\t{list_iterator})', game)

    # Input sanity check
    while True:
        selected_game = int(input(f"Please select the desired game [1 - {list_iterator}]: "))

        if (selected_game > 0 and selected_game <= len(games_list)):
            break
        print(f"Error: your input is outside the allowed selection, please input a number in the following interval: 0 - {list_iterator}\n")

    debugPrint(f"Game selected: {games_list[selected_game-1]}", DEBUG_MODE)
    return games_list[selected_game-1]


def getLocationAreasFromLocation (location_url):
    location_areas_list = []
    location_areas_iterator = 1
    location_query = queryPokeAPI(location_url)

    for location_area in location_query['areas']:
        debugPrint(f"\t{location_areas_iterator}) {location_area['name']}", DEBUG_MODE)
        location_areas_list.append(location_area['name'])
        location_areas_iterator += 1

    return location_areas_list


def checkEncountersInLocationArea (game_version, location_area_name):
    location_area_query = queryPokeAPI(f'https://pokeapi.co/api/v2/location-area/{location_area_name}/')

    for encounter in location_area_query['pokemon_encounters']:
        for encounter_version in encounter['version_details']:
            if (encounter_version['version']['name'] == game_version):
                debugPrint(f'\t\tEncounter detected in {location_area_name}', DEBUG_MODE)
                return True
    
    return False


def printTableHead (content, table_width):
    print(f'+', f'='*(table_width-2), f'+', sep='')
    print(f'|', f'{content:^{table_width-2}}', f'|', sep='')


def getTerminalWidth (discounted_chars = 2):
    return os.get_terminal_size().columns - discounted_chars

def printFramedTitle (content, new_lines = 1):
    for i in range(new_lines):
        print() # New empty line for spacing
    frame_width = getTerminalWidth()
    print(f'+', f'='*frame_width, f'+', sep='')
    print(f'|', f'{content:^{frame_width}}', f'|', sep='')
    print(f'+', f'='*frame_width, f'+', sep='')