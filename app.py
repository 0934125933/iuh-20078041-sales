from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# TẢI DỮ LIỆU TỪ FIRESTORE
cred = credentials.Certificate("./khoa-6a664-firebase-adminsdk-z3gwd-8c0cb81440.json")
appLoadData = firebase_admin.initialize_app(cred)

dbFireStore = firestore.client()

queryResults = list(dbFireStore.collection(u'tblIUHSALES').where(u'DEALSIZE', u'==', 'Large').stream())
listQueryResult = list(map(lambda x: x.to_dict(), queryResults))

df = pd.DataFrame(listQueryResult)

df["YEAR_ID"] = df["YEAR_ID"].astype("str")
df["QTR_ID"] = df["QTR_ID"].astype("str")

# TRỰC QUAN HÓA DỮ LIỆU WEB APP
app = Dash(__name__)

server = app.server

app.title = "Finance Data Analysis"

#Biểu đồ doanh thu theo năm
bd1_value = df[['YEAR_ID','SALES']].groupby('YEAR_ID').sum()
listValueLoiNhan = list(bd1_value.to_dict().values())
year = listValueLoiNhan[0].keys()
values_loiNhan = listValueLoiNhan[0].values()
bd1 = pd.DataFrame({'YEAR': year,'DoanhThu': values_loiNhan})

figSoLuongSanPham = px.histogram(df, x="YEAR_ID", y="QUANTITYORDERED", 
barmode="group", color="QTR_ID", title='Tổng số lượng sản phẩm theo quý và năm', histfunc = "sum",
labels={'YEAR_ID':'Từ năm 2003, 2004 và 2005', 'QTR_ID': 'Quý trong năm', 'Sum':'Tổng số lượng sản phẩm'})


figDoanhSoTheoNam = px.bar(bd1, x="YEAR", y="DoanhThu", title="Doanh Thu Theo Năm",
labels={'YEAR':'Năm',  'DoanhThu':'Doanh thu'})

figTiLeDongGopDanhSoTheoTungDoanhMuc = px.sunburst(df, path=['YEAR_ID', 'CATEGORY'], values='SALES',
color='QUANTITYORDERED',
labels={'parent':'Năm', 'labels':'Quý','QUANTITYORDERED':'Số lượng sản phẩm'},
title='TỈ LỆ ĐÓNG GHÓP CỦA DOANH SỐ THEO DANH MỤC TRONG NĂM')

figSoLuongHoaDon = px.sunburst(df, path=['YEAR_ID', 'QTR_ID'], values='QUANTITYORDERED',
color='QUANTITYORDERED',
labels={'parent':'Năm', 'labels':'Quý','QUANTITYORDERED':'Số lượng sản phẩm'},
title='Tỉ lệ số lượng sản phẩm theo quý và năm')
# Dữ liệu truy vấn
tongDoanhSo = df['SALES'].sum().round(2)
doanhSoCaoNhat = df.groupby(['CATEGORY']).sum(numeric_only=True)['SALES'].max()
#Tinh loi nhuan
#1 Tính total sale
df['TOTAL_SALES'] = df['QUANTITYORDERED'] * df['PRICEEACH']
#2 Tính lợi nhuận
df['Profit'] = (df['SALES'] - df['TOTAL_SALES']).round(2)
tongLoiNhuan = df['Profit'].sum().round(2)
loiNhuanCaoNhat = df.groupby(['CATEGORY']).sum('Profit')['Profit'].max()

figTiLeDongGopLoiNhanTheoTungDoanhMuc = px.sunburst(df, path=['YEAR_ID', 'CATEGORY'], values='Profit',
color='Profit',
labels={'parent':'Năm', 'labels':'Quý','QUANTITYORDERED':'Số lượng sản phẩm'},
title='TỈ LỆ ĐÓNG GHÓP CỦA LỢI NHUẬN THEO MỤC TRONG NĂM')

lnvalue = df[['YEAR_ID','Profit']].groupby('YEAR_ID').sum()
listValueLoiNhan = list(lnvalue.to_dict().values())
year = listValueLoiNhan[0].keys()
values_loiNhan = listValueLoiNhan[0].values()
bd2 = pd.DataFrame({'YEAR': year,'LoiNhuan': values_loiNhan})
figLoiNhanTheoNam = px.line(bd2, x="YEAR", y="LoiNhuan", title='LỢI NHUẬN BÁN HÀNG THEO NĂM', labels={'YEAR':'Năm',  'LoiNhuan':'Lợi nhuận'})

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Xây dựng danh mục sản phẩm tiềm năng ", className="header-title"
                ),
                
                html.H1(children="DHHTTT16B_20078041_Nguyễn Trần Đăng Khoa", className="header-title2" )
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[html.H4("DOANH SỐ SALE"),
                              html.P(tongDoanhSo)
                    ], className="so_lieu"),
                html.Div(
                    children=[html.H4("LỢI NHUẬN"),
                              html.P(tongLoiNhuan)
                    ], className="so_lieu"),
                html.Div(
                    children=[html.H4("TOP DOANH SỐ"),
                              html.P(doanhSoCaoNhat)
                    ], className="so_lieu"),
                html.Div(
                    children=[html.H4("TOP LỢI NHUẬN"),
                              html.P(loiNhuanCaoNhat)
                    ], className="so_lieu")
            ]
        ,className="under__header"),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                    id='doanhso-graph',
                    figure=figDoanhSoTheoNam),
                    className="mycard"
                ),
                html.Div(
                    children=dcc.Graph(
                    id='doanh_so_theo_muc-graph',
                    figure=figTiLeDongGopDanhSoTheoTungDoanhMuc),
                    className="mycard"
                )
            ], className="mywrapper"),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                    id='loi_nhuan_theo_nam-graph',
                    figure=figLoiNhanTheoNam),
                    className="mycard"
                ),
                html.Div(
                    children=dcc.Graph(
                    id='loi_nhuan_theo_muc-graph',
                    figure=figTiLeDongGopLoiNhanTheoTungDoanhMuc),
                    className="mycard"
                )
            ], className="mywrapper")
    ])


if __name__ == '__main__':
    app.run_server(debug=True)