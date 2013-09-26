from cx_Freeze import setup, Executable

setup(
        name = "AutoWP Parser",
        version = "0.2.1",
        description = "AutoWP Parser",
        author = "antofa",
        executables = [Executable("autowp.py"), Executable("main.py")])