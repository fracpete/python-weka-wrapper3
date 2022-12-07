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
# Copyright (C) 2014-2022 Fracpete (pythonwekawrapper at gmail dot com)

import argparse
import javabridge
import json
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

    def as_dict(self):
        """
        Turns the package information into a dictionary. Not to be confused with 'to_dict'!

        :return: the package information as dictionary
        :rtype: dict
        """
        return {
            "name": self.name,
            "version": self.version,
            "url": self.url,
            "is_installed": self.is_installed,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }

    def __str__(self):
        """
        Just returns name/version.

        :return: the name/version
        :rtype: str
        """
        return self.name + "/" + self.version


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


def install_package(pkge, version=LATEST, details=False):
    """
    Installs the specified package.

    :param pkge: the name of the repository package, a URL (http/https) or a zip file
    :type pkge: str
    :param version: in case of the repository packages, the version
    :type version: str
    :param details: whether to just return a success/failure flag (False) or a dict with detailed information (from_repo, version, error, install_message, success)
    :type details: bool
    :return: whether successfully installed or dict with detailed information
    :rtype: bool or dict
    """
    result = install_packages([(pkge, version)], details=details)
    if details:
        return result[pkge]
    else:
        return result


def install_packages(pkges, fail_fast=True, details=False):
    """
    Installs the specified packages. When running in fail_fast mode, then the first package
    that fails to install will stop the installation process. Otherwise, all packages are attempted
    to get installed.

    The details dictionary uses the package name, url or file path as the key and stores the following
    information in a dict as value:
    - from_repo (bool): whether installed from repo or "unofficial" package (ie URL or local file)
    - version (str): the version that was attempted to be installed (if applicable)
    - error (str): any error message that was encountered
    - install_message (str): any installation message that got returned when installing from URL or zip file
    - success (bool): whether successfully installed or not

    :param pkges: the list of packages to install (name of the repository package, a URL (http/https) or a zip file), if tuple must be name/version
    :type pkges: list
    :param fail_fast: whether to quit the installation of packages with the first package that fails (True) or whether to attempt to install all packages (False)
    :type fail_fast: bool
    :param details: whether to just return a success/failure flag (False) or a dict with detailed information (per package: from_repo, version, error, install_message, success)
    :type details: bool
    :return: whether successfully installed or detailed information
    :rtype: bool or dict
    """
    result = True
    result_details = dict()
    establish_cache()
    for p in pkges:
        # get name/version
        if isinstance(p, tuple):
            pkge, version = p
        else:
            pkge = p
            version = LATEST

        msg = None
        install_msg = None
        from_repo = False
        success = True
        if pkge.startswith("http://") or pkge.startswith("https://"):
            try:
                url = javabridge.make_instance(
                    "java/net/URL", "(Ljava/lang/String;)V", javabridge.get_env().new_string_utf(pkge))
                install_msg = javabridge.static_call(
                    "weka/core/WekaPackageManager", "installPackageFromURL",
                    "(Ljava/net/URL;[Ljava/io/PrintStream;)Ljava/lang/String;", url, [])
            except:
                msg = traceback.format_exc()
        elif pkge.lower().endswith(".zip"):
            try:
                install_msg = javabridge.static_call(
                    "weka/core/WekaPackageManager", "installPackageFromArchive",
                    "(Ljava/lang/String;[Ljava/io/PrintStream;)Ljava/lang/String;", pkge, [])
            except:
                msg = traceback.format_exc()
        else:
            from_repo = True
            try:
                javabridge.static_call(
                    "weka/core/WekaPackageManager", "installPackageFromRepository",
                    "(Ljava/lang/String;Ljava/lang/String;[Ljava/io/PrintStream;)Z", pkge, version, [])
            except:
                msg = traceback.format_exc()

        if msg is not None:
            if from_repo:
                print("Failed to install %s/%s:\n%s" % (pkge, version, msg))
            else:
                print("Failed to install %s:\n%s" % (pkge, msg))
            success = False
            result = False
        elif install_msg is not None:
            print("Installation message from %s:\n%s" % (pkge, install_msg))

        result_details[pkge] = {
            "from_repo": from_repo,
            "version": version if from_repo else None,
            "error": msg,
            "install_message": install_msg,
            "success": success,
        }

        if not result and fail_fast:
            break

    if details:
        return result_details
    else:
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

    :param pkges: list of tuples (packagename, version) or strings (packagename, LATEST is assume for version), use "Latest" or LATEST constant to grab latest version
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
        # get name/version
        if isinstance(p, tuple):
            pkge, version = p
        else:
            pkge = p
            version = LATEST

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


