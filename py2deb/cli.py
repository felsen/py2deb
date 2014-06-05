# Command line interface for the `py2deb' program.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: June 5, 2014
# URL: https://py2deb.readthedocs.org

"""
Usage: py2deb [OPTIONS] ...

Convert Python packages to Debian packages according to the given
command line options (see below). The positional arguments are the
same arguments accepted by the `pip install' command, that means you
can name the package(s) to convert on the command line but you can
also use `requirement files' if you prefer.

Supported options:

  -c, --config=FILENAME

    Load a configuration file. Because the command line arguments are processed
    in the given order, you have the choice and responsibility to decide if
    command line options override configuration file options or vice versa.
    Refer to the documentation for details on the configuration file format.

  -r, --repository=DIRECTORY

    Change the directory where *.deb archives are stored. Defaults to
    the system wide temporary directory (which is usually /tmp). If
    this directory doesn't exist py2deb refuses to run.

  --name-prefix=PREFIX

    Set the name prefix used during the name conversion from Python to
    Debian packages. Defaults to `python'. The name prefix and package
    names are always delimited by a dash.

  --no-name-prefix=PYTHON_PACKAGE_NAME

    Exclude a Python package from having the name prefix applied
    during the package name conversion. This is useful to avoid
    awkward repetitions.

  --rename=PYTHON_PACKAGE_NAME,DEBIAN_PACKAGE_NAME

    Override the package name conversion algorithm for the given pair
    of package names. Useful if you don't agree with the algorithm :-)

  --install-prefix=DIRECTORY

    Override the default system wide installation prefix. By setting
    this to anything other than `/usr' or `/usr/local' you change the
    way py2deb works. It will build packages with a file system layout
    similar to a Python virtual environment, except there will not be
    a Python executable: The packages are meant to be loaded by
    modifying Python's module search path. Refer to the documentation
    for details.

  --install-alternative=LINK,PATH

    Use Debian's `update-alternatives' system to add an executable
    that's installed in a custom installation prefix (see above) to
    the system wide executable search path. Refer to the documentation
    for details.

  -y, --yes

    Instruct pip-accel to automatically install build time
    dependencies where possible. Refer to the pip-accel
    documentation for details.

  -v, --verbose

    Make more noise :-).

  -h, --help

    Show this message and exit.
"""

# Standard library modules.
import getopt
import logging
import os
import sys

# External dependencies.
import coloredlogs
from executor import execute

# Modules included in our package.
from py2deb import PackageConverter

# Semi-standard module versioning.
__version__ = '0.1'

# Initialize a logger.
logger = logging.getLogger(__name__)

def main():
    """
    Command line interface for the ``py2deb`` program.
    """
    # Configure terminal output.
    coloredlogs.install()
    # Initialize a package converter.
    converter = PackageConverter()
    # Parse and validate the command line options.
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'c:r:yvh', [
            'config=', 'repository=', 'name-prefix=', 'no-name-prefix=',
            'rename=', 'install-prefix=', 'install-alternative=', 'yes',
            'verbose', 'help'
        ])
        for option, value in options:
            if option in ('-c', '--config'):
                converter.load_configuration(os.path.expanduser(value))
            elif option in ('-r', '--repository'):
                converter.set_repository(value)
            elif option == '--name-prefix':
                converter.set_name_prefix(value)
            elif option == '--no-name-prefix':
                converter.rename_package(value, value)
            elif option == '--rename':
                python_package_name, _, debian_package_name = value.partition(',')
                converter.rename_package(python_package_name, debian_package_name)
            elif option == '--install-prefix':
                converter.set_install_prefix(value)
            elif option == '--install-alternative':
                link, _, path = value.partition(',')
                converter.install_alternative(link, path)
            elif option in ('-y', '--yes'):
                converter.set_auto_install(True)
            elif option in ('-v', '--verbose'):
                coloredlogs.increase_verbosity()
            elif option in ('-h', '--help'):
                usage()
                return
            else:
                assert False, "Unhandled option!"
    except Exception as e:
        logger.error(e)
        logger.info("Hint: Use `py2deb --help' for instructions.")
        sys.exit(1)
    # Convert the requested package(s).
    try:
        if arguments:
            converter.convert(arguments)
        else:
            usage()
    except Exception as e:
        logger.exception("Caught an unhandled exception!")
        sys.exit(1)

def usage():
    """
    Print a usage message to standard output. Uses the ``less`` pager
    because the usage message is quite big and having the user start
    reading it from the bottom is not exactly user friendly...
    """
    lines = __doc__.strip().splitlines()
    for i, line in enumerate(lines):
        if line.startswith(('Usage:', '  -')):
            lines[i] = coloredlogs.ansi_text(line, color='green')
    execute('less', '-R', input='\n'.join(lines))

# vim: ts=4 sw=4
