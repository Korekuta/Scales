import logging
import sys
from scales.dragoncave import Cave, Client, Game

if len(sys.argv) == 3:
  
  logger = logging.getLogger("scales")

  # Create game instance and load the JSON files.
  game = Game()
  dragons = game.get_dragons()
  targets = game.load_json("scales/targets.json")["Example"]
  
  # Create and login on a new client object.
  client = Client()
  client.login(sys.argv[1], sys.argv[2])
  
  # Continue if authentication was successful.
  if client.online():
    logger.info("Starting to look for eggs.")
    
    # Set up the arrays to determine which caves to search.
    locations = [ None ] * 7
    caves = [ None ] * 7
    
    # Determines which caves need to be searched based on the targets' spawn(s).
    for dragon in targets:
      for location in dragons[dragon]["location"]: 
        locations[location] = location
    
    # Retrieve the egg descriptions and codes from the caves.
    for location in locations:
      if location is not None:
        caves[location] = Cave(location)
        caves[location].search(client)
        
    # Look through the eggs retrieved previously for a potential match.
    for dragon in targets:
      for location in dragons[dragon]["location"]:
        for egg in caves[location].get_eggs():
          if dragons[dragon]["description"] in egg[0]:
            logger.info("Found " + dragon + " (" + egg[1] + ") in " + caves[location].get_name() + ".")
    
    # Log out when all actions are complete.
    logger.info("Finished looking for eggs.")
    client.logout()

else:
  print("Usage:\n\n\tExample_-_Egg_Search.py Username Password")