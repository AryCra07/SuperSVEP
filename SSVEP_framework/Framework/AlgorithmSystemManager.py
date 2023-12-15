from Framework.Interface.FrameworkInterface import FrameworkInterface
from Task.TaskConfiguration_SSVEP import TaskConfiguration_SSVEP


class AlgorithmSystemManager(FrameworkInterface):
    # 实例属性
    def __init__(self):
        super().__init__()
        self.taskInterface = None
        self.algorithmInterface = None

    # 初始化
    def initial(self):
        pass

    # 填充任务
    def addTask(self, taskManager):
        self.taskInterface = taskManager
        # 若为SSVEP赛题
        if self.taskInterface.PROBLEMNAME == 'SSVEP':
            taskConfiguration_SSVEP = TaskConfiguration_SSVEP()
            self.taskInterface.initial(taskConfiguration_SSVEP)
        # 若为P300
        elif self.taskInterface.PROBLEMNAME == 'P300':
            pass

    # 填充数据
    def addData(self, personDataTransferModelSet):
        self.taskInterface.addData(personDataTransferModelSet)

    # 填充算法
    def addAlgorithm(self, algorithmImplement):
        self.algorithmInterface = algorithmImplement
        self.algorithmInterface.setProblemInterface(self.taskInterface)
        self.taskInterface.initialRecord()

    # 运行算法
    def run(self):
        self.algorithmInterface.run()

    # 取得成绩
    def getScore(self):
        scoreModel = self.taskInterface.getScore()
        return scoreModel

    # 清除赛题
    def clearTask(self):
        self.taskInterface = None

    # 清空已有数据
    def clearData(self):
        self.taskInterface.clearData()

    # 清除当前算法所有结果，为下一个算法做准备
    def clearAlgorithm(self):
        self.algorithmInterface = None
        self.taskInterface.clearRecord()
