class Mod:

    name = ''
    link = ''
    author = ''
    desc = ''
    license = ''
    requirements = []
    incompatibilities = []
    recommended = []
    _type = ''
    unstable = False
    installer_name = ''
    versions = []

    def __init__(self, name, link, author, desc, license, reqr, incompat, recmd,
        _type, unstable, versions, instname = ''):
        self.name = name
        self.link = link
        self.author = author
        self.desc = desc
        self.license = license
        self.requirements = reqr
        self.incompatibilities = incompat
        self.recommended = recmd
        self._type = _type
        self.unstable = True if unstable == 'true' else False 
        self.installer_name = instname
        self.versions = versions
