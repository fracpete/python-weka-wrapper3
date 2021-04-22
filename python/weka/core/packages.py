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

# packages.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import sys
import traceback
import weka.core.jvm as jvm
from weka.core.classes import JavaObject
import weka.core.classes as classes


LATEST = "Latest"
""" Constant for the latest version of a package """


class Package(JavaObject):
    """
    Wrapper for the weka.core.packageManagement.Package class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the java Package instance to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.core.packageManagement.Package")
        super(Package, self).__init__(jobject)
        self._metadata = None

    @property
    def name(self):
        """
        Returns the name of the package.

        :return: the name
        :rtype: str
        """
        return javabridge.call(self.jobject, "getName", "()Ljava/lang/String;")

    @property
    def version(self):
        """
        Returns the version of the package.

        :return: the version
        :rtype: str
        """
        return self.metadata["Version"]

    @property
    def url(self):
        """
        Returns the URL of the package.

        :return: the url
        :rtype: str
        """
        return str(JavaObject(javabridge.call(self.jobject, "getPackageURL", "()Ljava/net/URL;")))

    @property
    def dependencies(self):
        """
        Returns the dependencies of the package.

        :return: the list of Dependency objects
        :rtype: list of Dependency
        """
        result = []
        dependencies = javabridge.get_collection_wrapper(
            javabridge.call(self.jobject, "getDependencies", "()Ljava/util/List;"))
        for dependency in dependencies:
            result.append(Dependency(dependency))
        return result

    @property
    def metadata(self):
        """
        Returns the meta-data.

        :return: the meta-data dictionary
        :rtype: dict
        """
        if self._metadata is None:
            map = javabridge.get_map_wrapper(javabridge.call(self.jobject, "getPackageMetaData", "()Ljava/util/Map;"))
            self._metadata = dict()
            for k in map:
                self._metadata[javabridge.get_env().get_string(k)] = map[javabridge.get_env().get_string(k)]
        return self._metadata

    @property
    def is_installed(self):
        """
        Returns whether the package is installed.

        :return: whether installed
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isInstalled", "()Z")

    def install(self):
        """
        Installs the package.
        """
        return javabridge.call(self.jobject, "install", "()V")

    def __str__(self):
        """
        Just returns name/version.

        :return: the name/version
        :rtype: str
        """
        print(self.name + "/" + self.version)


class PackageConstraint(JavaObject):
    """
    Wrapper for the weka.core.packageManagement.PackageConstraint class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the java PackageConstraint instance to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.core.packageManagement.PackageConstraint")
        super(PackageConstraint, self).__init__(jobject)

    def set_package(self, pkge):
        """
        Sets the package.

        :param pkge: the package
        :type pkge: Package
        """
        javabridge.call(self.jobject, "setPackage", "(Lweka/core/packageManagement/Package;)V", pkge.jobject)

    def get_package(self):
        """
        Returns the package.

        :return: the package
        :rtype: Package
        """
        return Package(javabridge.call(self.jobject, "getPackage", "()Lweka/core/packageManagement/Package;"))

    def check_constraint(self, pkge=None, constr=None):
        """
        Checks the constraints.

        :param pkge: the package to check
        :type pkge: Package
        :param constr: the package constraint to check
        :type constr: PackageConstraint
        """
        if not pkge is None:
            return javabridge.call(
                self.jobject, "checkConstraint", "(Lweka/core/packageManagement/Package;)Z", pkge.jobject)
        if not constr is None:
            return javabridge.call(
                self.jobject, "checkConstraint", "(Lweka/core/packageManagement/PackageConstraint;)Z", pkge.jobject)
        raise Exception("Either package or package constraing must be provided!")


class Dependency(JavaObject):
    """
    Wrapper for the weka.core.packageManagement.Dependency class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the java Dependency instance to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.core.packageManagement.Dependency")
        super(Dependency, self).__init__(jobject)

    @property
    def source(self):
        """
        Returns the source package.

        :return: the package
        :rtype: Package
        """
        return Package(
            javabridge.call(self.jobject, "getSource", "()Lweka/core/packageManagement/Package;"))

    @source.setter
    def source(self, pkge):
        """
        Sets the source package.

        :param pkge: the package
        :type pkge: Package
        """
        javabridge.call(
            self.jobject, "setSource", "(Lweka/core/packageManagement/Package;)V", pkge.jobject)

    @property
    def target(self):
        """
        Returns the target package constraint.

        :return: the package constraint
        :rtype: PackageConstraint
        """
        return PackageConstraint(
            javabridge.call(self.jobject, "getTarget", "()Lweka/core/packageManagement/PackageConstraint;"))

    @target.setter
    def target(self, constr):
        """
        Sets the target package constraint.

        :param constr: the package constraint
        :type constr: Package
        """
        javabridge.call(
            self.jobject, "setTarget", "(Lweka/core/packageManagement/PackageConstraint;)V", constr.jobject)


