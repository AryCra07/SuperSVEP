from abc import abstractmethod


class AlgorithmInterface(object):
    # 类属性：赛题名称
    PROBLEMNAME = None

    def __init__(self):
        self._problemInterface = None

    @abstractmethod
    def run(self):
        pass

    def setProblemInterface(self, taskManager):
        self._problemInterface = taskManager
