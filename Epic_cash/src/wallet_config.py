import os
import toml


class Config:
    def __init__(self, config_path=None):
        self.config_path = config_path if os.path.isfile(str(config_path)) else None

        if self.config_path:
            self.settings = toml.load(self.config_path, _dict=dict)
            # print(self.show_config())
        else:
            pass

    def save(self, key, value, category):
        if self.config_path:
            self.settings[category][key] = value
            with open(self.config_path, 'w') as file:
                toml.dump(self.settings, file)
        else:
            print(f'No config (*.toml) file path provided')

    def show_config(self):
        if self.config_path:
            for k, v in self.settings.items():
                print(f'\n[{k}]')
                for key, val in v.items():
                    print(key, '=', val)
        else:
            print(f'No config (*.toml) file path provided')