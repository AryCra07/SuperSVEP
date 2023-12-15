# 仅供离线测试参考，正式测试请运行main.py
# Only for offline analysis，for formal test, please run main.py
import numpy as np
from numpy.matlib import repmat
import pickle
from scipy import signal
import math
import os

subnum=1
for subname in range(0,subnum):
    subName='S'+str(subname+1)
    filesName = './SampleData/SSVEP/S'+str(subname+1)+'/block1.pkl'
    fr = open(filesName, "rb")
    EEG = pickle.load(fr)
    data = EEG['data']
    pwd = os.getcwd()

    typeNum = 40
    nChans  = 8
    calTime = 2
    srate = 250
    offsetTime = 0.14
    sampleCount = calTime * srate
    offsetLength = math.floor(offsetTime * srate)

    fs = srate
    f0 = 50
    Q = 35
    b, a = signal.iircomb(f0, Q, ftype='notch', fs=fs)

    frequencySet = [8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8,
                    10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4, 11.6, 11.8,
                    12.0, 12.2, 12.4, 12.6, 12.8, 13.0, 13.2, 13.4, 13.6, 13.8,
                    14.0, 14.2, 14.4, 14.6, 14.8, 15.0, 15.2, 15.4, 15.6, 15.8]

    # 倍频数
    multiplicateTime = 5
    # 正余弦参考信号
    targetTemplateSet = []
    # 采样点
    t = np.linspace(0, (sampleCount - 1) / srate, int(sampleCount), endpoint=True)
    t = t.reshape(1, len(t))
    # 对于每个频率
    for freIndex in range(0, len(frequencySet)):
        frequency = frequencySet[freIndex]
        testFre = np.linspace(frequency, frequency * multiplicateTime, int(multiplicateTime), endpoint=True)
        testFre = testFre.reshape(1, len(testFre))
        numMatrix = 2 * np.pi * np.dot(testFre.T, t)
        cosSet = np.cos(numMatrix)
        sinSet = np.sin(numMatrix)

        csSet = np.append(cosSet, sinSet, axis=0)
        targetTemplateSet.append(csSet)

    triggerIndex = np.where((data[8, :]>0) & (data[8, :]<240))
    NTrials = len(triggerIndex[0])
    data_all=np.zeros([nChans, sampleCount-offsetLength, NTrials])
    p=np.zeros([NTrials, len(targetTemplateSet)])
    data_w=np.zeros([nChans, sampleCount-offsetLength,  len(targetTemplateSet)])
    #print(data[8, triggerIndex])
    for Ntrial in range(0, NTrials):
        data_epoch = signal.filtfilt(b, a, data[0:8, triggerIndex[0][Ntrial]+offsetLength:triggerIndex[0][Ntrial]+sampleCount])
        data_epoch = data_epoch.T

        [Q_temp, R_temp] = np.linalg.qr(data_epoch)
        for frequencyIndex in range(0,len(targetTemplateSet)):
            template = targetTemplateSet[frequencyIndex]
            template = template[:,0:data_epoch.shape[0]]
            template = template.T
            [Q_cs,R_cs] = np.linalg.qr(template)
            data_svd = np.dot(Q_temp.T,Q_cs)
            [U,S,V] = np.linalg.svd(data_svd)
            rho = 1.25 * S[0] + 0.67 * S[1] + 0.5 * S[2]
            p[Ntrial,frequencyIndex] = rho

        data_all[:,:,Ntrial]=data_epoch.T

    result = p.argmax(axis=1)
