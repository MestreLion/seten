# TOTALLY WIP!!!
# USE apt-manage (from repolib)!!!
# Also see ../setuplib@add_ppa()
#
# Dependencies changelog:
# - 'apt-transport-https' no longer needed since apt 1.5 (2017)
# - 'gpg --dearmor' not needed, '.asc' armored ASCII keys supported since apt 1.4
# - See (and update) brave-browser, firefox
#
# sudo apt install python3-software-properties
#   (already installed, requirement of ubuntu-desktop{,-minimal})
# noinspection PyPep8Naming


https://code.launchpad.net/~smoser/software-properties/trunk.lp1667725-https-signing-key/+merge/351824
#+def get_ppa_signing_key_data(info=None):
#+    """Return signing key data in armored ascii format for the provided ppa.
#+
#+    If 'info' is a dictionary, it is assumed to be the result
#+    of 'get_ppa_info(ppa)'.  If it is a string, it is assumed to
#+    be a ppa_path.
#+
#+    Return value is a text string."""
#+    if isinstance(info, dict):
#+        link = info["self_link"]
#+    else:
#+        link = get_ppa_info(mangle_ppa_shortcut(info))["self_link"]
#+
#+    return get_info_from_https(link + "?ws.op=getSigningKeyData",
#+                               accept_json=True, retry_delays=(1, 2, 3))

# https://api.launchpad.net/devel.html
# https://api.launchpad.net/devel/~deadsnakes/+archive/ubuntu/ppa?ws.op=getSigningKeyData
#
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
