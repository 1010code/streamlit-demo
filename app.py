import streamlit as st
import pandas as pd
import numpy as np
import pickle
import urllib.request

def fetchPickleFileFromHttp(pickle_file_url, timeout_s=1):
    try:
        if pickle_file_url:
            data = urllib.request.urlopen(pickle_file_url, timeout=timeout_s)
            return pickle.load(data)
        else:
            return []
    except Exception as error:
        print('讀取失敗', error)
        return []

st.set_page_config(layout="wide", initial_sidebar_state='collapsed') #https://github.com/streamlit/streamlit/issues/1770

st.sidebar.header('⚙️ Setting:')
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    xgbModel = pickle.load(uploaded_file)
    st.sidebar.write("模型載入成功！")
else:
    with open('./model/xgb-model.pickle', 'rb') as f:
        xgbModel = pickle.load(f)
# else:
#     ng_info_url = 'https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1sxhm5QyiMIoO7cWHzGP2aVm1ek1UIRfO'
#     xgbModel = fetchPickleFileFromHttp(ng_info_url)

st.header('👩🏻‍🔬 品質預測與配方分析')
st.write('**製程參數**:')
# get inputs
cols1 = st.columns(4)
LoadingFlow = round(float(cols1[0].number_input('Loading_flow(進料流量)', 79., 90., 88.985,step=0.1, format="%.3f")), 3)
MaterialNA = round(float(cols1[1].number_input('Material_NA(原料雜質)', 15., 21., 16.966,step=0.1, format="%.3f")), 3)
SteamFlow= round(float(cols1[2].number_input('Steam_flow(蒸汽用量)', 30., 36., 33.197, step=0.1, format="%.3f")), 3)
BackwashFlow = round(float(cols1[3].number_input('Backwash_flow(逆洗量)', 43., 57., 50.702, step=0.1, format="%.3f")), 3)
cols2 = st.columns(4)
SolventFlow = round(float(cols2[0].number_input('Solvent_flow(溶劑流量)', 27., 70., 54.81, step=0.1, format="%.3f")), 3)
RaffinateA = round(float(cols2[1].number_input('Raffinate_A(萃餘油濃度)', 1., 1.9, 1.71, step=0.1, format="%.3f")), 3)
HeatExchangerTemp = (float(cols2[2].number_input('HeatExchanger_temp(熱交換器溫度)', 87., 102., 97.583, step=0.1, format="%.3f")))
TowerTopPres = round(float(cols2[3].number_input('TowerTop_pres(塔頂壓力)', 1.1, 1.8, 1.524, step=0.1, format="%.3f")), 3)

# 預測原始的數值
prediction_state = st.markdown('預測中...')

data=np.array([[LoadingFlow, MaterialNA, SteamFlow, BackwashFlow, SolventFlow, RaffinateA, HeatExchangerTemp, TowerTopPres]])
pred=round(float(xgbModel.predict(data)[0]), 4)

prediction_state.write(f'##### 預測結果 Product_NA: {pred}')

if pred>=0.5:
    st.error('⛔&nbsp;&nbsp; 製成異常：雜質過高')
else:
    st.success('✅&nbsp;&nbsp; 正常範圍')
    
st.caption('提醒：產品雜質含量應少於 0.5')


st.write('#### 更多分析')
# 更多功能
with st.expander("點我展開"):
    st.write('**請輸入當前製成參數**:')
    cols1 = st.columns(4)
    tuneLoadingFlow = round(float(cols1[0].number_input('進料流量', 79., 90., LoadingFlow,step=0.1, format="%.3f")), 3)
    tuneMaterialNA = round(float(cols1[1].number_input('原料雜質', 15., 21., MaterialNA,step=0.1, format="%.3f")), 3)
    tuneSteamFlow= round(float(cols1[2].number_input('蒸汽用量', 30., 36., SteamFlow, step=0.1, format="%.3f")), 3)
    tuneBackwashFlow = round(float(cols1[3].number_input('逆洗量', 43., 57., BackwashFlow, step=0.1, format="%.3f")), 3)
    cols2 = st.columns(4)
    tuneSolventFlow = round(float(cols2[0].number_input('溶劑流量', 27., 70., SolventFlow, step=0.1, format="%.3f")), 3)
    tuneRaffinateA = round(float(cols2[1].number_input('萃餘油濃度', 1., 1.9, RaffinateA, step=0.1, format="%.3f")), 3)
    tuneHeatExchangerTemp = round(float(cols2[2].number_input('熱交換器溫度 ', 87., 102., HeatExchangerTemp, step=0.1, format="%.3f")), 3)
    tuneTowerTopPres = round(float(cols2[3].number_input('塔頂壓力', 1.1, 1.8, TowerTopPres, step=0.1, format="%.3f")), 3)
    
    col1, col2, col3 = st.columns(3)
    diffMaterialNA=round(tuneMaterialNA-MaterialNA, 2)
    col1.metric("原料雜質", f"{MaterialNA}%", f"{diffMaterialNA}%")
    diffSteamFlow=round(tuneSteamFlow-SteamFlow,2)
    col2.metric("蒸汽用量", f"{SteamFlow} L/s", f"{diffSteamFlow}L/s")
    diffHeatExchangerTemp=round(tuneHeatExchangerTemp-HeatExchangerTemp, 2)
    col3.metric("熱交換器溫度 ", f"{tuneHeatExchangerTemp}°C", f"{diffHeatExchangerTemp}°C")
    
    # 預測調整過後的數值
    prediction_state = st.markdown('預測中...')

    data=np.array([[tuneLoadingFlow, tuneMaterialNA, tuneSteamFlow, tuneBackwashFlow, tuneSolventFlow, tuneRaffinateA, tuneHeatExchangerTemp, tuneTowerTopPres]])
    pred=round(float(xgbModel.predict(data)[0]), 4)
    
    prediction_state.write(f'##### 調整後的預測結果 Product_NA: {pred}')

    if pred>=0.5:
        st.error('⛔&nbsp;&nbsp; 製成異常：雜質過高')
    else:
        st.success('✅&nbsp;&nbsp; 正常範圍')