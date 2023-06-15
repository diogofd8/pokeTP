import sys
from tabulate import tabulate
import pokeTP_utils as utils

##

def listEncounterAreas (game_version):
    location_iterator = 0
    locations_list = []

    # Collecting each location that matches the location_query onto a list
    while True:
        results = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/location?offset={location_iterator}&limit=20/')

        # Check if the locations on the list match the location_query
        for location in results['results']:
            location_name = location['name']
            location_url = location['url']
            print(f'Scanning location: {location_name}')
            # Getting all the location-areas in a given location
            location_areas_list = utils.getLocationAreasFromLocation(location_url)
            for location_area in location_areas_list:
                if utils.checkEncountersInLocationArea(game_version, location_area) is True:
                    location_entry = {
                        'name': location_name,
                        'id': location_url[35:-1]  # this truncates just the location id from the url
                    }
                    locations_list.append(location_entry)
                    print(f'\tAppending {location_name}')
                    break

        # Update the iterator according to the default pokeAPI limit (=20)
        location_iterator += 20

        # Aborts the search when the last batch is reached (there's no next)
        if (results['next'] is None):
            break

    if (not len(locations_list)):
        print(f"Error: couldn't obtain the locations list\nAborting...")
        sys.exit()

    # A list of the locations should be displayed
    print(f"")
    table_contents = []
    table_title = [f'Locations with encounters in {game_version}']
    table_contents.append(table_title)
    for location in locations_list:
        table_contents.append([location['name']])

    locations_table = tabulate(table_contents, headers="firstrow", tablefmt="outline", numalign="left")
    print(locations_table)

    return locations_list

##

def main (argv, argc):
    if (argc != 2):
        print(f"Invadid arguments: syntax is {{game_version_name}}")
        sys.exit()

    # game_version = "white"
    game_version = argv[1]

    # Check game_version query in pokeAPI's game list
    game_version = utils.selectGameName(game_version)

    # List every location-area in pokeAPI with pokemon_encounters in game-version
    location_area_id = listEncounterAreas(game_version)

    return

##

if __name__ == '__main__':
    main(sys.argv, len(sys.argv))