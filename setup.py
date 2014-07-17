from cx_Freeze import setup, Executable

setup(
    name = "wash_data",
    version = "1",
    description = "data cleaning program",
    executables = [Executable("wash_data.py")]
)
