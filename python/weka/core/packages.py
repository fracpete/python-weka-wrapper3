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
# Copyright (C) 2014-2024 Fracpete (pythonwekawrapper at gmail dot com)

import argparse
import json
import logging
import sys
import traceback
from datetime import datetime
from jpype import JClass
import weka.core.jvm as jvm
from weka.core.classes import JavaObject
import weka.core.classes as classes
from weka.core.version import pww_version, with_graph_support, with_plot_support


LATEST = "Latest"
""" Constant for the latest version of a package """

# logging setup
logger = logging.getLogger("weka.packages")
logger.setLevel(logging.INFO)


class Package(JavaObject):
    """
    Wrapper for the weka.core.packageManagement.Package class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the java Package instance to wrap
        :type jobject: JPype object
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
        return self.jobject.getName()

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
        return str(self.jobject.getPackageURL())

    @property
    def dependencies(self):
        """
        Returns the dependencies of the package.

        :return: the list of Dependency objects
        :rtype: list of Dependency
        """
        result = []
        for dependency in self.jobject.getDependencies():
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
            m = self.jobject.getPackageMetaData()
            self._metadata = dict()
            for k in m:
                self._metadata[k] = m[k]
        return self._metadata

    @property
    def is_installed(self):
        """
        Returns whether the package is installed.

        :return: whether installed
        :rtype: bool
        """
        return self.jobject.isInstalled()

    def install(self):
        """
        Installs the package.
        """
        return self.jobject.install()

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
        :type jobject: JPype object
        """
        self.enforce_type(jobject, "weka.core.packageManagement.PackageConstraint")
        super(PackageConstraint, self).__init__(jobject)

    def set_package(self, pkge):
        """
        Sets the package.

        :param pkge: the package
        :type pkge: Package
        """
        self.jobject.setPackage(pkge.jobject)

    def get_package(self):
        """
        Returns the package.

        :return: the package
        :rtype: Package
        """
        return Package(self.jobject.getPackage())

    def check_constraint(self, pkge=None, constr=None):
        """
        Checks the constraints.

        :param pkge: the package to check
        :type pkge: Package
        :param constr: the package constraint to check
        :type constr: PackageConstraint
        """
        if pkge is not None:
            return self.jobject.checkConstraint(pkge.jobject)
        if constr is not None:
            return self.jobject.checkConstraint(constr.jobject)
        raise Exception("Either package or package constraing must be provided!")


class Dependency(JavaObject):
    """
    Wrapper for the weka.core.packageManagement.Dependency class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the java Dependency instance to wrap
        :type jobject: JPype object
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
        return Package(self.jobject.getSource())

    @source.setter
    def source(self, pkge):
        """
        Sets the source package.

        :param pkge: the package
        :type pkge: Package
        """
        self.jobject.setSource(pkge.jobject)

    @property
    def target(self):
        """
        Returns the target package constraint.

        :return: the package constraint
        :rtype: PackageConstraint
        """
        return PackageConstraint(self.jobject.getTarget())

    @target.setter
    def target(self, constr):
        """
        Sets the target package constraint.

        :param constr: the package constraint
        :type constr: Package
        """
        self.jobject.setTarget(constr.jobject)


def establish_cache():
    """
    Establishes the package cache if necessary.
    """
    JClass("weka.core.WekaPackageManager").establishCacheIfNeeded()


def refresh_cache():
    """
    Refreshes the cache.
    """
    establish_cache()
    JClass("weka.core.WekaPackageManager").refreshCache()


def all_packages():
    """
    Returns a list of all packages.

    :return: the list of packages
    :rtype: list
    """
    establish_cache()
    result = []
    for pkge in JClass("weka.core.WekaPackageManager").getAllPackages():
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
    for pkge in JClass("weka.core.WekaPackageManager").getAvailablePackages():
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
    for pkge in JClass("weka.core.WekaPackageManager").getInstalledPackages():
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
                url = JClass("java.net.URL")(pkge)
                install_msg = JClass("weka.core.WekaPackageManager").installPackageFromURL(url)
            except:
                msg = traceback.format_exc()
        elif pkge.lower().endswith(".zip"):
            try:
                install_msg = JClass("weka.core.WekaPackageManager").installPackageFromArchive(pkge)
            except:
                msg = traceback.format_exc()
        else:
            from_repo = True
            try:
                JClass("weka.core.WekaPackageManager").installPackageFromRepository(pkge, version)
            except:
                msg = traceback.format_exc()

        if msg is not None:
            if from_repo:
                logger.error("Failed to install %s/%s:\n%s" % (pkge, version, msg))
            else:
                logger.error("Failed to install %s:\n%s" % (pkge, msg))
            success = False
            result = False
        elif (install_msg is not None) and (len(install_msg) > 0):
            logger.info("Installation message from %s:\n%s" % (pkge, install_msg))

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
                logger.info("%s/%s not installed, attempting installation..." % (pkge, version))
            if install_package(pkge, version=version):
                inst = installed_package(pkge)
                exit_required = True
                if not quiet:
                    logger.info("%s/%s successfully installed" % (pkge, inst.version))
            else:
                result = False
                logger.error("Failed to install %s/%s" % (pkge, version))
        else:
            inst = installed_package(pkge)
            all_pkg = all_package(pkge)
            install_required = False
            if (version == LATEST) and (all_pkg.version != inst.version):
                install_required = True
            if (version != LATEST) and (version != inst.version):
                install_required = True
            if install_required:
                if not quiet:
                    if version == LATEST:
                        logger.info("Latest version of %s requested (installed: %s, repository: %s), attempting upgrade" % (pkge, inst.version, all_pkg.version))
                    else:
                        logger.info("Different version of %s requested (installed: %s, requested: %s), attempting installation" % (pkge, inst.version, version))
                if install_package(pkge, version=version):
                    inst = installed_package(pkge)
                    exit_required = True
                    if not quiet:
                        logger.info("%s/%s successfully installed" % (pkge, inst.version))
                else:
                    result = False
                    logger.error("Failed to install %s/%s" % (pkge, version))
            else:
                if not quiet:
                    logger.info("%s/%s already installed, skipping installation" % (pkge, version))

    if exit_required:
        if not quiet:
            logger.info("Package(s) installed, JVM needs to be restarted")
        if stop_jvm_and_exit:
            logger.info("Stopping JVM...")
            jvm.stop()
            logger.info("Exiting...")
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

    :param names: the names of the package
    :type names: list
    """
    establish_cache()
    for name in names:
        JClass("weka.core.WekaPackageManager").uninstallPackage(name, True)


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


