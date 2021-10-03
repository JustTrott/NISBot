import os
import yaml
import configparser as cp

class Config():
    def __init__(self, file_name='config.ini'):
        self.cp = cp.ConfigParser()
        self.get_config(file_name)

    def get_config(self, file_name):
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
    def bot_token(self):
        return self.cp['connection']['bot_token']
    @property
    def classes(self):
        class_dict = {}
        for i in range(7, 13):
            class_dict[str(i)] = [char for char in self.cp['classes'][str(i)]]
        return class_dict


if __name__ == '__main__':
    config = Config()
    print(config.grade_list)
