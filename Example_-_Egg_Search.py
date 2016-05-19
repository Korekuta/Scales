import logging
import sys
from scales.dragoncave import User, DragonCave

logger = logging.getLogger("Scales")

if len(sys.argv) == 3:
  # Create game instance and load the JSON files 
  game = DragonCave()
  dragons = game.get_dragons()
  target = game.load_dragons("Targets.json")
  collection = "Rare"
  # Log the user in
  client = User()
  client.login(sys.argv[1], sys.argv[2])
  # Continue if authentication was successful
  if client.online():
    logger.info("Starting to look for " + collection + " eggs.")
    # Set up the arrays to determine which caves to look through
    locations = [ 0 ] * 7
    caves = [ 0 ] * 7
    # Determines which caves need to be searched
    for dragon in target[collection]:
      for location in dragons[dragon]["location"]: 
        locations[location] = location
    # Get sources for required caves
    for location in locations:
      if location is not 0:
        caves[location] = game.cave_search(location, client)
    # Search caves for dragons in the given collection
    for dragon in target[collection]:
      for location in dragons[dragon]["location"]:
        for egg in caves[location]:
          if dragons[dragon]["description"] in egg[1]:
            print("Found " + dragon + " (" + egg[0] + ") in " + game.cave_name(location) + ".")
    logger.info("Finished looking for " + collection + " eggs.")
    client.logout()
else:
  print("Usage:\n\n\tExample_-_Egg_Search.py Username Password")