def is_installed(name, version=None):
    """
    Checks whether a package with the name is already installed.

    :param name: the name of the package
    :type name: str
    :param version: the version to check as well, ignored if None
    :type version: str
    :return: whether the package is installed
    :rtype: bool
    """
    pkgs = installed_packages()
    for pkge in pkgs:
        if pkge.name == name:
            if version is not None:
                if pkge.version == version:
                    return True
            else:
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


def _output_text(content, format_lambda, output):
    """
    Outputs the text to the specified file or, if None, to stdout.

    :param content: the content to output
    :type content: list
    :param format_lambda: the lambda to format the list
    :param output: the file to output the content to, uses stdout if None
    :type output: str
    """
    formatted = []
    for c in content:
        formatted.append(format_lambda(c))
    if output is None:
        print("\n".join(formatted))
    else:
        with open(output, "w") as fp:
            fp.write("\n".join(formatted))


def _output_json(content, content_filter, output):
    """
    Outputs the content to the specified json file or, if None, to stdout.

    :param content: the content to output
    :type content: list
    :param content_filter: the lambda for filtering the content dictionaries, ignored if None
    :param output: the file to output the content to, uses stdout if None
    :type output: str
    """
    if content_filter is None:
        filtered = content
    else:
        filtered = [content_filter(x) for x in content]
    if output is None:
        print(json.dumps(filtered, indent=2))
    else:
        with open(output, "w") as fp:
            json.dump(filtered, fp, indent=2)


def _output_pkg_list(pkgs, args):
    """
    Outputs a package list.

    :param pkgs: the list of packages
    :type pkgs: list
    :param args: the parsed command-line arguments
    :type args: argparse.Namespace
    """
    content = [pkg.as_dict() for pkg in pkgs]
    if args.format == "text":
        _output_text(content, lambda x: "%s/%s" % (x["name"], x["version"]), args.output)
    elif args.format == "json":
        _output_json(content, lambda x: {"name": x["name"], "version": x["version"]}, args.output)


def _output_pkg_info(pkgs, args):
    """
    Outputs package information.

    :param pkgs: the list of packages
    :type pkgs: list
    :param args: the parsed command-line arguments
    :type args: argparse.Namespace
    """
    if args.format == "text":
        if args.type == "brief":
            _output_text(pkgs, lambda x: "%s/%s\n  dependencies: %s" % (x["name"], x["version"], x["dependencies"]),
                         args.output)
        elif args.type == "full":
            _output_text(pkgs, lambda x: "%s/%s\n  url: %s\n  dependencies: %s\n  metadata: %s" % (
            x["name"], x["version"], x["url"], x["dependencies"], x["metadata"]), args.output)
        else:
            raise Exception("Unhandled type: %s" % args.type)
    elif args.format == "json":
        if args.type == "brief":
            _output_json(pkgs,
                         lambda x: {"name": x["name"], "version": x["version"], "dependencies": x["dependencies"]},
                         args.output)
        elif args.type == "full":
            _output_json(pkgs, None, args.output)
        else:
            raise Exception("Unhandled type: %s" % args.type)


def _subcmd_list(args):
    """
    Lists packages (name and version).
    """
    if args.refresh_cache:
        refresh_cache()
    if args.type == "all":
        pkgs = all_packages()
    elif args.type == "installed":
        pkgs = installed_packages()
    elif args.type == "available":
        pkgs = available_packages()
    else:
        raise Exception("Unhandled list type: %s" % args.type)
    _output_pkg_list(pkgs, args)


def _subcmd_info(args):
    """
    Outputs information for packages.
    """
    if args.refresh_cache:
        refresh_cache()
    pkgs = [all_package(x).as_dict() for x in args.name]
    _output_pkg_info(pkgs, args)


def _subcmd_install(args):
    """
    Installs one or more packages. Specific versions are suffixed with "==VERSION".
    """
    for pkg in args.packages:
        version = LATEST
        if "==" in pkg:
            pkg, version = pkg.split("==")
        print("Installing: %s/%s" % (pkg, version))
        success = install_package(pkg, version)
        print("  installed successfully" if success else "  failed to install")


