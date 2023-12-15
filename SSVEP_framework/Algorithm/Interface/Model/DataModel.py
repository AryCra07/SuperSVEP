class DataModel:
    def __init__(self):
        self.data = None
        # double类型: 表示当前数据块相对本次Session起点位置(每名受试者一次采集视为一个Session)
        # 重置为0, 则认为开始新的block
        self.startPosition = 0
        self.personID = 0
        # 程序终止标志
        # bool类型
        self.finishedFlag = bool()
