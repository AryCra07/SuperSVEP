import os
import pickle

from Framework.Interface.Model.BlockDataTransferModel import BlockDataTransferModel
from Framework.Interface.Model.PersonDataTransferModel import PersonDataTransferModel


def loadData(folderPath):
    personnameSet = []
    subjectPath = []
    personDataTransferModelSet = []
    for root, dirs, files in os.walk(folderPath):
        # 被试名字
        if dirs:
            personnameSet.append(dirs)
            # print('sub_dirs当前路径下所有子目录:', personnameSet)  # 当前路径下所有子目录
    # 对于每个被试
    for subjectIndex in range(0,len(personnameSet[0])):
        subjectPath.append(os.path.join(folderPath, str(personnameSet[0][subjectIndex])))
        blockDataTransferModelSet = []
        # 对于每个block
        for root, dirs, files in os.walk(subjectPath[subjectIndex]):
            if files:
                # filesName = []
                # blockName = []
                for filesIndex in range(0, len(files)):
                    if 'pkl' in files[filesIndex]:
                        os.chdir(subjectPath[subjectIndex])
                        filesName = files[filesIndex]
                        fr = open(filesName, "rb")
                        # data = pickle.load(fr)
                        EEG = pickle.load(fr)
                        data = EEG['data']
                        # print(data)
                        blockName = filesName[0:filesName.find('.')]
                        blockDataTransferModel = BlockDataTransferModel(blockName,data)
                        blockDataTransferModelSet.append(blockDataTransferModel)
        personDataTransferModel = PersonDataTransferModel(str(personnameSet[0][subjectIndex]),blockDataTransferModelSet)
        personDataTransferModelSet.append(personDataTransferModel)

    return personDataTransferModelSet
