<h1 align="center">pokeTP</h1>

For now a bunch of useful Python scripts that query [pokeAPI](https://pokeapi.co) for certain information, displaying it simply on the console. In the future I plan to add more functionallity and even turn this project into some kind of web application.

## Scripts
- encountersLocation - lists all the encounters in a given game for a certain location, containing information about the encounter method, rate, level range and conditions
- pokemonLearnMoveSet - lists all the moves a pokemon can learn in a given game, separated by their learning method, with information about the moves type, category, power, accuracy and pp
- pokemonStats - lists the pokemon stats -- (work in progress)
- gameMetLocations - lists all the locations that have encounters in a given game, this is useful for nuzlocke challenge trackers

## Features
- Ambiguous queries - the scripts will detect ambiguous and/or incomplete location names (i.e. `viridian` can be `viridian-city` or `viridian-forest`), game names (i.e. `red` can be `red` or `firered`), letting the user select the intended input data. For pokemon with multiple forms, mega evolutions or regional variants, the script will also allow for selection of the intented entry (i.e. `vulpix` can be `vulpix` or `vulpix-alola`).
- Caching - all search queries in [pokeAPI](https://pokeapi.co) are cached, significantly improving load times for repeated or similar search queries and making sure the API is used responsibly.
- Exporting to file formats (csv, html) - (work in progress)
- Menu (GUI) - (work in progress)
- WebApp - (work in progress)

## Usage
Simply execute the `menuPokeTP` script in your terminal console:
```
python3 menuPokeTP.py
```

Additionally, you can execute each script directly, providing the required arguments separated by spaces. Executing the script without any argument (or invalid arguments) will return an error message indicating the instructions.
