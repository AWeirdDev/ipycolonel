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
    shutil.copytree("ipycolonel-environment", ".ipycolonel/%s" % name)


class Instance:
    def __init__(self, *, remove_on_exit: bool = True):
        self.name = str(uuid.uuid4())
        copy_environment(self.name)
        create_directories(self.name)
        self.runtime = WASMRuntime()

        if remove_on_exit:
            atexit.register(self.handle_exit)

    def get_stds(self) -> Mapping[Literal["stdout", "stderr"], str]:
        contents = {}
        for name, p in {
            "stdout": f".ipycolonel/{self.name}/.stdout",
            "stderr": f".ipycolonel/{self.name}/.stderr",
        }.items():
            with open(p, "r", encoding="utf-8") as f:
                t = f.read()
                contents.update({name: t})

        return contents

    def run(self, *, code: str):
        self.runtime = self.runtime.init(code, name=self.name)
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
