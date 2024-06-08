import venv


def create_venv():
    venv.create("./ipycolonel-environment/venv", system_site_packages=True, with_pip=True)
