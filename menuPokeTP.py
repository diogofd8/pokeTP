import sys
import pokeTP_utils as utils
import gameMetLocations as gML
import encountersLocation as eL
import pokemonStats as pS
import pokemonSearchLocation as pSL
import pokemonLearnMoveSet as pLMS

##

DEBUG_MODE = True
MAX_TITLE_WITDH = 100
DEFAULT_MENU_ENTRY_PADDING = 5
SCRIPT_LIST = ['encountersLocation', 'pokemonSearchLocation', 'gameMetLocations', 'pokemonLearnMoveSet', 'pokemonStats']

##

def printHorizontalLine (menu_size, padding, line_character):
    print(f"{' '}"*padding + f'+' + f"{line_character}"*menu_size + f'+' + f"{' '}"*padding)

def printMenuEntry (item_number, item_name, menu_size, padding):
    entry_text = f'{item_number}) {item_name}'
    text_padding = int(menu_size/8)
    entry_item = f"{' '}"*text_padding + entry_text + f"{' '}"*(menu_size-len(entry_text)-text_padding)
    print(f"{' '}"*padding + f'|' + entry_item + f'|')

def requiredInputArguments(menu_item):
    if (menu_item == 'encountersLocation'):
        return f'{{game_version}} {{location_name}}'
    if (menu_item == 'pokemonSearchLocation'):
        return f'{{game_version}} {{pokemon_species}}'
    if (menu_item == 'gameMetLocations'):
        return f'{{game_version}}'
    if (menu_item == 'pokemonLearnMoveSet'):
        return f'{{game_version}} {{pokemon_species}}'
    if (menu_item == 'pokemonStats'):
        return f'{{game_version}}'
    return f'ERROR: Menu entry not registered, contact the developer'

def processMenuEntry(menu_item, args):
    if (menu_item == 'encountersLocation'):
        return eL.main(args, len(args))
    if (menu_item == 'pokemonSearchLocation'):
        return pSL.main(args, len(args))
    if (menu_item == 'gameMetLocations'):
        return gML.main(args, len(args))
    if (menu_item == 'pokemonLearnMoveSet'):
        return pLMS.main(args, len(args))
    if (menu_item == 'pokemonStats'):
        return pS.main(args, len(args))
    return f'ERROR: Menu entry not registered, contact the developer'

##

def main ():
    # Calculate menu_width based on SCRIPT_LIST
    max_entry_length = 0
    for script in SCRIPT_LIST:
        if (len(script) > max_entry_length):
            max_entry_length = len(script)
    max_entry_length += 3 # Add 3 for the number and the parentheses
    menu_width_per = int(max_entry_length*MAX_TITLE_WITDH/utils.getTerminalWidth()+DEFAULT_MENU_ENTRY_PADDING)

    # Print the main menu
    utils.printFramedTitle(f".: pokeTP Menu :.", new_lines=1, title_width_per=menu_width_per, centered=True)

    # Padding calculation
    menu_size = int(utils.getTerminalWidth()*menu_width_per/MAX_TITLE_WITDH)
    padding = int((MAX_TITLE_WITDH-menu_width_per)/2)

    # Display script list
    script_iterator = 1
    printHorizontalLine(menu_size, padding, f'-')
    for script in SCRIPT_LIST:
        printMenuEntry(script_iterator, script, menu_size, padding)
        script_iterator += 1
    printHorizontalLine(menu_size, padding, f'-')

    
    script_iterator -= 1
    # Input sanity check
    while True:
        print()
        selected_script = int(input(f"Please select the desired script [1 - {script_iterator}]: "))

        if (selected_script > 0 and selected_script <= script_iterator):
            break
        print(f"Error: your input is outside the allowed selection, please input a number in the following interval: 0 - {script_iterator}")

    selected_item = SCRIPT_LIST[selected_script-1]
    print(f"Selected script: {selected_item}")

    # Input arguments, separated by spaces
    args = input(f"Required arguments: {requiredInputArguments(selected_item)}: ").split(' ')
    # Add the script name as the first argument
    args.insert(0, selected_item)

    # Process the menu entry
    print()
    processMenuEntry(selected_item, args)

    return

##

if __name__ == '__main__':
    main()