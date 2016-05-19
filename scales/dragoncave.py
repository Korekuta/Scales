import logging
import re
from json import load
from requests import Session
from sys import stdout

""" Dragon """

class Dragon(object):

  def __init__(self, id = None):
    self.exists = False
    if id is not None: self.set(id)
    
  def set(self, id, user = None):
    """
    Defines the object based on a dragon's information retrieved from it's page.
    
    Args:
      id - The identifier of the dragon to retrieve data from.
      user - The active user session to execute the action on.
    
    Returns:
      bool - True if dragon is found, False otherwise.    
    """
    if user is None: user = User()
    dragon = user.session.get("http://dragcave.net/view/" + id)
    source = dragon.text.encode(stdout.encoding, errors="replace")
    if b"alt='Fog'/><br/>" in source:
      self.logger.warn("'" + id + "' seems to be fogged/hidden.")
    elif b"<a href='/wilderness'>Wild Egg</a>" in source:
      self.logger.warn("'" + id + "' seems to be an unclaimed egg.")
    if b"Clicks:" in source:
      self.exists = True
      self.id = id
      self.name = re.search(b'Dragon Cave - Viewing Dragon: (.*?)<', source).group(1).decode("utf-8")
      self.clicks = int(re.search(b'Clicks:<\/b>(.*?)<', source).group(1).decode("utf-8").replace(",", ""))
      self.viewsAll = int(re.search(b'Overall views: <\/span>(.*?)<', source).group(1).decode("utf-8").replace(",", "")) 
      self.viewsUnique = int(re.search(b'Unique views: <\/span>(.*?)<', source).group(1).decode("utf-8").replace(",", ""))
      if b'Children:' in source:
        self.children = [ ] # Children IDs
      if b'Father:' in source:
        self.father = re.search(b'Father:</b><a href="\/view\/(.*?)"', source).group(1).decode("utf-8")
      if b'Gender:' in source:
        self.gender = re.search(b'Gender:<\/b>(.*?)<', source).group(1).decode("utf-8")
      if b'Grew up on:' in source:
        self.grew = re.search(b'Grew up on:<\/b>(.*?)<', source).group(1).decode("utf-8")
      if b'Hatched on:' in source:
        self.hatched = re.search(b'Hatched on:<\/b>(.*?)<', source).group(1).decode("utf-8")
      if b'Mother:' in source:
        self.mother = re.search(b'Mother:<\/b><a href="\/view\/(.*?)"', source).group(1).decode("utf-8")
      if b'Owner:' in source:
        self.owner = re.search(b'Owner:<\/b><a href="\/user\/(.*?)">', source).group(1).decode("utf-8")
      if b'Laid on:' in source:
        self.created = re.search(b'Laid on:<\/b>(.*?)<', source).group(1).decode("utf-8")
      else:
        self.created = re.search(b'Stolen on:<\/b>(.*?)<', source).group(1).decode("utf-8")
      if b'<b>Breed:' in source:
        self.breed = re.search(b'Breed:</b><a href="\/dragonopedia\/(.*?)">(.*?)<', source).group(2).decode("utf-8") 
      else:
        self.breed = "Unknown"
    else:
      self.exists = False
    return self.exists
  
  def exists(self):
    """ Returns whether the code attached to the object exists or not. """
    return self.exists
  
  def take(self, user = None):
    """
    Returns whether or not an egg was successfully taken.
    
    Args:
      user - The active user session to execute the action on.
      
    Returns:
      bool - True if successful, False otherwise.
    """
    take = session.get("http://dragcave.net/get/" + self.id)
    source = take.text.encode(stdout.encoding, errors="replace")
    if b"<img src=\"/image/" + self.id + "/1\" alt=\"Adopt one today!\"/" in source:
      self.logger.info("You managed to grab the egg (" + self.id + ").")
      return True
    elif b"You are already overburdened " in source:
      self.logger.warn("You have already met the egg limit.")
      return False
    else:
      self.logger.warn("You were unable to grab the egg.")
      return False
  
  def click(self, user = None):
    """
    Attempts to emulate clicking on a link to visit a dragon's page.
    """
    if self.exists:
      if user is None: user = User()
      user.session.headers.update({"referer": "http://dragcave.net/user/" + user})
      user.session.get("http://dragcave.net/view/" + id)
      user.session.headers.update({"referer": "http://dragcave.net/view/" + id})
      user.session.get("http://dragcave.net/click/" + id)
      return True
    else:
      return False

""" User """

