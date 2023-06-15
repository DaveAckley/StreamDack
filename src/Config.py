import tomlikey as tomli

class Config:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.hash = None

    def __str__(self):
        return f"C:{self.name}"

    def __repr__(self):
        return f"[C:{self.name}:{self.path}]"

    def load(self):
        # Opening a Toml file using tomlib
        with open(self.path,"rb") as toml:
            self.hash = tomli.load(toml)

    def print(self):
        # Printing the entire fetched toml file
        print(self.hash)

    def getRequiredSection(self,name):
        assert name in self.hash, f"Unknown section {name}"
        return self.hash[name]
        
    def getOptionalSection(self,name):
        return self.hash.get(name, None)
