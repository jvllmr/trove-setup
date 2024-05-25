from pathlib import Path

from trove_setup.app import TConfigType, TroveSetupApp

if __name__ == "__main__":
    app = TroveSetupApp(type_=TConfigType.pep621, pyproject_path=Path(__file__).parent)
    app.run()
