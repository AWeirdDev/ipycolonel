from ipycolonel.sandbox import Instance

instance = Instance(
    code="""import protonbites
print(protonbites)""", remove_on_exit=True
)
print(instance.run())
