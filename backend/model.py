from flask import Flask,render_template,request,session
from werkzeug.datastructures import FileStorage
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder 
from sklearn.ensemble import RandomForestRegressor
import matplotlib
matplotlib.use('Agg')
from sklearn.metrics import ConfusionMatrixDisplay,confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file:FileStorage):
    if file.filename.endswith(".csv") or file.filename.endswith(".xls"):
        df=pd.read_csv(file)
    elif file.filename.endswith(".xlsx"):
        df=pd.read_excel(file,engine="openpyxl")
    else:
        df=pd.DataFrame(["please upload a csv or excel file"],columns=["Invalid file type"])
    return df

def label_encoder(df,out):
    if out not in df.columns:
        print(df.columns)
        return df.columns
    for col in df.columns:
        if df[col].dtype=="object":
            df[col]=df[col].astype(str)
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
    return df

def init_model(model_type):
    models_list=open("./static/Models_list.txt","r").readlines()
    for model in models_list:
        if model.startswith("#") or model.startswith("from sklearn.datasets"):
            continue
        if model.endswith("\n"):
            model=model.replace("\n","")
        model.strip()
        if model_type in model:
            exec(model)
            if "lightgbm" in model:
                return eval(model_type)(verbosity=-1)
            else:
                return eval(model_type)()
    return RandomForestRegressor()

def train_model(df,out,model_type):
    model=init_model(model_type)
    model.fit(df.drop(columns=[out]),df[out])
    model_path=f"./static/ML_files/{model.__class__.__name__}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    return model,model_path

def save_image(df,out,model):
    plt.ioff()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=df[out], y=model.predict(df.drop(columns=[out])), hue=df[out], palette='Set1')
    model_name=model.__class__.__name__
    plt.title(f'{model_name} Predictions vs Actual')
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.tight_layout()
    image_name=f"./static/images/{model_name}_scatter.png"
    plt.savefig(image_name)
    plt.close()
    return image_name

def conf_mat(df,out,model):
    confusionmatrix=confusion_matrix(df[out],model.predict(df.drop(columns=[out])))
    cm_display = ConfusionMatrixDisplay(confusion_matrix = confusionmatrix)
    model_name=model.__class__.__name__
    print("Classifier" in model.__class__.__name__ )
    image_name=f"./static/images/{model_name}_confusion.png"
    cm_display.plot()
    plt.savefig(image_name)
    plt.close()
    return image_name

def Model_list():
    models_list=open("./static/Models_list.txt","r").readlines()
    new_list=[]
    for model in models_list:
        if model.startswith("#") or model.startswith("from sklearn.datasets"):
            continue
        if model.endswith("\n"):
            model=model.replace("\n","")
        new_list.append(model.strip().split("import ")[1])
    return new_list