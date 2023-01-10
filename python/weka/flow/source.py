# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# source.py
# Copyright (C) 2015-2023 Fracpete (pythonwekawrapper at gmail dot com)


import os
from weka.core.classes import to_commandline, from_commandline
from weka.core.database import InstanceQuery
import weka.datagenerators as datagen
from simflow.source import Source, Token


class LoadDatabase(Source):
    """
    Loads a dataset from the database.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the source.

        :param name: the name of the source
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(LoadDatabase, self).__init__(name=name, config=config)
        self._loader = None
        self._iterator = None

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Loads a dataset from a database using a supplied SQL query."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "url: " + str(self.config["db_url"]) \
               + ", query: " + str(self.config["query"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        opt = "db_url"
        if opt not in options:
            options[opt] = "jdbc:mysql://somehost:3306/somedatabase"
        if opt not in self.help:
            self.help[opt] = "The JDBC database URL to connect to (str)."

        opt = "user"
        if opt not in options:
            options[opt] = "user"
        if opt not in self.help:
            self.help[opt] = "The database user to use for connecting (str)."

        opt = "password"
        if opt not in options:
            options[opt] = "secret"
        if opt not in self.help:
            self.help[opt] = "The password for the database user (str)."

        opt = "query"
        if opt not in options:
            options[opt] = "SELECT * FROM table"
        if opt not in self.help:
            self.help[opt] = "The SQL query for generating the dataset (str)."

        opt = "sparse"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to return the data in sparse format (bool)."

        opt = "custom_props"
        if opt not in options:
            options[opt] = ""
        if opt not in self.help:
            self.help[opt] = "Custom properties filename (str)."

        return super(LoadDatabase, self).fix_config(options)

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        iquery = InstanceQuery()
        iquery.db_url = str(self.resolve_option("db_url"))
        iquery.user = str(self.resolve_option("user"))
        iquery.password = str(self.resolve_option("password"))
        props = str(self.resolve_option("custom_props"))
        if (len(props) > 0) and os.path.isfile(props):
            iquery.custom_properties = props
        iquery.query = str(self.resolve_option("query"))
        data = iquery.retrieve_instances()
        self._output.append(Token(data))
        return None


class DataGenerator(Source):
    """
    Generates artificial data using the specified data generator.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the source.

        :param name: the name of the source
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(DataGenerator, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Generates artificial data using the specified data generator."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "setup: " + to_commandline(self.config["setup"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        opt = "setup"
        if opt not in options:
            options[opt] = datagen.DataGenerator(classname="weka.datagenerators.classifiers.classification.Agrawal")
        if opt not in self.help:
            self.help[opt] = "The data generator to use (DataGenerator)."

        opt = "incremental"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to output the data incrementally, in case the generator supports that (bool)."

        return super(DataGenerator, self).fix_config(options)

    def to_config(self, k, v):
        """
        Hook method that allows conversion of individual options.

        :param k: the key of the option
        :type k: str
        :param v: the value
        :type v: object
        :return: the potentially processed value
        :rtype: object
        """
        if k == "setup":
            return to_commandline(v)
        return super(DataGenerator, self).to_config(k, v)

    def from_config(self, k, v):
        """
        Hook method that allows converting values from the dictionary.

        :param k: the key in the dictionary
        :type k: str
        :param v: the value
        :type v: object
        :return: the potentially parsed value
        :rtype: object
        """
        if k == "setup":
            return from_commandline(v, classname=to_commandline(datagen.DataGenerator()))
        return super(DataGenerator, self).from_config(k, v)

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        generator = datagen.DataGenerator.make_copy(self.resolve_option("setup"))
        generator.dataset_format = generator.define_data_format()
        if bool(self.resolve_option("incremental")) and generator.single_mode_flag:
            for i in range(generator.num_examples_act):
                self._output.append(Token(generator.generate_example()))
        else:
            data = generator.generate_examples()
            self._output.append(Token(data))
        return None
