# RandTalkBot Bot matching you with a random person on Telegram.
# Copyright (C) 2016 quasiyoke
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs
import json
import logging
import os
from pathlib import Path
from .config import *


LOGGER = logging.getLogger('randtalkbot.configuration')

class ConfigurationObtainingError(Exception):
    pass



class Configuration:
    def __init__(self, path):

        try:
            with open(path,  'rb' ) as file_descriptor:
                configuration_json = json.load(file_descriptor)
        except OSError as err:
            reason = f'Troubles with opening \"{path}\"'
            LOGGER.exception(reason)
            raise ConfigurationObtainingError(reason) from err
        except ValueError as err:
            reason = f'Troubles with parsing \"{path}\"'
            LOGGER.exception(reason)
            raise ConfigurationObtainingError(reason) from err

        self.database_password = database_password
        self.token = token

        try:
            self.database_host = configuration_json['database']['host']
            self.database_name = configuration_json['database']['name']
            self.database_user = configuration_json['database']['user']

            if self.database_password is None:
                self.database_password = configuration_json['database']['password']

            self.logging = configuration_json['logging']

            if self.token is None:
                self.token = configuration_json['token']
        except (KeyError, TypeError) as err:
            reason = 'Troubles with obtaining parameters'
            LOGGER.exception(reason)
            raise ConfigurationObtainingError(reason) from err

        self.admins_telegram_ids = configuration_json.get('admins', [])
