import sys
from tabulate import tabulate
import pokeTP_utils as utils

##

STAT_MAX_VALUE = 255
BAR_CHARACTER = '█'

class Stat:
    def __init__ (self, name, value):
        self.name = name
        self.value = value
        self.value_bar = ''

    def getName (self):
        return self.name

    def getValue (self):
        return self.value

    def setValueBar (self, total_width):
        num_characters = round(total_width * self.value / STAT_MAX_VALUE)
        # Set a minimum of 1 character to avoid empty bars
        if (num_characters == 0):
            num_characters = 1
        self.value_bar = num_characters*BAR_CHARACTER

    def getValueBar (self):
        return self.value_bar

##

def printPokemonStatsTable (pokemon_name, pokemon_stats_list, stats_width):
    table_title = f"{pokemon_name.capitalize()} stats:"
    table_entries_list = []

    for stat in pokemon_stats_list:
        stat.setValueBar(stats_width)
        table_entries_list.append([stat.getName(), stat.getValueBar(), stat.getValue()])

    # Calculate stat total and add it to the table
    stat_total = 0
    for stat in pokemon_stats_list:
        stat_total += stat.getValue()
    table_entries_list.append(['TOTAL', f'\033[30m{round(stats_width)*BAR_CHARACTER}\033[0m', stat_total])

    pokemon_stats_table = tabulate(table_entries_list, tablefmt='grid')
    table_width = len(pokemon_stats_table.split("\n")[0])
    utils.printTableHead(table_title, table_width)

    # last cell of the table should be printed black
    print(pokemon_stats_table)

##

def main (argv, argc):
    if (argc != 2):
        print(f"Invadid arguments: syntax is {{pokemon_name}}")
        sys.exit()

    pokemon_query = argv[1]

    # Querying pokemon species to list all the possible species with the given name (region forms, etc)
    pokemon_name = utils.selectPokemonSpecies(pokemon_query)

    # Parse location-area information from pokeAPI into a data frame
    queried_pokemon = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}/')

    # Store pokemon Stats
    pokemon_stats = []
    pokemon_stats.append(Stat('HP', queried_pokemon['stats'][0]['base_stat']))
    pokemon_stats.append(Stat('ATK', queried_pokemon['stats'][1]['base_stat']))
    pokemon_stats.append(Stat('DEF', queried_pokemon['stats'][2]['base_stat']))
    pokemon_stats.append(Stat('SATK', queried_pokemon['stats'][3]['base_stat']))
    pokemon_stats.append(Stat('SDEF', queried_pokemon['stats'][4]['base_stat']))
    pokemon_stats.append(Stat('SPD', queried_pokemon['stats'][5]['base_stat']))

    # Get terminal width
    terminal_width = utils.getTerminalWidth(discounted_chars=40)

    # Print the stats like in bulbapedia
    printPokemonStatsTable(pokemon_name, pokemon_stats, terminal_width/2)

    return

##

if __name__ == '__main__':
    main(sys.argv, len(sys.argv))