def establish_cache():
    """
    Establishes the package cache if necessary.
    """
    javabridge.static_call(
        "weka/core/WekaPackageManager", "establishCacheIfNeeded", "([Ljava/io/PrintStream;)Ljava/lang/Exception;", [])


def refresh_cache():
    """
    Refreshes the cache.
    """
    establish_cache()
    javabridge.static_call(
        "weka/core/WekaPackageManager", "refreshCache", "([Ljava/io/PrintStream;)Ljava/lang/Exception;", [])


def all_packages():
    """
    Returns a list of all packages.

    :return: the list of packages
    :rtype: list
    """
    establish_cache()
    result = []
    pkgs = javabridge.get_collection_wrapper(
        javabridge.static_call(
            "weka/core/WekaPackageManager", "getAllPackages", "()Ljava/util/List;"))
    for pkge in pkgs:
        result.append(Package(pkge))
    return result


def all_package(name):
    """
    Returns Package object for the specified package (either installed or available). Returns None if not found.

    :param name: the name of the package to retrieve
    :type name: str
    :return: the package information, None if not available
    :rtype: Package
    """
    pkgs = all_packages()
    for pkg in pkgs:
        if pkg.name == name:
            return pkg
    return None


def available_packages():
    """
    Returns a list of all packages that aren't installed yet.

    :return: the list of packages
    :rtype: list
    """
    establish_cache()
    result = []
    pkgs = javabridge.get_collection_wrapper(
        javabridge.static_call(
            "weka/core/WekaPackageManager", "getAvailablePackages", "()Ljava/util/List;"))
    for pkge in pkgs:
        result.append(Package(pkge))
    return result


def available_package(name):
    """
    Returns Package object for the specified, available package. Returns None if not installed.

    :param name: the name of the available package to retrieve
    :type name: str
    :return: the package information
    :rtype: Package
    """
    pkgs = available_packages()
    for pkg in pkgs:
        if pkg.name == name:
            return pkg
    return None


def installed_packages():
    """
    Returns a list of the installed packages.

    :return: the list of packages
    :rtype: list
    """
    establish_cache()
    result = []
    pkgs = javabridge.get_collection_wrapper(
        javabridge.static_call(
            "weka/core/WekaPackageManager", "getInstalledPackages", "()Ljava/util/List;"))
    for pkge in pkgs:
        result.append(Package(pkge))
    return result


def installed_package(name):
    """
    Returns Package object for the specified, installed package. Returns None if not installed.

    :param name: the name of the installed package to retrieve
    :type name: str
    :return: the package information
    :rtype: Package
    """
    pkgs = installed_packages()
    for pkg in pkgs:
        if pkg.name == name:
            return pkg
    return None


def install_package(pkge, version=LATEST):
    """
    Installs the specified package.

    :param pkge: the name of the repository package, a URL (http/https) or a zip file
    :type pkge: str
    :param version: in case of the repository packages, the version
    :type version: str
    :return: whether successfully installed
    :rtype: bool
    """
    return install_packages([(pkge, version)])


def install_packages(pkges):
    """
    Installs the specified package.

    :param pkge: the name of the repository package, a URL (http/https) or a zip file
    :type pkge: str
    :param version: in case of the repository packages, the version
    :type version: str
    :return: whether successfully installed
    :rtype: bool
    """
    result = True
    establish_cache()
    for p in pkges:
        pkge, version = p
        msg = None
        if pkge.startswith("http://") or pkge.startswith("https://"):
            try:
                url = javabridge.make_instance(
                    "java/net/URL", "(Ljava/lang/String;)V", javabridge.get_env().new_string_utf(pkge))
                msg = javabridge.static_call(
                    "weka/core/WekaPackageManager", "installPackageFromURL",
                    "(Ljava/net/URL;[Ljava/io/PrintStream;)Ljava/lang/String;", url, [])
            except:
                msg = traceback.format_exc()
        elif pkge.lower().endswith(".zip"):
            try:
                msg = javabridge.static_call(
                    "weka/core/WekaPackageManager", "installPackageFromArchive",
                    "(Ljava/lang/String;[Ljava/io/PrintStream;)Ljava/lang/String;", pkge, [])
            except:
                msg = traceback.format_exc()
        else:
            try:
                javabridge.static_call(
                    "weka/core/WekaPackageManager", "installPackageFromRepository",
                    "(Ljava/lang/String;Ljava/lang/String;[Ljava/io/PrintStream;)Z", pkge, version, [])
            except:
                msg = traceback.format_exc()

        if msg is not None:
            print("Failed to install %s/%s:\n%s" % (pkge, version, msg))
            result = False

        if not result:
            break

    return result


