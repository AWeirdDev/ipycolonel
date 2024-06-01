from ipycolonel.sandbox import Instance

instance = Instance(
    code="""import pandas
print(pandas)""", remove_on_exit=True
)
print(instance.run())
