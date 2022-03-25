import os
import configparser as cp

class Config():
    def __init__(self, file_name='config.ini'):
        self.cp = cp.ConfigParser()
        self.file_name = file_name
        self.config(file_name)
        if os.path.isfile(file_name):
            self.cp.read(file_name)
        else:
            print("No config file has been found. Creating a blank one")
            self.cp['connection'] = {}
            self.cp['connection']['bot_token'] = ''
            self.cp['classes'] = {}
            for i in range(7, 13):
                self.cp['classes'][str(i)] = ''
            with open(file_name, 'w') as file:
                self.cp.write(file)

    @property
    def bot_token(self) -> str:
        return self.cp['connection']['bot_token']

    @property
    def classes(self) -> dict[str, str]:
        _classes = self.cp['classes']
        return _classes

    @classes.setter
    def classes(self, value : dict[str, str]):
        self.cp['classes'] = value
        with open(self.file_name, 'w') as file:
            self.cp.write(file)

    @property
    def admin_id(self) -> int:
        return int(self.cp['admin']['admin_id'])


if __name__ == '__main__':
    config = Config()
    print(config.grade_list)
