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
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
from weka.core.classes import OptionHandler
from weka.core.dataset import Instances


class DatabaseUtils(OptionHandler):
    """
    Wrapper class for weka.experiment.DatabaseUtils.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes a DatabaseUtils object from scratch or uses the provided JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
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
        return javabridge.call(self.jobject, "getDatabaseURL", "()Ljava/lang/String;")

    @db_url.setter
    def db_url(self, url):
        """
        Sets the database URL.

        :param url: the database URL
        :type url: str
        """
        javabridge.call(self.jobject, "setDatabaseURL", "(Ljava/lang/String;)V", url)

    @property
    def user(self):
        """
        Obtains the currently set database user.

        :return: the database user
        :rtype: str
        """
        return javabridge.call(self.jobject, "getUsername", "()Ljava/lang/String;")

    @user.setter
    def user(self, user):
        """
        Sets the database user.

        :param user: the database user
        :type user: str
        """
        javabridge.call(self.jobject, "setUsername", "(Ljava/lang/String;)V", user)

    @property
    def password(self):
        """
        Obtains the currently set database password.

        :return: the database password
        :rtype: str
        """
        return javabridge.call(self.jobject, "getPassword", "()Ljava/lang/String;")

    @password.setter
    def password(self, password):
        """
        Sets the database password.

        :param password: the database password
        :type password: str
        """
        javabridge.call(self.jobject, "setPassword", "(Ljava/lang/String;)V", password)


class InstanceQuery(DatabaseUtils):
    """
    Wrapper class for weka.experiment.InstanceQuery.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes an InstanceQuery object from scratch or uses the provided JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
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
        return javabridge.to_string(javabridge.call(self.jobject, "getCustomPropsFile", "()Ljava/io/File;"))

    @custom_properties.setter
    def custom_properties(self, props):
        """
        Sets the custom properties file to use.

        :param props: the props file
        :type props: str
        """
        fprops = javabridge.make_instance("java/io/File", "(Ljava/lang/String;)V", props)
        javabridge.call(self.jobject, "setCustomPropsFile", "(Ljava/io/File;)V", fprops)

    @property
    def sparse_data(self):
        """
        Obtains the whether sparse data is returned or not.

        :return: whether sparse data is generated
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getSparseData", "()Z")

    @sparse_data.setter
    def sparse_data(self, sparse):
        """
        Sets whether to generate sparse data.

        :param sparse: whether to generated sparse data
        :type sparse: bool
        """
        javabridge.call(self.jobject, "setSparseData", "(Z)V", sparse)

    @property
    def query(self):
        """
        Obtains the current SQL query to execute.

        :return: the SQL query
        :rtype: str
        """
        return javabridge.call(self.jobject, "getQuery", "()Ljava/lang/String;")

    @query.setter
    def query(self, query):
        """
        Sets the SQL query to execute.

        :param query: the SQL query
        :type query: str
        """
        javabridge.call(self.jobject, "setQuery", "(Ljava/lang/String;)V", query)

    def retrieve_instances(self, query=None):
        """
        Executes either the supplied query or the one set via options (or the 'query' property).

        :param query: query to execute if not the currently set one
        :type query: str
        :return: the generated dataq
        :rtype: Instances
        """
        if query is None:
            data = javabridge.call(self.jobject, "retrieveInstances", "()Lweka/core/Instances;")
        else:
            data = javabridge.call(self.jobject, "retrieveInstances", "(Ljava/lang/String;)Lweka/core/Instances;")
        return Instances(data)

