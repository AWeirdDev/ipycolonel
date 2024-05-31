from typing import Iterable, Self
from wasmtime import Config, Linker, Engine, Module, Store, WasiConfig


class WASMRuntime:
    def init(self, code: str, *, name: str) -> Self:
        self.engine_cfg = Config()
        self.engine_cfg.consume_fuel = True
        self.engine_cfg.cache = True

        self.linker = Linker(Engine(self.engine_cfg))
        self.linker.define_wasi()

        self.python_module = Module(
            self.linker.engine, open("python-3.12.0.wasm", "rb").read()
        )

        self.name = name
        self.set_argv(["python", "-c", code])
        return self

    def set_argv(self, argv: Iterable[str]):
        self.config = WasiConfig()
        self.config.argv = argv
        self.config.stdout_file = (
            "./.ipycolonel/" + self.name + "/.stdout"
        )  # self.stdout
        self.config.stderr_file = (
            "./.ipycolonel/" + self.name + "/.stderr"
        )  # self.stderr
        # self.config.stdin_file = "./.ipycolonel/" + self.name + "/.stdin"
        self.config.preopen_dir("./.ipycolonel/%s" % self.name, "./")

        self.store = Store(self.linker.engine, self.config)

        self.store.set_fuel(400_000_000)
        self.store.set_wasi(self.config)
        self.instance = self.linker.instantiate(self.store, self.python_module)

        exports = self.instance.exports(self.store)
        self.start, _ = exports["_start"], exports["memory"]

        # mem.size(self.store)
        # data_len = mem.data_len(self.store)

    def exec(self):
        r = self.start(self.store)  # type: ignore
        self.store.close()
        return r
