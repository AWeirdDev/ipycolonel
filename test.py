from ipycolonel.sandbox import Instance

instance = Instance(remove_on_exit=True)

print(
    instance.run(code="import math\nprint(math.pi)")
)
