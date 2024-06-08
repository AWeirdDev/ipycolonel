import atexit

import os
import shutil
from typing import Literal, Mapping
import uuid

from wasmtime import ExitTrap

from .wasm import WASMRuntime


def create_directories(name: str):
    os.makedirs(".ipycolonel/%s" % name, exist_ok=True)
    os.makedirs("ipycolonel-environment", exist_ok=True)


def copy_environment(name: str):
    shutil.copytree("ipycolonel-environment/packages", ".ipycolonel/%s" % name)


def copy_venv(name: str):
    shutil.copytree("ipycolonel-environment/venv", ".ipycolonel/%s/venv" % name)


class Instance:
    def __init__(self, *, venv: bool = False, remove_on_exit: bool = True):
        self.name = str(uuid.uuid4())
        self.venv = venv

        self.runtime = WASMRuntime()
        self.init_env()

        if remove_on_exit:
            atexit.register(self.handle_exit)

    def init_env(self):
        if not self.venv:
            copy_environment(self.name)
        else:
            copy_venv(self.name)

        create_directories(self.name)

    def get_stds(self) -> Mapping[Literal["stdout", "stderr"], str]:
        contents = {}
        for name, p in {
            "stdout": f".ipycolonel/{self.name}/stdout",
            "stderr": f".ipycolonel/{self.name}/stderr",
        }.items():
            with open(p, "r", encoding="utf-8") as f:
                t = f.read()
                contents.update({name: t})

        return contents

    def run(self, *, code: str):
        self.runtime = self.runtime.init(code, name=self.name, venv=self.venv)
        try:
            self.runtime.exec()
        except ExitTrap:
            pass

        return self.get_stds()

    def handle_exit(self):
        del self.runtime
        import gc

        gc.collect()
        shutil.rmtree(".ipycolonel/%s" % self.name, ignore_errors=True)
