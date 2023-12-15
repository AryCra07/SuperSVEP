import numpy as np
from scipy.linalg import sqrtm

class CCAClass:
    def __init__(self):
        pass

    def initial(self,targetTemplateSet):
        self.targetTemplateSet = targetTemplateSet
        
    def recognize(self,data):
        p = []
        data = data.T
        # qr分解,data:length*channel
        
        [Q_temp, R_temp] = np.linalg.qr(data)
        for frequencyIndex in range(0,len(self.targetTemplateSet)):
            template = self.targetTemplateSet[frequencyIndex]
            template = template[:,0:data.shape[0]]
            template = template.T
            [Q_cs,R_cs] = np.linalg.qr(template)
            data_svd = np.dot(Q_temp.T,Q_cs)
            [U,S,V] = np.linalg.svd(data_svd)
            rho = 1.25 * S[0] + 0.67 * S[1] + 0.5 * S[2] + 0.25 * S[3] + 0.15 * S[4]
            p.append(rho)
        result = p.index(max(p))
        result = result+1
        
        return result

    
