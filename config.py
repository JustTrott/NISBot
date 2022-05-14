import os

import yaml
from yaml import Loader, Dumper

class Config():
    def __init__(self, filename='config.yaml') -> None:
        self.filename = filename
        with open(filename, 'r') as config_file:
            self.config = yaml.load(config_file, Loader=Loader)
    
    @property
    def bot_token(self) -> str:
        return os.getenv('BOT_TOKEN')

    @property
    def classes(self) -> 'dict[str, str]':
        return self.config['classes']

    @classes.setter
    def classes(self, value : 'dict[str, str]') -> None:
        self.config['classes'] = value
        with open(self.filename, 'w') as config_file:
            yaml.dump(self.config, config_file, Dumper=Dumper)

    @property
    def admin_id(self) -> int:
        return int(self.config['misc']['admin_id'])
            
if __name__ == '__main__':
    config = Config()
    print(config.admin_id)
