import Migrate

class RemoveWinModelerGraphPoints(Migrate.Step):
    version = Migrate.Version(2, 2, 0)

    def balete(self, dmd, path):
        parts = path.split('/')
        obj = dmd
        for part in parts[:-1]:
            obj = obj._getOb(part)
        obj._delObject(parts[-1])

    def cutover(self, dmd):
        base = 'Monitors/rrdTemplates/PerformanceConf/'
        paths = [
            base + 'graphDefs/Cycle Times/graphPoints/zenwinmodeler',
            base + 'thresholds/zenwinmodeler cycle time',
            base + 'datasources/zenwinmodeler',
            ]
        for path in paths:
            try:
                self.balete(dmd, path)
            except AttributeError:
                pass
            

RemoveWinModelerGraphPoints()
