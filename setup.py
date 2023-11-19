import setuptools
import os

# Lê a descrição longa a partir do arquivo README.md
with open("README.md", "r") as fh:
    long_description = fh.read()

# Caminho para os dados do arquivo a serem incluídos no pacote
data_files_path = os.path.join("lib", "site-packages")
dll_path = os.path.join("ultrades", "UltraDES.dll")

setuptools.setup(
    # Informações básicas
    name="ultrades-python",
    version="0.0.5",
    author="LACSED Developers",
    author_email="lacsed.ufmg@gmail.com",
    description="A library for analysis and control of Discrete Event Systems",
    
    # Descrição longa e seu tipo
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Link para o repositório do projeto
    url="https://github.com/lacsed/ultrades",
    
    # Encontra todos os pacotes no diretório atual
    packages=setuptools.find_packages(),
    
    # Classificadores para informar sobre o tipo de pacote
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
    # Dependências necessárias
    install_requires=[
        'pycparser',
        'pythonnet>=2.5.0',
        'ipython'
    ],
    
    # Arquivos de dados a serem incluídos no pacote
    data_files=[(data_files_path, [dll_path])],
    
    # Versão mínima do Python necessária
    python_requires='>=3.6',
)