class User(object):
  
  def __init__(self, username = None, password = None):
    self.logger = logging.getLogger("Scales")
    self.session = Session()
    self.username = None
    if username is not None and password is not None:
      self.login(username, password)
    
  def get_session(self):
    return self.session
  
  def login(self, username, password):
    """
    Returns whether or not a login attempt has succeeded.
    
    Args:
      username - The username of the account.
      password - The password of the account.
    
    Returns:
      bool - True if successful, False otherwise.
    """
    payload = { "username":username, "password":password, "submit":"Sign+in" }
    login = self.session.post("http://dragcave.net/login", data = payload)
    source = login.text.encode(stdout.encoding, errors="replace")
    if b"<a href=\"/logout\">Log out</a>" in source:
      self.username = username
      self.logger.info("'" + username + "' has been logged in.")
      return True
    else:
      self.username = None
      self.logger.error("'" + username + "' failed to be logged in.")
      return False
    
  def logout(self):
    """
    Returns whether or not a user was logged out successfully.
    
    Returns:
      bool - True if successful, False otherwise.
    """
    if self.username is not None:
      self.session.get("http://dragcave.net/logout")
      self.logger.info("'" + self.username + "' has been logged out.")
      self.username = None
      return True
    else:
      self.logger.warn("There is no user session active to be logged out.")
      return False
  
  def online(self):
    """ Returns whether or not the user is logged in. """
    if self.username is not None:
      return True
    return False

""" Scroll """

class Scroll(object):
  
  def __init__(self):
    return
    
  def exists(self, user, session = Session()):
    """ Returns whether or not a scroll is visible. """
    scroll = session.get("http://dragcave.net/user/" + user)
    source = scroll.text.encode(stdout.encoding, errors="replace")
    if "You pick up the scroll labeled " in source:
      return True
    else:
      return False
  
  def view(self, user, page, session = Session()):
    """ Returns a scroll's source if it exists. """
    if self.exists(user):
      scroll = session.get("http://dragcave.net/user/" + user + "/" + str(page))
      source = scroll.text.encode(stdout.encoding, errors="replace")
      return source
    else:
      return None

""" DragonCave """

class DragonCave(object):

  def __init__(self, file = "scales/Dragons.json"):
    self.logger = logging.getLogger("Scales")
    self.dragons = self.load_dragons(file)

  def get_dragons(self):
    return self.dragons
    
  def load_dragons(self, file):
    """
    Returns a JSON object of dragons that were loaded in successfully.
    
    Args:
      file - The file that contains the JSON of relevant dragon data.
    
    Returns:
      object - Data from the loaded in JSON file.
    """
    dragons = None
    try:
      dragons = load(open(file))
    except Exception:
      dragons = None
      self.logger.warn("Unable to load list of dragons (" + file + ").")    
    return dragons
  
  def cave_code(self, name):
    """ Returns the int identifier associated with an existing cave's name. """
    if name == "All": return 0
    if name == "Coast": return 1
    if name == "Desert": return 2
    if name == "Forest": return 3
    if name == "Jungle": return 4
    if name == "Alpine": return 5
    if name == "Volcano": return 6
    return None
  
  def cave_name(self, code):
    """ Returns the str name associated with an existing cave's identifier. """
    if code == 0: return "All"
    if code == 1: return "Coast"
    if code == 2: return "Desert"
    if code == 3: return "Forest"
    if code == 4: return "Jungle"
    if code == 5: return "Alpine"
    if code == 6: return "Volcano"
    return None
  
  def cave_search(self, code, user = User()):
    """
    Returns the dragons that are at the specified cave.
    
    Args:
      code - The code of the cave that is being searched.
      user - The session to perform the search on.
      
    Returns:
      array - Dragon breeds (and ids if online) if there are any matches.
    """
    source = self.cave_visit(code, user.get_session())
    eggs = [ ]
    if user.online():
      for match in re.findall(b'<div><a href="\/get\/(.*?)"><img src="\/mystery.gif" alt="Egg"><\/a><br>(.*?)<\/div>', source):
        eggs.append([ match[0].decode("utf-8"), match[1].decode("utf-8") ])
    else:
      for match in re.findall(b'<img src="\/mystery.gif" alt="Egg"><\/a><br>(.*?)</div>', source):
        eggs.append([ match[0].decode("utf-8") ])
    return eggs
  
  def cave_visit(self, code, session = Session()):
    """ Returns the source code of the cave, if it exists. """
    if code > 0 and code < 7:
      cave = session.get("http://dragcave.net/locations/" + str(code))
      source = cave.text.encode(stdout.encoding, errors="replace")
      return source
    return None