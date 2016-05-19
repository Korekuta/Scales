import logging

print("""
                               888                   
                               888                   
                               888                   
    .d8888b   .d8888b  8888b.  888  .d88b.  .d8888b  
    88K      d88P"        "88b 888 d8P  Y8b 88K      
    "Y8888b. 888      .d888888 888 88888888 "Y8888b. 
         X88 Y88b.    888  888 888 Y8b.          X88 
     88888P'  "Y8888P "Y888888 888  "Y8888   88888P' 
                                                     
             Dragon Cave Bot Library - Version 0.2.0 
      """)

logger = logging.getLogger("Scales")
logger.setLevel(logging.INFO)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(
  logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s", 
                    "%d-%m-%Y][%H:%M:%S"))

logger.addHandler(streamHandler)