def install_missing_package(pkge, version=LATEST, quiet=False, stop_jvm_and_exit=False):
    """
    Installs the package if not yet installed.

    :param pkge: the name of the repository package, a URL (http/https) or a zip file
    :type pkge: str
    :param version: in case of the repository packages, the version
    :type version: str
    :param quiet: whether to suppress console output and only print error messages
    :type quiet: bool
    :param stop_jvm_and_exit: whether to stop the JVM and exit if anything was installed
    :type stop_jvm_and_exit: bool
    :return: tuple of (success, exit_required); "success" being True if either nothing to install or all successfully
             installed, False otherwise; "exit_required" being True if at least one package was installed and the
             JVM needs restarting
    :rtype: tuple
    """
    return install_missing_packages([(pkge, version)], quiet=quiet, stop_jvm_and_exit=stop_jvm_and_exit)


def install_missing_packages(pkges, quiet=False, stop_jvm_and_exit=False):
    """
    Installs the missing packages.

    :param pkges: list of tuples (packagename, version), use "Latest" or LATEST constant to grab latest version
    :type pkges: the packages to install
    :param quiet: whether to suppress console output and only print error messages
    :type quiet: bool
    :param stop_jvm_and_exit: whether to stop the JVM and exit if anything was installed
    :type stop_jvm_and_exit: bool
    :return: tuple of (success, exit_required); "success" being True if either nothing to install or all successfully
             installed, False otherwise; "exit_required" being True if at least one package was installed and the
             JVM needs restarting
    :rtype: tuple
    """
    result = True
    exit_required = False
    for p in pkges:
        pkge, version = p
        if not is_installed(pkge):
            if not quiet:
                print("%s/%s not installed, attempting installation..." % (pkge, version))
            if install_package(pkge, version=version):
                inst = installed_package(pkge)
                exit_required = True
                if not quiet:
                    print("%s/%s successfully installed" % (pkge, inst.version))
            else:
                result = False
                print("Failed to install %s/%s" % (pkge, version))
        else:
            inst = installed_package(pkge)
            all = all_package(pkge)
            install_required = False
            if (version == LATEST) and (all.version != inst.version):
                install_required = True
            if (version != LATEST) and (version != inst.version):
                install_required = True
            if install_required:
                if not quiet:
                    if version == LATEST:
                        print("Latest version of %s requested (installed: %s, repository: %s), attempting upgrade" % (pkge, inst.version, all.version))
                    else:
                        print("Different version of %s requested (installed: %s, requested: %s), attempting installation" % (pkge, inst.version, version))
                if install_package(pkge, version=version):
                    inst = installed_package(pkge)
                    exit_required = True
                    if not quiet:
                        print("%s/%s successfully installed" % (pkge, inst.version))
                else:
                    result = False
                    print("Failed to install %s/%s" % (pkge, version))
            else:
                if not quiet:
                    print("%s/%s already installed, skipping installation" % (pkge, version))

    if exit_required:
        if not quiet:
            print("Package(s) installed, JVM needs to be restarted")
        if stop_jvm_and_exit:
            print("Stopping JVM...")
            jvm.stop()
            print("Exiting...")
            sys.exit(0)

    return result, exit_required


def uninstall_package(name):
    """
    Uninstalls a package.

    :param name: the name of the package
    :type name: str
    """
    return uninstall_packages([name])


def uninstall_packages(names):
    """
    Uninstalls a package.

    :param name: the names of the package
    :type name: list
    """
    establish_cache()
    for name in names:
        javabridge.static_call(
            "weka/core/WekaPackageManager", "uninstallPackage",
            "(Ljava/lang/String;Z[Ljava/io/PrintStream;)V", name, True, [])


def is_installed(name):
    """
    Checks whether a package with the name is already installed.

    :param name: the name of the package
    :type name: str
    :return: whether the package is installed
    :rtype: bool
    """
    pkgs = installed_packages()
    for pkge in pkgs:
        if pkge.name == name:
            return True
    return False


def suggest_package(name, exact=False):
    """
    Suggests package(s) for the given name (classname, package name). Matching can be either exact or just a substring.

    :param name: the name to look for
    :type name: str
    :param exact: whether to perform exact matching or substring matching
    :type exact: bool
    :return: list of matching package names
    :rtype: list
    """

    return classes.suggest_package(name, exact)


if __name__ == "__main__":
    jvm.start()
    try:
        print("Establish cache")
        print("===============")
        establish_cache()

        print("Refresh cache")
        print("=============")
        refresh_cache()

        print("All packages")
        print("============")
        packages = all_packages()
        for pkg in packages:
            print(pkg.name)
            print("  url: " + pkg.url)
            print("")

        print("Available packages")
        print("==================")
        packages = available_packages()
        p = packages[0]
        for pkg in packages:
            print(pkg.name)
            print("  url: " + pkg.url)
            print("")

        print("Installed packages")
        print("==================")
        packages = installed_packages()
        for pkg in packages:
            print(pkg.name)
            print("  url: " + pkg.url)
            print("")
    except Exception as e:
        print(e)
    finally:
        jvm.stop()
