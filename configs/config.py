import os
import configparser

curr_dir = os.path.dirname(__file__)
#relative_path_config = os.path.join(curr_dir,'..','configs','config.ini')
relative_path_config = os.path.join(curr_dir,'config.ini')
path_config = os.path.realpath(relative_path_config)


conf_data = configparser.ConfigParser()
conf_data.read(path_config)


DB__DB_NAME = conf_data['DB']['DB_NAME']


if __name__ == '__main__':
    db_name = conf_data['DB']['DB_NAME']
    print(db_name)