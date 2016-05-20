import logging
import re
from json import load
from requests import Session
from sys import stdout

""" Game """
  
class Game(object):

  def __init__(self):
    self.logger = logging.getLogger("scales")
    self.dragons = self.load_json("scales/dragons.json")

  def get_dragons(self):
    return self.dragons
    
  def load_json(self, file):
    """ Returns a JSON object from a file loaded in. """
    dragons = None
    try:
      dragons = load(open(file))
    except Exception:
      self.logger.warn("Unable to load json (" + file + ").")    
    return dragons

""" Cave """
  
class Cave(object):

  def __init__(self, code = 0):
    self.id = 0
    self.source = None
    self.eggs = [ ]
    self.set_code(code)
  
  def set_code(self, code):
    """ Sets the id for the cave object if given a valid code. """
    if 0 < code < 7:
      self.id = code
      return True
    return False
  
  def get_code(self):
    return self.id
  
  def get_eggs(self):
    return self.eggs
  
  def get_source(self):
    return self.source
  
  def get_name(self):
    """ Returns the str name associated with the cave object's identifier. """
    if self.id == 0: return None
    if self.id == 1: return "Coast"
    if self.id == 2: return "Desert"
    if self.id == 3: return "Forest"
    if self.id == 4: return "Jungle"
    if self.id == 5: return "Alpine"
    if self.id == 6: return "Volcano"
  
  def search(self, client):
    """ Returns whether or not the cave's egg information was retrieved. """
    # Make sure the source is available in order to continue.
    if self.source is None:
      if not self.visit(client):
        return False
    # Add egg code and description to self.eggs if client is logged in.
    if client.online():
      for match in re.findall(b'<div><a href="\/get\/(.*?)"><img src="\/mystery.gif" alt="Egg"><\/a><br>(.*?)<\/div>', self.source):
        self.eggs.append([ match[1].decode("utf-8"), match[0].decode("utf-8") ])
    # Add egg description to self.eggs if client is not logged in.
    else:
      for match in re.findall(b'<img src="\/mystery.gif" alt="Egg"><\/a><br>(.*?)</div>', self.source):
        self.eggs.append([ match[0].decode("utf-8") ])
    return True
  
  def visit(self, client):
    """ Returns whether or not the source code of the cave was retrieved. """
    if self.id is not 0:
      cave = client.get_session().get("http://dragcave.net/locations/" + str(self.id))
      self.source = cave.text.encode(stdout.encoding, errors="replace")
      return True
    return False

""" Client """

class Client(object):
  
  def __init__(self):
    self.logger = logging.getLogger("scales")
    self.session = Session()
    self.username = None
  
  def get_session(self):
    return self.session
  
  def get_username(self):
    return self.username
  
  def online(self):
    return False if self.username is None else True
  
  def login(self, username, password):
    """ Returns whether or not a login attempt has succeeded. """
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
    """ Returns whether or not a user was logged out successfully. """
    if self.username is not None:
      self.session.get("http://dragcave.net/logout")
      self.logger.info("'" + self.username + "' has been logged out.")
      self.username = None
      return True
    else:
      self.logger.warn("There is no user session active to be logged out.")
      return False

""" Dragon """

