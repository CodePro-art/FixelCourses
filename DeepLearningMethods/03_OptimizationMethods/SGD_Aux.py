import numpy as np

#--------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------#
class LinearLayer:
    def __init__(self, dIn, dOut, init='Kaiming'):
        if   init == 'Kaiming': mW = np.random.randn(dOut, dIn) * np.sqrt(2 / dIn)
        elif init == 'Xavier':  mW = np.random.randn(dOut, dIn) * np.sqrt(1 / dIn)
        else:                   mW = np.random.randn(dOut, dIn) / dIn #-- this is how we initialize previously

        vB = np.zeros(dOut)

        self.dParams = {'mW' : mW,   'vB': vB}
        self.dGrads  = {'mW' : None, 'vB' : None}

    def Forward(self, mX):
        mW      = self.dParams['mW']
        vB      = self.dParams['vB']
        self.mX = mX                   #-- store for Backward
        mZ      = mW @ mX + vB[:,None]

        return mZ

    def Backward(self, mDz):
        mW  = self.dParams['mW']
        mX  = self.mX

        vDb = mDz.sum(1)
        mDw = mDz  @ mX.T
        mDx = mW.T @ mDz

        self.dGrads['vB'] = vDb
        self.dGrads['mW'] = mDw

        return mDx

#--------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------#
class ReLULayer:
    def __init__(self):
        self.dParams = {}
        self.dGrads  = {}

    def Forward(self, mX):
        self.mX = mX                 #-- store for Backward
        mZ      = np.maximum(mX, 0)

        return mZ

    def Backward(self, mDz):
        mX    = self.mX
        mMask = (mX > 0).astype(np.float32)
        mDx   = mDz * mMask

        return mDx

#--------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------#
class SequentialModel:
    def __init__(self, lLayers):
        self.lLayers = lLayers

    def Forward(self, mX):
        for oLayer in self.lLayers:
            mX = oLayer.Forward(mX)
        return mX

    def Backward(self, mDz):
        for oLayer in reversed(self.lLayers):
            mDz = oLayer.Backward(mDz)


#--------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------#
def CrossEntropyLoss(vY, mZ):
    '''
    Returns both the loss and the gradient w.r.t the input (mZ)
    '''
    N      = len(vY)
    mHatY  = np.exp(mZ)
    mHatY /= np.sum(mHatY, axis=0)
    loss   = -np.log(mHatY[vY,range(N)]).mean()

    mDz               = mHatY
    mDz[vY,range(N)] -= 1
    mDz              /= N

    return loss, mDz

#--------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------#
def Accuracy(mScore, vY):
    vHatY    = np.argmax(mScore, axis=0)
    accuracy = (vHatY == vY).mean()
    return accuracy