import sys
import os

sys.path.append('')
from Algorithm.AlgorithmImplement_SSVEP import AlgorithmImplement_SSVEP
from Framework.AlgorithmSystemManager import AlgorithmSystemManager
from Task.TaskManager_SSVEP import TaskManager_SSVEP
from TestData.loadData import loadData

if __name__ == '__main__':
    # 生成框架实例
    algorithmSystemManager = AlgorithmSystemManager()
    # 生成SSVEPTaskManager的实例
    taskManager_SSVEP = TaskManager_SSVEP()
    # SSVEP赛题注入框架
    algorithmSystemManager.addTask(taskManager_SSVEP)

    # 加载SSVEP数据
    dataPath = os.path.join(os.getcwd(), 'TestData')
    SSVEPdataPath = os.path.join(dataPath, 'SSVEP')
    # 读取SSVEP数据
    personDataTransferModelSet = loadData(SSVEPdataPath)

    # 注入SSVEP数据
    algorithmSystemManager.addData(personDataTransferModelSet)
    # 生成算法实例
    algorithmImplement_SSVEP = AlgorithmImplement_SSVEP()
    # 注入算法
    algorithmSystemManager.addAlgorithm(algorithmImplement_SSVEP)
    # 执行算法
    algorithmSystemManager.run()
    # 获取评分
    scoreModel = algorithmSystemManager.getScore()
    # 输出结果
    print(scoreModel.score)
    # 清除算法
    algorithmSystemManager.clearAlgorithm()
    # 清除数据
    algorithmSystemManager.clearData()
    # 清除赛题
    algorithmSystemManager.clearTask()
