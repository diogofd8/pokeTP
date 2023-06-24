import sys
from tabulate import tabulate
import pokeTP_utils as utils
import gameMetLocations as gML
import encountersLocation as eL

##

DEBUG_MODE = True

##

def removeLocationNameFromLocationAreaName (location_name, location_area_name):
    # Typical syntax is location-name-area-name, we want to remove the 'location-name-'
    area_name = location_area_name.replace(location_name, '')
    return area_name[1:]

def checkPokemonInLocation (game_version, pokemon_species, location):
    # Convert location area id to a url, to match the input of encountersLocation
    location_url = f"https://pokeapi.co/api/v2/location/{location['id']}/"
    location_encounters = []

    # Check if the pokemon is in the location_area
    pokemon_encounters = eL.encountersLocation(game_version, location_url, debug_flag=False)
    for encounter_dict in pokemon_encounters:
        for encounter in encounter_dict['encounter_list']:
            if (encounter.getPokemon() == pokemon_species):
                location_encounter_entry = {
                    'location': location['name'],
                    'location_area': removeLocationNameFromLocationAreaName(location['name'], encounter_dict['location_area']),
                    'method': encounter.getMethod(),
                    'rate': f'{encounter.getRate()}%',
                    'levels': encounter.exportLevelRangeString()
                }
                location_encounters.append(location_encounter_entry)

    return location_encounters


def listAreasWithPokemonEncounter (game_version, pokemon_species, location_list):
    location_encounter_list = []
    for location in location_list:
        #print(f'Checking {pokemon_species} in {location["name"]}')
        location_encounters = checkPokemonInLocation(game_version, pokemon_species, location)
        if (len(location_encounters) > 0):
            for location_encounter in location_encounters:
                location_encounter_list.append(location_encounter)

    return location_encounter_list


def printLocationEncountersTable (location_encounter_list):
    # Sort the list by location_area name
    location_encounter_list.sort(key=lambda x: x['location_area'])
    # Sort the list by encounter method
    location_encounter_list.sort(key=lambda x: x['method'])
    # Sort the list by location name
    location_encounter_list.sort(key=lambda x: x['location'])

    # Print the list
    print(tabulate(location_encounter_list, headers='keys', tablefmt='grid'))

    return

##

def main (argv, argc):
    if (argc != 3):
        print(f"Invadid arguments: syntax is {{game_version_name}} {{pokemon_name}}")
        sys.exit()

    # game_version = "white"
    # location_area_id = "unova-route-6-area"
    # game_version = "blue"
    # location_area_id = "kanto-route-1-area"
    game_version = argv[1]
    pokemon_name = argv[2]

    # Check game_version query in pokeAPI's game list
    game_version = utils.selectGameName(game_version)

    # Get all the location areas in the game
    location_list = gML.gameMetLocations(game_version, debug_flag=False)

    # Search pokeAPI's location and select the one corresponding to location_query
    pokemon_species = utils.selectPokemonSpecies(pokemon_name)

    # Check which location areas have encounters for the selected pokemon
    location_encounter_list = listAreasWithPokemonEncounter(game_version, pokemon_species, location_list)

    # Printing the results
    pokemon_species = pokemon_species.capitalize()
    utils.printFramedTitle(f".: {pokemon_species} encounters in {game_version} :.", new_lines=1)
    printLocationEncountersTable(location_encounter_list)

    return

##

if __name__ == '__main__':
    main(sys.argv, len(sys.argv))