def _subcmd_uninstall(args):
    """
    Uninstalls one or more packages.
    """
    for pkg in args.packages:
        print("Uninstalling: %s" % pkg)
        if is_installed(pkg):
            uninstall_package(pkg)
            print("  uninstalled")
        else:
            print("  not installed, skipping")


def _subcmd_suggest(args):
    """
    Suggests packages that contain the specified classname.
    """
    suggestions = []
    for classname in args.classname:
        suggestions.extend(suggest_package(classname, exact=args.exact))
    pkgs = []
    for suggestion in suggestions:
        if suggestion is None:
            continue
        pkgs.append(all_package(suggestion))
    _output_pkg_list(pkgs, args)


def _subcmd_is_installed(args):
    content = []
    for name in args.name:
        version = None
        if "==" in name:
            name, version = name.split("==")
        installed = is_installed(name, version=version)
        if version is None:
            if installed:
                version = installed_package(name).version
            else:
                version = LATEST
        content.append({"name": name, "version": version, "installed": installed})

    if args.format == "text":
        _output_text(content, lambda x: "%s/%s: %s" % (x["name"], x["version"], str(x["installed"])), args.output)
    elif args.format == "json":
        _output_json(content, None, args.output)


def main(args=None):
    """
    Performs the specified package operation from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    main_parser = argparse.ArgumentParser(
        description='Manages Weka packages.',
        prog='pww-packages')
    sub_parsers = main_parser.add_subparsers()

    # list
    parser = sub_parsers.add_parser("list", help="For listing all/installed/available packages")
    parser.add_argument("type", nargs="?", choices=["all", "installed", "available"], default="all", help="defines what packages to list")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text", help="the output format to use")
    parser.add_argument("-o", "--output", metavar="FILE", default=None, help="the file to store the output in, uses stdout if not supplied")
    parser.add_argument("-r", "--refresh-cache", dest="refresh_cache", action="store_true", help="whether to refresh the package cache")
    parser.set_defaults(func=_subcmd_list)

    # info
    parser = sub_parsers.add_parser("info", help="Outputs information about packages")
    parser.add_argument("name", nargs="+", help="the package(s) to output the information for")
    parser.add_argument("-t", "--type", choices=["brief", "full"], default="brief", help="the type of information to output")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text", help="the output format to use")
    parser.add_argument("-o", "--output", metavar="FILE", default=None, help="the file to store the output in, uses stdout if not supplied")
    parser.add_argument("-r", "--refresh-cache", dest="refresh_cache", action="store_true", help="whether to refresh the package cache")
    parser.set_defaults(func=_subcmd_info)

    # install
    parser = sub_parsers.add_parser("install", help="For installing one or more packages")
    parser.add_argument("packages", nargs="+", help="the name of the package(s) to install, append '==VERSION' to pin to a specific version")
    parser.set_defaults(func=_subcmd_install)

    # uninstall/remove
    parser = sub_parsers.add_parser("uninstall", aliases=["remove"], help="For uninstalling one or more packages")
    parser.add_argument("packages", nargs="+", help="the name of the package(s) to uninstall")
    parser.set_defaults(func=_subcmd_uninstall)

    # suggest
    parser = sub_parsers.add_parser("suggest", help="For suggesting packages that contain the specified class")
    parser.add_argument("classname", nargs=1, help="the classname to suggest packages for")
    parser.add_argument("-e", "--exact", action="store_true", help="whether to match the name exactly or perform substring matching")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text", help="the output format to use")
    parser.add_argument("-o", "--output", metavar="FILE", default=None, help="the file to store the output in, uses stdout if not supplied")
    parser.set_defaults(func=_subcmd_suggest)

    # is-installed
    parser = sub_parsers.add_parser("is-installed", help="Checks whether a package is installed, simply outputs true/false")
    parser.add_argument("name", nargs="+", help="the name of the package to check, append '==VERSION' to pin to a specific version")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text", help="the output format to use")
    parser.add_argument("-o", "--output", metavar="FILE", default=None, help="the file to store the output in, uses stdout if not supplied")
    parser.set_defaults(func=_subcmd_is_installed)

    parsed = main_parser.parse_args(args=args)
    # no action chosen? show help
    if not hasattr(parsed, "func"):
        main_parser.print_help()
    else:
        # execute action
        jvm.start(packages=True)
        try:
            parsed.func(parsed)
        except Exception:
            print(traceback.format_exc())
        finally:
            jvm.stop()


def sys_main():
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    :rtype: int
    """

    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