def is_official_package(name, version=None):
    """
    Checks whether the package is an official one.

    :param name: the name of the package to check
    :type name: str
    :param version: the specific version to check
    :type version: str
    :return: whether an official package or not
    :rtype: bool
    """
    result = False
    pkgs = all_packages()
    for pkg in pkgs:
        if pkg.name == name:
            if version is None:
                if pkg.version == version:
                    result = True
                    break
            else:
                result = True
                break
    return result


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
        logger.info("Writing to: %s" % output)
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
        logger.info("Writing to: %s" % output)
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


def _freeze_info(output_urls=False, force_urls=False):
    """
    Compiles the information for the "freeze" sub-command.

    :param output_urls: whether to output the URLs
    :type output_urls: bool
    :param force_urls: whether to always output the URLs
    :type force_urls: bool
    :return: the list of dictionaries with the package info
    :rtype: list
    """
    pkgs = installed_packages()
    result = [pkg.as_dict() for pkg in pkgs]
    for c in result:
        output = force_urls or (output_urls and not is_official_package(c["name"], c["version"]))
        if output:
            if "url" in c:
                c["url"] = "|" + c["url"]
            else:
                c["url"] = ""
        else:
            c["url"] = ""
    return result


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
    A requirements text file can be supplied as well (PKGNAME[==VERSION[|URL]]).
    """
    if (args.packages is None) and (args.requirements is None):
        raise Exception("Packages have to be either listed explicitly or provided via a text file (-r/--requirements)!")

    if args.refresh_cache:
        refresh_cache()

    for pkg in args.packages:
        version = LATEST
        if "==" in pkg:
            pkg, version = pkg.split("==")
        logger.info("Installing: %s/%s" % (pkg, version))
        success = install_package(pkg, version)
        logger.info("  installed successfully" if success else "  failed to install")

    if args.requirements is not None:
        logger.info("Processing: %s" % args.requirements)
        with open(args.requirements, "r") as fp:
            lines = fp.readlines()
        for line in lines:
            pkg = line.strip()
            if len(pkg) > 0:
                version = LATEST
                url = None
                if "==" in pkg:
                    pkg, version = pkg.split("==")
                    if "|" in version:
                        version, url = version.split("|")
                if url is None:
                    logger.info("Installing: %s/%s" % (pkg, version))
                    success = install_package(pkg, version)
                    logger.info("  installed successfully" if success else "  failed to install")
                else:
                    logger.info("Installing: %s/%s" % (pkg, url))
                    success = install_package(url)
                    logger.info("  installed successfully" if success else "  failed to install")


def _subcmd_uninstall(args):
    """
    Uninstalls one or more packages.
    """
    for pkg in args.packages:
        logger.info("Uninstalling: %s" % pkg)
        if is_installed(pkg):
            uninstall_package(pkg)
            logger.info("  uninstalled")
        else:
            logger.info("  not installed, skipping")


def _subcmd_freeze(args):
    """
    Outputs the currently installed packages in requirements.txt file format (PKGNAME==VERSION[|URL], one per line).
    Either to the specified requirements file or to stdout. The URL is only output for "unofficial" packages unless forced.
    """
    content = _freeze_info(output_urls=args.output_urls, force_urls=args.force_urls)
    _output_text(content, lambda x: "%s==%s%s" % (x["name"], x["version"], x["url"]), args.requirements)


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
    """
    Checks whether the package(s) are installed.
    """
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


def _subcmd_bootstrap(args):
    """
    Generates a python script that bootstraps pww3 and currently installed packages
    on another computer.
    """
    lines = list()

    # general info
    lines.append("# python-weka-wrapper3 - bootstrap")
    lines.append("# Generated: %s" % str(datetime.now()))
    lines.append("")

    # logging
    lines.append("# 1. configure logging")
    lines.append("import logging")
    lines.append("logging.basicConfig()")
    lines.append('logger = logging.getLogger("bootstrap")')
    lines.append("logger.setLevel(logging.INFO)")
    lines.append("")

    # pww3
    additional = list()
    if with_graph_support():
        additional.append("graphs")
    if with_plot_support():
        additional.append("plots")
    if len(additional) > 0:
        additional_modules = "[%s]" % ",".join(additional)
    else:
        additional_modules = ""
    lines.append("# 2. install python-weka-wrapper3")
    lines.append('logger.info("Installing python-weka-wrapper3...")')
    lines.append("import subprocess")
    lines.append("import sys")
    version = pww_version()
    lines.append("pkgs = [")
    lines.append('    "python-weka-wrapper3%s==%s"' % (additional_modules, version))
    lines.append("]")
    lines.append('subprocess.check_call([sys.executable, "-m", "pip", "install", " ".join(pkgs)])')
    lines.append("")

    # packages
    content = _freeze_info(output_urls=True, force_urls=args.force_urls)
    if len(content) > 0:
        lines.append("# 3. install Weka packages")
        lines.append('logger.info("Installing Weka packages...")')
        lines.append("import weka.core.jvm as jvm")
        lines.append("from weka.core.packages import install_package")
        lines.append("jvm.start(packages=True)")
        lines.append("")
        for c in content:
            lines.append("# %s" % c["name"])
            if ("url" in c) and (len(c["url"]) > 0):
                url = c["url"]
                if "|" in url:
                    _, url = url.split("|")
                lines.append('logger.info("%s/%s")' % (c["name"], url))
                lines.append('install_package("%s")' % url)
            else:
                lines.append('logger.info("%s/%s")' % (c["name"], c["version"]))
                lines.append('install_package("%s", "%s")' % (c["name"], c["version"]))
        lines.append("")
        lines.append("jvm.stop()")

    # output
    script = "\n".join(lines)
    if args.output is None:
        print(script)
    else:
        logger.info("Writing script to: %s" % args.output)
        with open(args.output, "w") as fp:
            fp.write(script)



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
    parser.add_argument("packages", nargs="*", help="the name of the package(s) to install, append '==VERSION' to pin to a specific version")
    parser.add_argument("-r", "--requirements", metavar="FILE", default=None, help="the text file with packages to install (one per line, format: PKGNAME[==VERSION[|URL]])")
    parser.add_argument("--refresh-cache", dest="refresh_cache", action="store_true", help="whether to refresh the package cache")
    parser.set_defaults(func=_subcmd_install)

    # uninstall/remove
    parser = sub_parsers.add_parser("uninstall", aliases=["remove"], help="For uninstalling one or more packages")
    parser.add_argument("packages", nargs="+", help="the name of the package(s) to uninstall")
    parser.set_defaults(func=_subcmd_uninstall)

    # freeze
    parser = sub_parsers.add_parser("freeze", help="For outputting list of installed packages")
    parser.add_argument("-r", "--requirements", metavar="FILE", default=None, help="the text file to store the package/version pairs in (one per line, format: PKGNAME[==VERSION])")
    parser.add_argument("-u", "--output_urls", action="store_true", help="whether to output the download URL for unofficial packages (appends '|URL')")
    parser.add_argument("-f", "--force_urls", action="store_true", help="forces the output of the URLs for all packages, not just unofficial ones")
    parser.set_defaults(func=_subcmd_freeze)

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

    # bootstrap
    parser = sub_parsers.add_parser("bootstrap", help="Generates Python script for recreating current pww3 environment.")
    parser.add_argument("-f", "--force_urls", action="store_true", help="forces the install from URLs, not just unofficial ones")
    parser.add_argument("-o", "--output", metavar="FILE", default=None, help="the file to store the Python script in, otherwise outputs it on stdout")
    parser.set_defaults(func=_subcmd_bootstrap)

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
