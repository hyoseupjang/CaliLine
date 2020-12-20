import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame as df
from scipy import stats

class Caliline():
    '''
    검량선을 작성하고 평가하는 간단한 도구를 제공합니다. 
    
    Methods:
    
    setdata(): 검량선 데이터와 시료의 흡광도를 넣습니다. 검량선을 작성합니다. 
    convert(): 검량선 함수입니다. 흡광도를 넣으면 농도로 바꾸어 줍니다. 
    accuracy(): 검량선의 정확도를 평가합니다. 
    precision(): 검량선의 정밀도를 평가합니다. 
    plot(): 검량선과 sample을 합쳐 플롯합니다. 
    '''

    def __init__(self):
        pass
    
    def setdata(self,reference,absorbance,sample):
        '''
        concentraion: 
        absp: 흡광도
        sample: Sample들의 흡광도
        출력: 검량선 작성에 사용된 점들의 정보를 출력합니다. 
        반환: 검량선 정보를 반환합니다. 
        '''
        self.calibrationdata=df({'Reference':reference,'Absorbance':absorbance})
        self.sample=sample
        slope,intercept,r_value,p_value,std_err=stats.linregress(self.calibrationdata['Absorbance'],self.calibrationdata['Reference'])
        self.caliline=np.poly1d([slope,intercept])
        con=self.caliline(self.calibrationdata['Absorbance'])
        self.calibrationdata['Concentraion']=con
        print(self.calibrationdata)
        return{'slope':slope,'intercept':intercept,'r_sq':r_value,'p':p_value,'sd':std_err}
    
    def convert(self,absp):
        '''
        흡광도를 농도로 바꿔주는 메서드입니다. 이 메서드는 setdata()메서드를 사용한 뒤에 사용할 수 있습니다. 
        입력: 흡광도(수로 변환가능한 Python object, Python array, Numpy ndarray.)
        반환: 농도(Type은 위와 같음.)
        '''
        return self.caliline(absp)
    
    def accuracy(self):
        '''
        겸량선의 정확도를 반환합니다. 
        반환: 검량선의 정확도 테이블(Pandas.Dataframe)
        '''
        acc=self.calibrationdata.groupby('Reference',as_index=False).mean()
        accuracy=acc['Concentraion']/acc['Reference'] #추측된 검량선 작성용 시료의 평균값을 ref값으로 나눔. 
        acc['accuracy']=accuracy
        return acc
    
    def precision(self):
        '''
        검량선의 정밀도를 반환합니다. 검량점당 시료가 하나라면 NaN이 반환됩니다. 
        반환: 검량선의 정밀도 테이블(Pandas.Dataframe)
        '''
        mean=self.calibrationdata.groupby('Reference',as_index=False).mean()
        sd=self.calibrationdata.groupby('Reference',as_index=False).std()
        precision=sd['Concentraion']/mean['Concentraion']
        mean['precision']=precision
        mean['sd']=sd['Concentraion']
        return mean
    
    def plot(self,filename,**kwargs):
        '''
        검량선 작성에 사용된 점과 검량선, 그리고 샘플을 플롯합니다. 
        '''
        
        unit=kwargs.get('unit',r'($\mu$mol/L)')
        name=kwargs.get('name','NAME')
        xname=kwargs.get('xname','Absorptivity')
        mk=kwargs.get('marker','+')

        F1=plt.figure(figsize=(5,5))
        ax1=F1.add_subplot(111)
        ax1.set_xlabel(xname)
        ax1.set_ylabel(f'{name} {unit}')
        plt.scatter(np.array(self.calibrationdata['Absorbance']),np.array(self.calibrationdata['Reference']),color='k',marker=mk,label='Calibration Points',zorder=100,linewidth=0.75)
        plt.plot(np.array(self.calibrationdata['Absorbance']),np.array(self.caliline(self.calibrationdata['Absorbance'])),color='k',label='Linear Regressed Value')
        plt.scatter(self.sample,self.caliline(self.sample),color='r',marker=mk,label='Sample',zorder=200)
        plt.legend()
        plt.grid(True)
        plt.savefig(filename)