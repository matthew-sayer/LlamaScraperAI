import subprocess

class TransformData:
    def __init__(self):
        pass

    def transformData(self):
        dbtPath = 'src/Data/dbt/ai_ingestion'
        subprocess.run(['dbt', 'run'], cwd=dbtPath)

    