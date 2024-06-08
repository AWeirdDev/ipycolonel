from ipycolonel import Instance

# Write your code here
code = """\
""".strip()

instance = Instance(venv=False)
result = instance.run(code=code)

print("stdout:", result['stdout'], sep="\n")
print("stderr:", result['stderr'], sep="\n")
