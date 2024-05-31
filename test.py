from ipycolonel.sandbox import Instance

instance = Instance(
    code="""import this
print(dir(this))""", remove_on_exit=True
)
print(instance.run())
