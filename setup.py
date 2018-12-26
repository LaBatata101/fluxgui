#!/usr/bin/env python3

from distutils.core import setup
from distutils.command.install import install
import os, subprocess, shutil, sys

class CustomInstall(install):

    def run(self):
        gschema_dir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))), 'fluxgui')

        # check if --user option is passed and install gschema file
        # accordingly
        if sys.argv[2] == '--user':
            print("Compiling gschema file...")
            subprocess.call(['glib-compile-schemas', gschema_dir])
        else:
            gschema_dir_global = '/usr/share/glib-2.0/schemas'
            gschema_file = gschema_dir + '/apps.fluxgui.gschema.xml'

            shutil.copy2(gschema_file, gschema_dir_global)
            print("Compiling gschema file...")
            subprocess.call(['glib-compile-schemas', gschema_dir_global])

        super().run()


data_files = [
    ('share/icons/hicolor/16x16/apps', ['icons/hicolor/16x16/apps/fluxgui.svg']),
    ('share/icons/hicolor/22x22/apps', ['icons/hicolor/22x22/apps/fluxgui.svg']),
    ('share/icons/hicolor/24x24/apps', ['icons/hicolor/24x24/apps/fluxgui.svg']),
    ('share/icons/hicolor/32x32/apps', ['icons/hicolor/32x32/apps/fluxgui.svg']),
    ('share/icons/hicolor/48x48/apps', ['icons/hicolor/48x48/apps/fluxgui.svg']),
    ('share/icons/hicolor/64x64/apps', ['icons/hicolor/64x64/apps/fluxgui.svg']),
    ('share/icons/hicolor/96x96/apps', ['icons/hicolor/96x96/apps/fluxgui.svg']),
    ('share/icons/ubuntu-mono-dark/status/16', ['icons/ubuntu-mono-dark/status/16/fluxgui-panel.svg']),
    ('share/icons/ubuntu-mono-dark/status/22', ['icons/ubuntu-mono-dark/status/22/fluxgui-panel.svg']),
    ('share/icons/ubuntu-mono-dark/status/24', ['icons/ubuntu-mono-dark/status/24/fluxgui-panel.svg']),
    ('share/icons/ubuntu-mono-light/status/16', ['icons/ubuntu-mono-light/status/16/fluxgui-panel.svg']),
    ('share/icons/ubuntu-mono-light/status/22', ['icons/ubuntu-mono-light/status/22/fluxgui-panel.svg']),
    ('share/icons/ubuntu-mono-light/status/24', ['icons/ubuntu-mono-light/status/24/fluxgui-panel.svg']),
    ('share/icons/Adwaita/16x16/status', ['icons/Adwaita/16x16/status/fluxgui-panel.svg']),
    ('share/icons/breeze/status/22', ['icons/breeze/status/22/fluxgui-panel.svg']),
    ('share/icons/breeze-dark/status/22', ['icons/breeze-dark/status/22/fluxgui-panel.svg']),
    ('share/icons/elementary/status/24', ['icons/elementary/status/24/fluxgui-panel.svg']),
    ('share/icons/elementary-xfce/panel/22', ['icons/elementary-xfce/panel/22/fluxgui-panel.svg']),
    ('share/icons/elementary-xfce-dark/panel/22', ['icons/elementary-xfce-dark/panel/22/fluxgui-panel.svg']),
    ('share/applications', ['desktop/fluxgui.desktop'])]

scripts = ['fluxgui']

if (os.path.exists("xflux")):
    # Unlike for 'scripts', the 'setup.py' doesn't modify the
    # permissions on files installed using 'data_files', so we need to
    # set the permissions ourselves.
    subprocess.call(['chmod', 'a+rx', 'xflux'])
    data_files.append(('bin', ['xflux']))
else:
    print("""WARNING: if you are running 'python setup.py' manually, and not as
part of Debian package creation, then you need to download the 'xflux'
binary separately. You can do this by running

    ./download-xflux.py

before running 'setup.py'.""")


setup(name = "f.lux indicator applet",
    version = "1.1.11~pre",
    description = "f.lux indicator applet - better lighting for your computer",
    author = "Kilian Valkhof, Michael and Lorna Herf, Josh Winters",
    author_email = "kilian@kilianvalkhof.com",
    url = "http://www.stereopsis.com/flux/",
    license = "MIT license",
    package_dir = {'fluxgui' : 'src/fluxgui'},
    packages = ["fluxgui",],
    package_data = {"fluxgui" : ["*.glade"] },
    data_files=data_files,
    scripts = scripts,
    long_description = """f.lux indicator applet is an indicator applet to
    control xflux, an application that makes the color of your computer's
    display adapt to the time of day, warm at nights and like sunlight during
    the day""",
    cmdclass = {"install": CustomInstall},
  )

