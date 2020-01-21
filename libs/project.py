from libs.replicon_client import RepliconClient

class Project:
  projects = {}

  @classmethod
  def name(self, uri):
    return self.all()[uri]['name']

  @classmethod
  def code(self, uri):
    return self.all()[uri]['code']

  @classmethod
  def all(self):
    if not self.projects:
      print("Loading all projects with details.")

      data = {
        "page": "1",
        "pagesize": "10000",
        "columnUris": ["urn:replicon:project-list-column:project", "urn:replicon:project-list-column:code"]
      }
      result = RepliconClient.query('ProjectListService1', 'GetData', data)
      for u in result['d']['rows']:
        uri = u['cells'][0]['uri']
        name = u['cells'][0].get('textValue', '')
        code = u['cells'][1].get('textValue', '')
        self.projects[uri] = { 'name': name, 'code': code }
    return self.projects