class TaskConfiguration_SSVEP:
    # 目标采样率(Hz)，题目说明中给出
    experimentEventTypeTable = None
    srate = 250
    # 单次数据包长度(s)，题目说明中给出
    # packageLength * srate必须为正整数
    packageLength = 0.04
    # 单试次最长判决时间，题目中说明给出，超过该值，则认为判断错误。
    maxTrialTime = 4
    # 备选目标数，题目说明中给出
    targetNumber = 40

    def __init__(self):
        # 事件定义列表，题目说明中给出
        self.experimentEventTypeTable = []
        # 实验数据中的事件定义列表，题目中并不提及
        self.testEventTypeTable = []
        eventType_FrequencyVector = [8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 
                                    10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4, 11.6, 11.8, 
                                    12.0, 12.2, 12.4, 12.6, 12.8, 13.0, 13.2, 13.4, 13.6, 13.8, 
                                    14.0, 14.2, 14.4, 14.6, 14.8, 15.0, 15.2, 15.4, 15.6, 15.8]
        tempList = ['STIMULATION' for i in range(0, 40)]
        for eETTableIndex in range(0, 41):
            if eETTableIndex == 0:
                self.experimentEventTypeTable = [['ID', 'EVENTTYPE', 'OPERATION', 'FREQUENCY']]
            else:
                self.experimentEventTypeTable.append([eETTableIndex,
                                                      eETTableIndex,
                                                      tempList[eETTableIndex - 1],
                                                      eventType_FrequencyVector[eETTableIndex - 1]])
        self.testEventTypeTable = [['ID', 'EVENTTYPE', 'OPERATION']]
        self.testEventTypeTable.append([1, 1, 'STIMULATION'])
