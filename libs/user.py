from libs.replicon_client import RepliconClient

class User:
  users = {}

  @classmethod
  def email(self, uri):
    return self.all()[uri]['email']

  @classmethod
  def title(self, uri):
    return self.all()[uri]['title']

  @classmethod
  def all(self):
    if not self.users:
      print("Loading all users with details.")

      result = RepliconClient().query('UserService1', 'GetAllUsers')

      userUri = []
      for u in result['d']:
        userUri.append(u['uri'])
      data = { 'userUri': userUri }
      result = RepliconClient().query('UserService1', 'BulkGetUserDetails', data)
      for u in result['d']:
        uri = u['uri']
        slug = u['slug']
        name = u['displayText']
        email = u['emailAddress']
        title = [c for c in u['customFieldValues'] if c['customField']['name'] == "Title"][0]['text']
        self.users[uri] = { 'email': email, 'title': title }
    return self.users
