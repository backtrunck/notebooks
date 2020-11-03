import pandas as pd
import numpy as np

print(f'Sua versão do pandas é:{pd.__version__}')
print(f'Sua versão do numpy é: {np.__version__}')

from sklearn.datasets import load_iris
iris = load_iris()
iris_nparray = iris.data

iris_dataframe = pd.DataFrame(iris.data, columns=iris.feature_names)
iris_dataframe['group'] = pd.Series([iris.target_names[k] for k in iris.target],
    dtype='category')
print(iris_dataframe)
print('medias')
print(iris_dataframe.mean(numeric_only=True))
print('medianas')
print(iris_dataframe.median(numeric_only=True))
print('desvio padrão')
print(iris_dataframe.std())
print('Faixas')
print(iris_dataframe.max(numeric_only=True)
- iris_dataframe.min(numeric_only=True))
print('Quartis')
print(iris_dataframe.quantile([0,.25,.50,.75,1]))
