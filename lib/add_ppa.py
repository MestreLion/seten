# TOTALLY WIP!!!
# USE apt-manage (from repolib)!!!

# sudo apt install python3-software-properties
# noinspection PyPep8Naming
import softwareproperties.SoftwareProperties as softprop


KEY_DIR = "/etc/apt/keyrings"
KEY_FILE_FMT = KEY_DIR + "/{}.gpg"
DEB_LINE_FMT = "{} [arch={} signed-by]"


def add_ppa(sourceline: str, options: dict):
    shortcut: softprop.ppa.PPAShortcutHandler = softprop.shortcut_handler(sourceline)
    sp = softprop.SoftwareProperties(options=options)
    # in sp.add_source_from_shortcut(shortcut, options.enable_source)
    deb_line, file = shortcut.expand(codename=sp.distro.codename,
                                     distro=sp.distro.id.lower())
    deb_line = sp.expand_http_line(deb_line)
    deb_entry = softprop.SourceEntry(deb_line, file)
    if deb_entry.invalid:
        raise ValueError(f"Invalid <sourceline>: {sourceline}")
    print((deb_line, file, deb_entry))
    # in sp.check_and_add_key_for_whitelisted_shortcut(shortcut)

    info: dict = shortcut.info()
    for k, v in info.items():
        print(f"{k} = {v!r}")


if __name__ == '__main__':
    argv = ["ppa:mestrelion/ppa"]
    add_ppa(argv[0], {'enable_source': True})
