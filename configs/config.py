import os
import configparser

curr_dir = os.path.dirname(__file__)
#relative_path_config = os.path.join(curr_dir,'..','configs','config.ini')
relative_path_config = os.path.join(curr_dir,'config.ini')
path_config = os.path.realpath(relative_path_config)


conf_data = configparser.ConfigParser()
conf_data.read(path_config)


DB__DB_NAME = conf_data['DB']['DB_NAME']
DB__HISTORY_TABLE = conf_data['DB']['HISTORY_TABLE']
SRC__SRC_HISTORY = conf_data['SRC']['SRC_HISTORY']

#cred_path = 'E:\\'
#relative_path_credentials = os.path.join(cred_path,'credentials.ini')

relative_path_credentials = os.path.join(curr_dir,'credentials.ini')
path_credentials = os.path.realpath(relative_path_credentials)
conf_cred = configparser.ConfigParser()
conf_cred.read(path_credentials)

API_USER = None#conf_cred['CREDENTIALS']['user']
API_KEY = None#conf_cred['CREDENTIALS']['key']
API_SECRET = None#conf_cred['CREDENTIALS']['secret']

if __name__ == '__main__':
    db_name = conf_data['DB']['DB_NAME']
    print(db_name)