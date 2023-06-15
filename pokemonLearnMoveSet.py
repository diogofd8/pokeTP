import sys
from tabulate import tabulate
import pokeTP_utils as utils

##

TypeDamageMap = {
    'normal': 'physical',
    'fighting': 'physical',
    'flying': 'physical',
    'poison': 'physical',
    'ground': 'physical',
    'rock': 'physical',
    'bug': 'physical',
    'ghost': 'physical',
    'steel': 'physical',
    'fire': 'special',
    'water': 'special',
    'grass': 'special',
    'electric': 'special',
    'psychic': 'special',
    'ice': 'special',
    'dragon': 'special',
    'dark': 'special',
    'fairy': 'null',
    'unknown': 'null',
    'shadow': 'null'
}

class Move:
    def __init__ (self, method, condition, name, movetype, category, power, accuracy, pp, machine):
        # condition is either 'TM/HM<number>' or 'Level: <number>'
        self.method = method
        self.level_up_condition = condition
        self.name = name
        self.type = movetype
        self.category = category
        self.power = power
        self.accuracy = accuracy
        self.pp = pp
        self.machine = machine

    def getMethod (self):
        return self.method

    def getLevelUpCondition (self):
        return self.level_up_condition

    def getName (self):
        return self.name

    def getType (self):
        return self.type

    def getCategory (self):
        return self.category

    def getPower (self):
        return self.power

    def getAccuracy (self):
        return self.accuracy

    def getPP (self):
        return self.pp

    def getMachine (self):
        return self.machine

##

def selectVersionGroup (version_query):
    # Queries pokeAPI version list to check the corresponding version_group which carries the learnsets
    results = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/version/{version_query}/')
    return results['version_group']['name']


def getGamesGenerationNumber (version_group):
    result = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/version-group/{version_group}/')
    version_info = {
        'generation': int(result['generation']['url'][37:-1]),    # 37 is the url cropper
        'version_group_id': result['id']
    }
    return version_info


def exportLearnMethodString (learning_method):
    MoveLearnMethod = {
        '1': 'Level-up',
        '2': 'Egg-moves',
        '3': 'Move-tutor',
        '4': 'TM/HM',
        '5': 'gtadium-surfing-pikachu',
        '6': 'gight-ball-egg',
        '7': 'colosseum-purification',
        '8': 'xd-shadow',
        '9': 'xd-purification',
        '10': 'form-change',
        '11': 'zygarde-cube'
    }
    return MoveLearnMethod[f'{learning_method}']


def getMachineFromGame (move_query, version_info):
    machine_id = ""
    for machine in move_query['machines']:
        # 40 is the url cropper
        if (version_info['version_group_id'] == int(machine['version_group']['url'][40:-1])):
            machine_id_query = utils.queryPokeAPI(machine['machine']['url'])
            machine_id = machine_id_query['item']['name']
            break

    return machine_id.upper()


def updateMovesetList (pokemon_moveset_list, move_name, learn_method, learn_condition, version_info):
    # Query pokeAPI about the move
    results = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/move/{move_name}/')

    isOldGen = False
    # Check if move characteristics have changed in previous generations
    for generation_changes in results['past_values']:
        # 40 is the url cropper
        if (int(generation_changes['version_group']['url'][40:-1]) > version_info['version_group_id']):
            isOldGen = True
            if generation_changes['type'] is not None:
                move_type = generation_changes['type']['name']
            else:
                move_type = results['type']['name']
            if generation_changes['power'] is not None:
                move_power = generation_changes['power']
            else:
                move_power = results['power']
            if generation_changes['accuracy'] is not None:
                move_accuracy = generation_changes['accuracy']
            else:
                move_accuracy = results['accuracy']
            if generation_changes['pp'] is not None:
                move_pp = generation_changes['pp']
            else:
                move_pp = results['pp']
            break

    # Unchanged characteristics should read the current gen value
    if (not isOldGen):
        move_type = results['type']['name']
        move_power = results['power']
        move_accuracy = results['accuracy']
        move_pp = results['pp']

    # Check version-group to determine damaging move class
    if ((results['damage_class']['name'] != 'status') and version_info['generation'] < 4):
        move_category = TypeDamageMap[f'{move_type}']
    else:
        move_category = results['damage_class']['name']

    # Add TM/HM info if available
    move_machine = getMachineFromGame(results, version_info)

    # Append move to moveset_list
    move_entry = Move(learn_method, learn_condition, move_name, move_type, move_category, move_power, move_accuracy, move_pp, move_machine)
    pokemon_moveset_list.append(move_entry)
    return pokemon_moveset_list


