from Algorithm.Interface.AlgorithmInterface import AlgorithmInterface
from Algorithm.Interface.Model.ReportModel import ReportModel
from Algorithm.CCAClass import CCAClass
from scipy import signal
import numpy as np
import math


class AlgorithmImplement_SSVEP(AlgorithmInterface):
    """
    这个类用于控制算法和框架的交互过程，从框架读入数据，传输给算法，并从算法获取结果，反馈给框架。

    Attributes:
        _problemInterface: 框架的回调接口，用于提交结果
        method: 处理数据的算法, 示例算法是CCA, 关于method的实例化和调用可自由调整, 甚至可以弃用(不建议)
        testTrialStartEvent: trial开始trigger，理论上的数据起点标记

        calTime: 计算所用的数据采样时间, 影响ITR的关键因素之一
        offsetTime: 偏移时间, 用于抵消采集脑电信号时的一些延迟, 如人的反应时、通信传输路径时延等

        __idleProcess(self, dataModel): 检查是否有trial开始trigger, 省去不必要处理
        __calculateProcess(self, dataModel): 处理数据

    """
    def __init__(self):
        super().__init__()
        # 类属性：赛题名称
        self.PROBLEMNAME = 'SSVEP'
        # 定义采样率，题目文件中给出
        sample_rate = 250
        # 选择导联编号
        self.selectChannel = [1, 2, 3, 4, 5, 6, 7, 8]
        # python列表从0开始算
        self.selectChannel = [i - 1 for i in self.selectChannel]
        # 试次启始事件定义，题目说明中给出
        self.testTrialStartEvent = 1
        # 频率集合
        frequencySet = [8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8,
                        10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4, 11.6, 11.8,
                        12.0, 12.2, 12.4, 12.6, 12.8, 13.0, 13.2, 13.4, 13.6, 13.8,
                        14.0, 14.2, 14.4, 14.6, 14.8, 15.0, 15.2, 15.4, 15.6, 15.8]

        ###################################################
        # 自此以下内容是可以改动的
        ###################################################

        # 计算所用的数据采样时间
        calTime = 3
        # 计算时偏移时间（s）
        offsetTime = 0.3
        # 偏移长度
        self.offsetLength = math.floor(offsetTime * sample_rate)
        # 计算长度
        self.sampleCount = calTime * sample_rate
        # 工频滤波器设置
        self.filterB, self.filterA = self.__getPreFilter(sample_rate)
        # 带通滤波器设置
        self.bpfilterB, self.bpfilterA = self.__getFilter(sample_rate)
        # 正余弦参考信号的的倍频数
        multiplicateTime = 5
        # 正余弦参考信号
        targetTemplateSet = []
        # 采样点
        t = np.linspace(0, (self.sampleCount - 1) / sample_rate, int(self.sampleCount), endpoint=True)
        t = t.reshape(1, len(t))
        # 生成正余弦参考信号
        for freIndex in range(0, len(frequencySet)):
            frequency = frequencySet[freIndex]
            testFre = np.linspace(frequency, frequency * multiplicateTime, int(multiplicateTime), endpoint=True)
            testFre = testFre.reshape(1, len(testFre))
            numMatrix = 2 * np.pi * np.dot(testFre.T, t)
            cosSet = np.cos(numMatrix)
            sinSet = np.sin(numMatrix)
            csSet = np.append(cosSet, sinSet, axis=0)
            targetTemplateSet.append(csSet)
        # 初始化算法
        self.method = CCAClass()
        self.method.initial(targetTemplateSet)

    def run(self):
        # 由框架给出，算法停止标志
        endFlag = False
        # 是否进入计算模式标签
        calFlag = False
        while not endFlag:
            # 读入数据, 需要用到dataModel的两个属性: data和finishedFlag. 其中type(dataModel.data)=numpy.ndarray,
            # dataModel.data.shape=(9,10)=(通道数, 采样点数)=(8+1, 0.04*250), 8+1中的8指数据通道, 1指trigger通道
            dataModel = self._problemInterface.getData()

            if not calFlag:
                # 非计算模式，则进行事件检测
                calFlag = self.__idleProcess(dataModel)
            else:
                # 计算模式，则进行处理
                calFlag, result = self.__calculateProcess(dataModel)
                # 如果有结果，则进行报告
                if result is not None:
                    reportModel = ReportModel()
                    reportModel.resultType = result
                    self._problemInterface.report(reportModel)
                    # 清空缓存
                    self.__clearCach()

            endFlag = dataModel.finishedFlag

    def __idleProcess(self, dataModel):
        data = dataModel.data
        eventData = data[-1, :]
        # 这里不能用list.index，因为不能保证有满足条件的值
        eventPosition = []
        for eventIndex in range(0, len(eventData)):
            if eventData[eventIndex] == self.testTrialStartEvent:
                eventPosition.append(eventIndex)
                break
        eegData = data[0:data.shape[0] - 1, :]
        # 有新的trigger
        if len(eventPosition) > 0:
            calFlag = True
            self.trialStartPoint = eventPosition[0]
            self.cacheData = eegData[:, self.trialStartPoint:]
        else:
            calFlag = False
            self.trialStartPoint = None
            self.__clearCach()

        return calFlag

    def __calculateProcess(self, dataModel):
        data = dataModel.data
        eventData = data[-1, :]
        # 这里不能用list.index，因为不能保证有满足条件的值
        eventPosition = []
        for eventIndex in range(0, len(eventData)):
            if eventData[eventIndex] == self.testTrialStartEvent:
                eventPosition.append(eventIndex)
                break
        eegData = data[0:data.shape[0] - 1, :]
        # 如果event为空，表示依然在当前试次中，根据数据长度判断是否计算
        if len(eventPosition) == 0:
            cacheDataLength = self.cacheData.shape[1]
            # 如果接收数据长度达到要求，则进行计算
            if eegData.shape[1] > self.sampleCount - cacheDataLength:
                self.cacheData = np.append(self.cacheData, eegData[:, :int(self.sampleCount - cacheDataLength)],
                                           axis=1)
                usedData = self.cacheData[:, self.offsetLength:]

                # 滤波处理
                usedData = self.__preprocess(usedData)
                # 开始计算
                result = self.method.recognize(usedData)
                # 停止计算模式
                calFlag = False
            else:
                # 反之继续采集数据
                self.cacheData = np.append(self.cacheData, eegData, axis=1)
                result = None
                calFlag = True
        # 下一试次已经开始,需要强制结束计算
        else:
            nextTrialStartPoint = eventPosition[0]
            cacheDataLength = self.cacheData.shape[1]
            usedLength = min(nextTrialStartPoint, self.sampleCount - cacheDataLength)
            self.cacheData = np.append(self.cacheData, eegData[:, :usedLength], axis=1)
            usedData = self.cacheData[:, self.offsetLength:]
            # 滤波处理
            usedData = self.__preprocess(usedData)
            # 开始计算
            result = self.method.recognize(usedData)
            # 开始新试次的计算模式
            calFlag = True
            # 清除缓存
            self.__clearCach()
            # 添加新试次数据
            self.cacheData = eegData[:, nextTrialStartPoint:]
        return calFlag, result

    @staticmethod
    def __getPreFilter(sample_rate):
        fs = sample_rate
        f0 = 50
        Q = 19
        b, a = signal.iircomb(f0, Q, ftype='notch', fs=fs)
        return b, a

    def __clearCach(self):
        self.cacheData = None

    def __preprocess(self, data):
        data = data[self.selectChannel, :]
        notchedData = signal.filtfilt(self.filterB, self.filterA, data)
        filtedData = signal.filtfilt(self.bpfilterB, self.bpfilterA, notchedData)
        return filtedData

    @staticmethod
    def __getFilter(sample_rate):
        fs = sample_rate/2
        N, Wn = signal.ellipord(90/fs, 100/fs, 3, 60)
        b, a = signal.ellip(N, 1, 60, Wn)
        return b, a
