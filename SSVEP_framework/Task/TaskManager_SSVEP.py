from Algorithm.Interface.ProblemInterface import ProblemInterface
from Task.Interface.TaskInterface import TaskInterface
from Task.Model.CurrentProcessModel import CurrentProcessModel
from Task.Interface.Model.ScoreModel import ScoreModel
from Algorithm.Interface.Model.DataModel import DataModel
import numpy as np
import math
from random import shuffle

class TaskManager_SSVEP(TaskInterface, ProblemInterface):
    # 类属性：赛题名称
    PROBLEMNAME = 'SSVEP'

    def __init__(self):
        # 受试者信息
        super().__init__()
        self.personTable = []
        # 文件信息列表
        self.dataFileTable = []
        # 试次信息列表
        self.trialTable = []
        # 结果记录信息
        self.recordTable = []
        # 每个数据包的长度
        self.segmentLength = 0
        # 试次最大读取长度
        self.maxTrialLength = 0
        # 采样率
        self.srate = 0
        # 目标数
        self.targetNumber = 0
        # 刺激trigger编号列表
        self.stimulationEventTypeVector = []
        # 测试试次trigger编号
        self.testTrialStartEvent = []
        # 赛题配置
        self.taskConfiguration = None
        # 当前进度模型
        self.currentProcessModel = None

    def initial(self, taskConfiguration):
        self.taskConfiguration = taskConfiguration
        self.currentProcessModel = CurrentProcessModel()
        self.personTable = [['ID', 'NAME']]
        self.dataFileTable = [['ID', 'PERSONTABLEID', 'NAME', 'EEGDATA']]
        self.trialTable = [['ID', 'DATAFILETABLEID', 'ORIGINALEVENTINDEX', 'EVENTTYPE', 'EVENTPOSITION','PERSONID']]
        self.recordTable = [['ID', 'DATAFILETABLEID', 'REPORTPOINT', 'RESULTTYPE']]
        experimentEventTypeTable = self.taskConfiguration.experimentEventTypeTable
        self.stimulationEventTypeVector = [experimentEventTypeTable[i][1] for i in
                                           range(1, len(experimentEventTypeTable)) \
                                           if (experimentEventTypeTable[i][2] == 'STIMULATION')]

        testEventTypeTable = self.taskConfiguration.testEventTypeTable
        if testEventTypeTable[1][2] == 'STIMULATION':
            self.testTrialStartEvent.append(testEventTypeTable[1][1])

        self.srate = self.taskConfiguration.srate
        self.targetNumber = self.taskConfiguration.targetNumber
        self.segmentLength = self.taskConfiguration.packageLength * self.taskConfiguration.srate
        self.maxTrialLength = self.taskConfiguration.maxTrialTime * self.taskConfiguration.srate

    def addData(self, personDataTransferModelSet):
        self.personNum = len(personDataTransferModelSet)
        for personIndex in range(0, len(personDataTransferModelSet)):
            personDataTransferModel = personDataTransferModelSet[personIndex]
            blockDataTransferModelSet = personDataTransferModel.blockDataTransferModelSet
            # 调用函数
            personID = self.__addPerson(personDataTransferModel.name)
            for blockIndex in range(0, len(blockDataTransferModelSet)):
                blockDataTransferModel = blockDataTransferModelSet[blockIndex]
                # 调用函数
                self.__addDataFile(personID, blockDataTransferModel.name, blockDataTransferModel.data)

    def getScore(self):
        # 调用函数
        scoreModel = self.__calculateScore()
        return scoreModel

    def clearData(self):
        self.personTable = [['ID', 'NAME']]
        self.dataFileTable = [['ID', 'PERSONTABLEID', 'NAME', 'EEGDATA']]
        self.trialTable = [['ID', 'DATAFILETABLEID', 'ORIGINALEVENTINDEX', 'EVENTTYPE', 'EVENTPOSITION','PERSONID']]
        TaskManager_SSVEP.clearRecord(self)

    def clearRecord(self):
        self.recordTable = [['ID', 'DATAFILETABLEID', 'REPORTPOINT', 'RESULTTYPE']]
        self.currentProcessModel.dataFileTableID = 1
        self.currentProcessModel.currentPosition = 0

    def initialRecord(self):
        self.shuffleList = [i + 1 for i in range(0, self.personNum)]
        shuffle(self.shuffleList)
        self.shuffleTrialTable = [['ID', 'DATAFILETABLEID', 'ORIGINALEVENTINDEX', 'EVENTTYPE', 'EVENTPOSITION', 'PERSONID']]
        for i in self.shuffleList:
            for trialIndex in range(1, len(self.trialTable)):
                if (i == self.trialTable[trialIndex][5]):
                    self.shuffleTrialTable.append(self.trialTable[trialIndex])
        self.shuffleDataFileTable = [['ID', 'PERSONTABLEID', 'NAME', 'EEGDATA']]
        for i in self.shuffleList:
            for blockIndex in range(1,len(self.dataFileTable)):
                if(i==self.dataFileTable[blockIndex][1]):
                    self.shuffleDataFileTable.append(self.dataFileTable[blockIndex])

        # print(self.shuffleList)

    def getData(self):
        dataModel = DataModel()
        shuffleDataFileTable_local = self.shuffleDataFileTable
        # block编号，从1开始，除去table的第一行
        dataFileTableID = shuffleDataFileTable_local[self.currentProcessModel.dataFileTableID][0]
        # person编号
        personReadID = shuffleDataFileTable_local[self.currentProcessModel.dataFileTableID][1]
        # 开始位置，从0开始
        startPoint = self.currentProcessModel.currentPosition
        # 结束位置，不减1，因为python的特性
        endPoint = startPoint + self.segmentLength
        # 取出对应的block的数据
        for tableIndex in range(1, len(shuffleDataFileTable_local)):
            if dataFileTableID == shuffleDataFileTable_local[tableIndex][0]:
                eegData = shuffleDataFileTable_local[tableIndex][3]

        eegDataLength = eegData.shape[1]
        blockEndFlag = False
        if startPoint < 0:
            startPoint = 0
        if endPoint >= eegDataLength:
            endPoint = eegDataLength
            blockEndFlag = True

        # 得到相应范围的数据
        data = eegData[:, int(startPoint):int(endPoint)]

        # 更改trigger
        for dataIndex in range(0, data.shape[1]):
            if data[data.shape[0] - 1, dataIndex] in self.stimulationEventTypeVector:
                data[data.shape[0] - 1, dataIndex] = 1
        # print(data)
        self.currentProcessModel.currentPosition = self.currentProcessModel.currentPosition + len(data[0])
        finishedFlag = False
        # 如果该block结束
        if blockEndFlag:
            # 是否为最后一个block
            if self.currentProcessModel.dataFileTableID >= len(shuffleDataFileTable_local) - 1:
                finishedFlag = True
            else:
                # 更新当前位置
                self.currentProcessModel.dataFileTableID = self.currentProcessModel.dataFileTableID+1
                self.currentProcessModel.currentPosition = 0
        personTableID = personReadID
        dataModel.data = data
        dataModel.startPosition = startPoint
        dataModel.personID = personTableID
        dataModel.finishedFlag = finishedFlag
        return dataModel

    def report(self, reportModel):
        resultType = reportModel.resultType
        dataFileTableID = self.shuffleDataFileTable[self.currentProcessModel.dataFileTableID][0]
        # dataFileTableID = self.currentProcessModel.dataFileTableID
        currentPosition = self.currentProcessModel.currentPosition
        if len(self.recordTable) > 1:
            newRecordId = len(self.recordTable)
        else:
            newRecordId = 1
        self.recordTable.append([newRecordId, dataFileTableID, currentPosition, resultType])

    def __addPerson(self, name):
        if len(self.personTable) > 1:
            personID = len(self.personTable)
        else:
            personID = 1
        self.personTable.append([personID, name])
        newPersonID = name[1:len(name)]
        newPersonID = int(newPersonID)
        return newPersonID

    def __addDataFile(self, personID, name, data):
        if len(self.dataFileTable) > 1:
            newDataFileId = len(self.dataFileTable)
        else:
            newDataFileId = 1
        self.dataFileTable.append([newDataFileId, personID, name, data])
        # trigger通道
        eventChannle = data[data.shape[0] - 1, :]
        # trigger位置
        fileEventPosition = np.nonzero(eventChannle)
        eventIndexVector = []
        targetEventVector = []
        targetPositonVector = []
        for triggerIndex in range(0, len(fileEventPosition[0])):
            typePositon = fileEventPosition[0][triggerIndex]
            fileEventType = eventChannle[typePositon]
            if fileEventType in self.stimulationEventTypeVector:
                eventIndexVector.append(triggerIndex)
                targetEventVector.append(fileEventType)
                targetPositonVector.append(typePositon)

        if len(self.trialTable) > 1:
            newTrialId = len(self.trialTable)
        else:
            newTrialId = 1

        for trialIndex in range(0, len(eventIndexVector)):
            self.trialTable.append([newTrialId, newDataFileId,
                                    eventIndexVector[trialIndex],
                                    int(targetEventVector[trialIndex]),
                                    targetPositonVector[trialIndex],personID])

            newTrialId = newTrialId + 1

    def __calculateScore(self):
        shuffleTrialTable_local = self.shuffleTrialTable
        # 从第一行开始算
        eventPosition = []
        for trialTableIndex in range(1, len(shuffleTrialTable_local)):
            eventPosition.append(shuffleTrialTable_local[trialTableIndex][4])
        eventSegmentEndPosition = []
        for positionIndex in range(0, len(eventPosition)):
            eventSegmentEndPosition.append(
                self.segmentLength * math.ceil(eventPosition[positionIndex] / self.segmentLength))

        resultType = []
        reportTimeLength = []
        # 对于每个trial,最后一个trial单独计算
        for trialTableIndex in range(1, len(shuffleTrialTable_local) - 1):
            recordTableForDataFile = []
            # blockID
            dataFileTableID = shuffleTrialTable_local[trialTableIndex][1]
            nextDataFileTableID = shuffleTrialTable_local[trialTableIndex + 1][1]
            for recordTableIndex in range(1, len(self.recordTable)):
                if self.recordTable[recordTableIndex][1] == dataFileTableID:
                    recordTableForDataFile.append(self.recordTable[recordTableIndex])
            # 如果下一个试次不是同一个block文件，寻找报告点大于当前事件分段点的第一次报告
            if dataFileTableID != nextDataFileTableID:
                recordIndex = [i for i in range(0, len(recordTableForDataFile)) \
                               if recordTableForDataFile[i][2] > eventSegmentEndPosition[trialTableIndex - 1]]

                if len(recordIndex) > 0:
                    resultTypeForThisTrial = recordTableForDataFile[recordIndex[0]][3]
                    reportTimeLengthForThisTrial = recordTableForDataFile[recordIndex[0]][2] - eventPosition[
                        trialTableIndex - 1]
                else:
                    resultTypeForThisTrial = 0
                    reportTimeLengthForThisTrial = self.maxTrialLength + 1

            else:
                # 如果下一个试次位于同一个数据文件中
                # 寻找报告点大于当前事件分段点，且小于等于下一次分段点的第一次报告
                recordIndex = [i for i in range(0, len(recordTableForDataFile)) \
                               if (eventSegmentEndPosition[trialTableIndex - 1] < recordTableForDataFile[i][2] <
                                   eventSegmentEndPosition[trialTableIndex])]

                if len(recordIndex) > 0:
                    resultTypeForThisTrial = recordTableForDataFile[recordIndex[0]][3]
                    reportTimeLengthForThisTrial = recordTableForDataFile[recordIndex[0]][2] - eventPosition[
                        trialTableIndex - 1]
                else:
                    resultTypeForThisTrial = 0
                    reportTimeLengthForThisTrial = self.maxTrialLength + 1

            resultType.append(resultTypeForThisTrial)
            reportTimeLength.append(reportTimeLengthForThisTrial)
        # 最后一个trial单独处理
        dataFileTableID = shuffleTrialTable_local[len(shuffleTrialTable_local) - 1][1]
        recordTableForLastTrial = []
        for recordTableIndex in range(1, len(self.recordTable)):
            if self.recordTable[recordTableIndex][1] == dataFileTableID:
                recordTableForLastTrial.append(self.recordTable[recordTableIndex])

        # 找到第一个大于最后一个trigger位置的报告点
        recordIndex = [i for i in range(0, len(recordTableForLastTrial)) \
                       if (recordTableForLastTrial[i][2] > eventSegmentEndPosition[len(eventSegmentEndPosition) - 1])]

        if len(recordIndex) > 0:
            resultTypeForThisTrial = recordTableForLastTrial[recordIndex[0]][3]
            reportTimeLengthForThisTrial = recordTableForLastTrial[recordIndex[0]][2] - eventPosition[
                len(eventPosition) - 1]
        else:
            resultTypeForThisTrial = 0
            reportTimeLengthForThisTrial = self.maxTrialLength + 1

        resultType.append(resultTypeForThisTrial)
        reportTimeLength.append(reportTimeLengthForThisTrial)

        # 报告时间
        reportTime = []
        for reportIndex in range(0, len(reportTimeLength)):
            reportTime.append(reportTimeLength[reportIndex] / self.srate)
            if reportTimeLength[reportIndex] > self.maxTrialLength:
                resultType[reportIndex] = 0

        # 统计正确数
        # 以block为单位计算ITR及正确率
        DATAFILETABLEID = [shuffleTrialTable_local[i][1] for i in range(1, len(shuffleTrialTable_local))]

        DATAFILETABLEID_set = set(DATAFILETABLEID)
        dataFileID = [ID for ID in DATAFILETABLEID_set]
        dataFileID.sort()

        blockITR = []
        # 对于每个block
        for dataFileIndex in range(0, len(dataFileID)):
            # 报告结果
            blockResult = [resultType[i - 1] for i in range(1, len(shuffleTrialTable_local)) \
                           if (shuffleTrialTable_local[i][1] == dataFileID[dataFileIndex])]
            # 原本结果
            blockEventType = [shuffleTrialTable_local[i][3] for i in range(1, len(shuffleTrialTable_local)) \
                              if (shuffleTrialTable_local[i][1] == dataFileID[dataFileIndex])]
            # 报告时间
            trialReportTimeForOneBlock = [reportTime[i - 1] for i in range(1, len(shuffleTrialTable_local)) \
                                          if (shuffleTrialTable_local[i][1] == dataFileID[dataFileIndex])]
            correctNum = 0
            # trialTable中对应于该block的内容
            for trialIndex in range(1, len(shuffleTrialTable_local)):
                if shuffleTrialTable_local[trialIndex][1] == dataFileID[dataFileIndex]:
                    # 预测正确个数
                    if resultType[trialIndex - 1] == shuffleTrialTable_local[trialIndex][3]:
                        correctNum = correctNum + 1

            # print(correctNum)
            # 平均预测时间
            avgTrialReportTimeForOneBlock = sum(trialReportTimeForOneBlock) / len(trialReportTimeForOneBlock)
            # 预测准确率
            accuracyForOneBlock = correctNum / len(blockResult)
            # 该block的ITR
            ITR = 60 * self.__calculateITR(self.targetNumber,
                                           accuracyForOneBlock,
                                           avgTrialReportTimeForOneBlock)
            blockITR.append(ITR)
        scoreModel = ScoreModel()
        scoreModel.score = sum(blockITR) / len(blockITR)
        return scoreModel

    def __calculateITR(self, N, P, T):

        if P == 0:
            ITR = (1 / T) * (math.log(N, 2) + (1 - P) * math.log((1 - P) / (N - 1), 2))
        if P <= 1 / N:
            ITR = 0
        elif P == 1:
            ITR = (1 / T) * (math.log(N, 2) + P * math.log(P, 2))
        else:
            ITR = (1 / T) * (math.log(N, 2) + (1 - P) * math.log((1 - P) / (N - 1), 2) + P * math.log(P, 2))
        return ITR