def generateMovesetList (pokemon_moveset, version_group):
    # Some moves change with the generations
    version_info = getGamesGenerationNumber(version_group)
    pokemon_moveset_list = []

    # Browsing list of moves of a given pokemon
    # Filtering the ones belonging to the version-group
    for move in pokemon_moveset:
        isMoveLearnable = False
        for version_details in move['version_group_details']:
            if (version_details['version_group']['name'] == version_group):
                isMoveLearnable = True
                #learn_method = version_details['move_learn_method']['name']
                # 44 is the url cropper
                learn_method = version_details['move_learn_method']['url'][44:-1]
                learn_condition = version_details['level_learned_at']
                move_name = move['move']['name']
                updateMovesetList(pokemon_moveset_list, move_name, learn_method, learn_condition, version_info)
                break

    # Order moveset_list by learning-method and learning-condition
    pokemon_moveset_list = sorted(pokemon_moveset_list, key=Move.getMethod, reverse=True)
    pokemon_moveset_list = sorted(pokemon_moveset_list, key=Move.getLevelUpCondition, reverse=False)
    return pokemon_moveset_list


def generateLearningMethodList ():
    method_iterator = 0
    methods_list = []

    # Collecting each location that matches the method_query onto a list
    while True:
        results = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/move-learn-method?offset={method_iterator}&limit=20/')

        # Check if the locations on the list match the method_query
        for result in results['results']:
            methods_list.append(result['url'][44:-1])   # this truncates just the method id from the url

        # Update the iterator according to the default pokeAPI limit (=20)
        method_iterator += 20

        # Aborts the search when the last batch is reached (there's no next)
        if (results['next'] is None):
            break

    return methods_list


def printLearnSetListTable (learn_method, pokemon_moveset_list, version_group):
    # For each learn_method, search for matches in the
    # pokemon_moveset_list and print them in a nice table
    table_title = f"Method: {exportLearnMethodString(learn_method)}"
    table_entries_list = [
        ["", "Move", "Type", "Category", "Power", "Accuracy", "PP"]
    ]
    if (learn_method == '1'):
        table_entries_list[0][0] = 'Level'
    elif (learn_method == '2'):
        table_entries_list[0][0] = 'Egg'
    elif (learn_method == '3'):
        table_entries_list[0][0] = 'Tutor'
    elif (learn_method == '4'):
        table_entries_list[0][0] = 'TM/HM'

    for move in pokemon_moveset_list:
        if (move.getMethod() == learn_method):
            # Patch learn_condition with the level
            if (exportLearnMethodString(learn_method) == 'Level-up'):
                table_entry = [move.getLevelUpCondition(), move.getName(), move.getType(), move.getCategory(), move.getPower(), move.getAccuracy(), move.getPP()]
            # Patch learn_condition with the TM/HM
            elif (exportLearnMethodString(learn_method) == 'TM/HM'):
                table_entry = [move.getMachine(), move.getName(), move.getType(), move.getCategory(), move.getPower(), move.getAccuracy(), move.getPP()]
            else:
                table_entry = ['', move.getName(), move.getType(), move.getCategory(), move.getPower(), move.getAccuracy(), move.getPP()]
            table_entries_list.append(table_entry)

    if (len(table_entries_list) == 1):
        return

    moveset_table = tabulate(table_entries_list, headers="firstrow", tablefmt="grid")
    table_width = len(moveset_table.split("\n")[0])
    utils.printTableHead(table_title, table_width)
    print(moveset_table)

##

def main (argv, argc):
    if (argc != 3):
        print(f"Invadid arguments: syntax is {{game_version_name}} {{pokemon_name}}")
        sys.exit()

    game_version = argv[1]
    pokemon_query = argv[2]

    # Search and select version-group in pokeAPI's version
    version_group = selectVersionGroup(game_version)

    # Search pokemon-name in pokeAPI's pokemon
    pokemon_name = utils.selectPokemonSpecies(pokemon_query)

    # Parse location-area information from pokeAPI into a data frame
    queried_pokemon = utils.queryPokeAPI(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}/')
    pokemon_moveset = queried_pokemon['moves']

    # Generate moveset_list of a given pokemon in a given version-group
    moveset_list = generateMovesetList(pokemon_moveset, version_group)

    # Display error message if encounter_list is empty
    if (not len(moveset_list)):
        print(f"This pokémon doesn't exist in pokémon", game_version)
        sys.exit()

    # Printing the results
    move_learn_method_list = generateLearningMethodList()
    for learning_method in move_learn_method_list:
        printLearnSetListTable(learning_method, moveset_list, version_group)

    return

##

if __name__ == '__main__':
    main(sys.argv, len(sys.argv))