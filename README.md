SetEn - The Setup Engine
==============================================================================

*For those like me that never heard of Ansible or Terraform*

A collection of install and setup scripts, tailored for my personal use and
hopefully useful to others. Heavily geared towards configuring Ubuntu Desktops
and Laptops after its installation.

Perfect for automatically installing and configuring software that:

- Has installation steps beyond the basic`apt install`, so you don't have to
  remember what is its standard way:
  - Does it have an official PPA? Which one?
  - Using a language-specific installer, such as `pip`, `cargo` or `npm`?
  - Is it a vendor repository to be added to at `sources.list.d/`? GPG Keys?
  - Built from source? Ok, but `wget -O- ... | tar x ...` or `git clone ...`?
    Then `./configure && make && make install` or `cmake`?
  - You get the idea: every time you see *“Installation Instructions”* in a
    software's website or GitHub page, save those instructions as a setup script.

- You have lots of settings you want to customize, and it is tedious and not
  reproducible to do so using its GUI. Be it a simple Gnome app such as Gedit
  and Nautilus, or your complex NGINX reverse proxying to Apache setup.

---

To get started:

- Run this to bootstrap the setup environment:

```sh
bash <(wget -qO- https://github.com/MestreLion/seten/raw/main/bootstrap.sh)
```

- Run the setup scripts you want: `seten <name>.install`. You can directly run the installers too!

- Have fun!

See the [available installers](setup) for more information.
The [libraries](setuplib.d) might be worth taking a look too.

---

FAQ
---
*Questions no one really ever asked, but serve as a self-reminder of some of my design decisions*

- Why all the environment variables are prefixed as `SETUP_` and not `SETEN_`?
  - Historical reasons. Before being an independent project, *Seten* was merely a `setup/`
    subdirectory of my [personal scripts](https://github.com/MestreLion/scripts), hence
    the prefix. I'm too lazy for a mass-rename that will produce a noisy git diff for
    little gain, since all but one of these vars are only used internally, or maybe
    referenced in the config file, but not as actual environment variables.

- What about `SETEN_CONFIG`?
  - See the *“all but one”* in the above answer? Well, that exception is `SETEN_CONFIG`,
    the path of the config file. Being the only setting that cannot be set in the
    config file, by definition, it must be set as an environmental variable, possibly
    in `~/.profile`. As such it had to be properly prefixed with an easily recognizable,
    distinguished namespace.