class Dragon(object):

  def __init__(self, id = None):
    self.logger = logging.getLogger("scales")
    self.exists = False
    self.source = None
    if id is not None: self.set(id)
  
  def exists(self):
    return self.exists
  
  def grab(self, expression, index = 1):
    """ Returns results from regex of the dragon's source if it was found. """
    if expression.decode("utf-8").split(":")[0] in self.source:
      return re.search(expression, self.source).group(index).decode("utf-8")
    return None
  
  def set(self, id, client = Client()):
    """ Verifies a dragon based on identifier given, and grabs information. """
    dragon = client.get_session().get("http://dragcave.net/view/" + id)
    source = dragon.text.encode(stdout.encoding, errors="replace")
    if b"Clicks:" in source:
      self.exists = True
      self.id = id
      self.source = source
      self.name = self.grab(b'Dragon Cave - Viewing Dragon: (.*?)<')
      self.clicks = int(self.grab(b'Clicks:<\/b>(.*?)<').replace(",", ""))
      self.viewsAll = int(self.grab(b'Overall views: <\/span>(.*?)<').replace(",", ""))
      self.viewsUnique = int(self.grab(b'Unique views: <\/span>(.*?)<').replace(",", ""))
      self.father = self.grab(b'Father:</b><a href="\/view\/(.*?)"')
      self.gender = self.grab(b'Gender:<\/b>(.*?)<')
      self.grew = self.grab(b'Grew up on:<\/b>(.*?)<')
      self.hatched = self.grab(b'Hatched on:<\/b>(.*?)<')
      self.mother = self.grab(b'Mother:<\/b><a href="\/view\/(.*?)"')
      self.owner = self.grab(b'Owner:<\/b><a href="\/user\/(.*?)">')
      self.breed = self.grab(b'Breed:<\/b><a href="\/dragonopedia\/(.*?)">(.*?)<', 2)
      self.created = self.grab(b'Laid on:<\/b>(.*?)<')
      if self.created is None: 
        self.created = self.grab(b'Stolen on:<\/b>(.*?)<')
    else:
      self.exists = False
      self.source = None
    return self.exists
  
  def take(self, client = Client()):
    """ Returns whether or not an egg was successfully taken. """
    take = client.get_session().get("http://dragcave.net/get/" + self.id)
    source = take.text.encode(stdout.encoding, errors="replace")
    if b"<img src=\"/image/" + self.id + "/1\" alt=\"Adopt one today!\"/" in source:
      self.logger.info("You managed to grab the egg (" + self.id + ").")
      return True
    elif b"You are already overburdened " in source:
      self.logger.warn("You have already met the egg limit.")
    else:
      self.logger.warn("You were unable to grab the egg.")
    return False
  
  def click(self, client = Client()):
    """ Attempts to emulate clicking on a link to visit a dragon's page. """
    if self.exists:
      if client.online():
        client.get_session().headers.update({"referer": "http://dragcave.net/user/" + client.get_username() })
      client.get_session().get("http://dragcave.net/view/" + id)
      client.get_session().headers.update({"referer": "http://dragcave.net/view/" + id})
      client.get_session().get("http://dragcave.net/click/" + id)
      return True
    return False

""" Scroll """

class Scroll(object):
  
  def __init__(self, user = None, client = Client()):
    self.exists = False
    self.username = user
    self.pages = 0
    self.dragons = [ ]
    if user is not None:
      self.set(user, client)
  
  def exists(self):
    return self.exists
  
  def get_username(self):
    return self.username
  
  def get_dragons(self):
    return self.dragons
  
  def get_pages(self):
    return self.pages
  
  def set(self, user = None, client = Client()):
    """ Returns whether or not a scroll is visible. """
    scroll = client.get_session().get("http://dragcave.net/user/" + user)
    source = scroll.text.encode(stdout.encoding, errors="replace")
    if "You pick up the scroll labeled " in source:
      self.exists = True
      self.username = user
      self.dragons = [ ]
      self.pages = int(re.search(b'<b>Now viewing page 1 of (.*?)<\/b>', source).group(1).decode("utf-8"))
    else:
      self.exists = False
      self.username = None
      self.dragons = [ ]
      self.pages = 0
    return self.exists
  
  def view(self, client = Client()):
    """ Returns whether or not a user's list of dragons were retrieved. """
    if self.exists:
      for page in range(1, self.pages + 1):
        scroll = client.get_session().get("http://dragcave.net/user/" + self.username + "/" + str(page))
        source = scroll.text.encode(stdout.encoding, errors="replace")
        for match in re.findall(b'<a href="\/view\/(.*?)">', source):
          self.dragons.append(match[0].decode("utf-8"))
      return True
    return False