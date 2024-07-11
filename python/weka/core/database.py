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

# database.py
# Copyright (C) 2015-2024 Fracpete (pythonwekawrapper at gmail dot com)

from jpype import JClass
from weka.core.classes import OptionHandler
from weka.core.dataset import Instances


class DatabaseUtils(OptionHandler):
    """
    Wrapper class for weka.experiment.DatabaseUtils.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes a DatabaseUtils object from scratch or uses the provided JPype object.

        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = DatabaseUtils.new_instance("weka.experiment.DatabaseUtils")
        self.enforce_type(jobject, "weka.experiment.DatabaseUtils")
        super(DatabaseUtils, self).__init__(jobject=jobject, options=options)

    @property
    def db_url(self):
        """
        Obtains the currently set database URL.

        :return: the database URL
        :rtype: str
        """
        return self.jobject.getDatabaseURL()

    @db_url.setter
    def db_url(self, url):
        """
        Sets the database URL.

        :param url: the database URL
        :type url: str
        """
        self.jobject.setDatabaseURL(url)

    @property
    def user(self):
        """
        Obtains the currently set database user.

        :return: the database user
        :rtype: str
        """
        return self.jobject.getUsername()

    @user.setter
    def user(self, user):
        """
        Sets the database user.

        :param user: the database user
        :type user: str
        """
        self.jobject.setUsername(user)

    @property
    def password(self):
        """
        Obtains the currently set database password.

        :return: the database password
        :rtype: str
        """
        return self.jobject.getPassword()

    @password.setter
    def password(self, password):
        """
        Sets the database password.

        :param password: the database password
        :type password: str
        """
        self.jobject.setPassword(password)


class InstanceQuery(DatabaseUtils):
    """
    Wrapper class for weka.experiment.InstanceQuery.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes an InstanceQuery object from scratch or uses the provided JPype object.

        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = InstanceQuery.new_instance("weka.experiment.InstanceQuery")
        self.enforce_type(jobject, "weka.experiment.InstanceQuery")
        super(InstanceQuery, self).__init__(jobject=jobject, options=options)

    @property
    def custom_properties(self):
        """
        Obtains the currently set custom properties file.

        :return: the custom properties file
        :rtype: str
        """
        return str(self.jobject.getCustomPropsFile())

    @custom_properties.setter
    def custom_properties(self, props):
        """
        Sets the custom properties file to use.

        :param props: the props file
        :type props: str
        """
        fprops = JClass("java.io.File")(props)
        self.jobject.setCustomPropsFile(fprops)

    @property
    def sparse_data(self):
        """
        Obtains the whether sparse data is returned or not.

        :return: whether sparse data is generated
        :rtype: bool
        """
        return self.jobject.getSparseData()

    @sparse_data.setter
    def sparse_data(self, sparse):
        """
        Sets whether to generate sparse data.

        :param sparse: whether to generated sparse data
        :type sparse: bool
        """
        self.jobject.setSparseData(sparse)

    @property
    def query(self):
        """
        Obtains the current SQL query to execute.

        :return: the SQL query
        :rtype: str
        """
        return self.jobject.getQuery()

    @query.setter
    def query(self, query):
        """
        Sets the SQL query to execute.

        :param query: the SQL query
        :type query: str
        """
        self.jobject.setQuery(query)

    def retrieve_instances(self, query=None):
        """
        Executes either the supplied query or the one set via options (or the 'query' property).

        :param query: query to execute if not the currently set one
        :type query: str
        :return: the generated data
        :rtype: Instances
        """
        if query is None:
            data = self.jobject.retrieveInstances()
        else:
            data = self.jobject.retrieveInstances(query)
        return Instances(data)

