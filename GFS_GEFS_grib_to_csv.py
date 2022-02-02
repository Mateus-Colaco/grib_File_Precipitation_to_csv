import pygrib
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import numpy as np
import matplotlib
import geopandas as gpd
import matplotlib.colors as colors
import cartopy.feature as cfeature
from matplotlib.axes import Axes
import xarray as xr
import pandas as pd
import seaborn as sns
from datetime import datetime
import sys
import requests
import time as t
from datetime import datetime, timedelta
import os
import time as t
from ftplib import FTP
import glob
import regex as re
from copy import Error


class Previsao:

    def __init__(self, caminho):

        # Dates
        self.date = datetime.today().strftime('%Y%m%d')
        self.today = datetime.now().strftime(format='%d-%m-%Y')
        self.today_format_day = int(datetime.today().strftime('%d'))
        self.today_format_month = int(datetime.today().strftime('%m'))
        self.today_format_month_string = datetime.today().strftime('%m')
        self.mes_final = int(self.today_format_month)
        self.today_format_year = int(datetime.today().strftime('%Y'))
        self.mes_inicial = self.today_format_month
        self.caminho = caminho

        os.chdir(self.caminho)

        self.precipitation_data = np.array(0)

        self.colors = ["#ffffff", "#dedede", "#b5b5b5", "#959595", "#828282", "#b2f0fa", "#96d2fc",
                       "#92bfed", "#78b9fa", "#097ff6", "#0761bb",
                       "#0da011", "#10cb17", "#13e71a", "#2fee36", "#71f476",
                       "#FFE778", "#ffdf52", "#ffd724", "#e6bb00", "#ff7214", "#ff5005", "#ff2f05", "#eb2700",
                       "#c00100", "#A20100", "#870000", "#653b32"]

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                                             FUNCAO PARA ESCOLHER O MODELO
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def choose_model(self):
        self.models = ['WRF', 'ETA', 'BAM', 'GFS', 'GEFS']
        while True:
            self.model = str(input('Escolha um modelo: WRF, ETA, BAM, GFS ou GEFS: ')).upper()
            if self.model in self.models:
                print(os.getcwd())
                os.makedirs(os.getcwd() + f'/{self.model}', exist_ok=True)
                os.chdir(os.getcwd() + f'/{self.model}')
                print(os.getcwd())
                break
            else:
                print('Não é um dos modelos listados')

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                                     FUNCAO PARA SETAR AS EXTENSOES DO MAPA
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #                                                     min_lon           min_lat           max_lon          max_lat
    def set_extent(self, extent=[-110.0, -60.00, -20.00, 18.00]):
        self.extent = extent[:4]
        self.min_lon, self.max_lon, self.min_lat, self.max_lat = str(self.extent[0]), str(self.extent[2]), str(
            self.extent[1]), str(self.extent[3])
        return

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                           FUNCAO PARA SETAR AS VARIAVEIS RELACIONADAS AOS DIAS
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def set_quant_dias(self):
        self.quant_dias = int(input('Numero maximo de dias: ' + str((len(self.samples) - 1) / 4)))

    def set_dias(self, dia_inicial=1, quant_dias=16):
        self.quant_dias = quant_dias
        if self.today_format_month == 1 or self.today_format_month == 3 or self.today_format_month == 5 or self.today_format_month == 7 or self.today_format_month == 8 or self.today_format_month == 10 or self.today_format_month == 12:
            if self.today_format_day + self.quant_dias > 31:
                self.final_day = self.today_format_day + self.quant_dias - 31
                self.mes_final = self.today_format_month + 1
        elif self.today_format_month == 2:
            if (self.today_format_day + self.quant_dias) > 28:
                self.final_day = self.today_format_day + self.quant_dias - 28
                self.mes_final = self.today_format_month + 1
        else:
            if (self.today_format_day + self.quant_dias) > 30:
                self.final_day = self.today_format_day + self.quant_dias - 30
                self.mes_final = self.today_format_month + 1
            else:
                self.mes_final = self.today_format_month
        if self.mes_final > 12:
            self.mes_final -= 12
        self.dia_inicial = dia_inicial
        self.dias = self.quant_dias
        self.hora_inicial = (self.dia_inicial - 1) * 24
        print("quant_dias:", self.quant_dias, "\n dias:", self.dias, "\n hora_inicial", self.hora_inicial, "\n")
        self.samples_hour = (self.dias * 24) + self.hora_inicial
        self.dia_final = self.quant_dias + dia_inicial
        return

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                            FUNCAO PARA SETAR AS VARIAVEIS RODADA E RESOLUTION
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def set_resolution_hour_run(self, resolution='50', hour_run='00'):
        self.resolution = resolution
        self.hour_run = hour_run
        return

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                          FUNCAO PARA SETAR INTERVALO DE HORAS E RANGE ARRAY
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def set_hour_int_e_range(self, hour_int=6,
                             range=[0, 0.5, 1, 1.5, 2, 2.5, 5, 7.5, 10, 13, 16, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90,
                                    100, 125, 150, 175, 200, 250, 300]):
        self.hour_int = hour_int
        self.range = range
        return

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                            FUNCAO PARA SETAR AS VARIAVEIS AUTOMATICAMENTE
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    def set_vars_auto(self):
        try:
            os.makedirs(os.getcwd() + f'/Samples-{self.today}', exist_ok=True)
            self.samples = os.listdir(os.getcwd() + f'/Samples-{self.today}')
            self.dir = os.getcwd() + f'/Samples-{self.today}/'
            os.chdir(self.dir)
            print(self.dir)

        except:
            os.makedirs(os.getcwd() + f'\\Samples-{self.today}', exist_ok=True)
            self.samples = os.listdir(os.getcwd() + f'\\Samples-{self.today}')
            self.dir = os.getcwd() + f'\\Samples-{self.today}\\'
            os.chdir(self.dir)
        self.choose_model()
        self.set_hour_int_e_range()
        self.set_resolution_hour_run()
        self.set_dias()
        self.set_extent()
        return

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                              FUNCAO PARA SETAR AS VARIAVEIS MANUALMENTE
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    def set_vars_manual(self):
        try:
            os.makedirs(os.getcwd() + f'/Samples-{self.today}', exist_ok=True)
            self.samples = os.listdir(os.getcwd() + f'/Samples-{self.today}')
            self.dir = os.getcwd() + f'/Samples-{self.today}/'
            os.chdir(self.dir)
            print(self.dir)

        except:
            os.makedirs(os.getcwd() + f'\\Samples-{self.today}', exist_ok=True)
            self.samples = os.listdir(os.getcwd() + f'\\Samples-{self.today}')
            self.dir = os.getcwd() + f'\\Samples-{self.today}\\'
            os.chdir(self.dir)

        self.choose_model()
        self.set_hour_int_e_range(hour_int=int(input('Intervalo de Horas: \n')), range=np.arange(0, int(input(
            'Range Max: \n'), int(input('Intervalo de 0 até o Range Max: \n')))))
        self.set_resolution_hour_run(resolution=input('Resolution: \n', hour_run=input('Rodada 00 ou 06 ou 12 ou 18')))
        self.set_dias(dia_inicial=int(input('Primeiro Dia: \n')))
        self.set_extent(
            extent=[int(input('Longitude Min: \n')), int(input('Latitude Min: \n')), int(input('Longitude Max: \n')),
                    int(input('Latitude Max: \n'))])
        return

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                                                 DOWNLOAD DO MODELO GFS
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    def download_gfs(self):
        # Create the URL's based on the self.resolution
        if (self.resolution == '25'):
            self.url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p' + self.resolution + '.pl?file=gfs.t' + self.hour_run + 'z.pgrb2.0p' + self.resolution + '.f' + str(
                self.hour).zfill(
                3) + '&all_lev=on&all_var=on&subregion=&leftlon=' + self.min_lon + '&rightlon=' + self.max_lon + '&toplat=' + self.max_lat + '&bottomlat=' + self.min_lat + '&dir=%2Fgfs.' + self.date + '%2F00%2Fatmos'
            self.file_name = 'gfs.t' + self.hour_run + 'z.pgrb2.0p' + self.resolution + '.f' + str(self.hour).zfill(3)
        elif (self.resolution == '50'):
            self.url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p' + self.resolution + '.pl?file=gfs.t' + self.hour_run + 'z.pgrb2full.0p' + self.resolution + '.f' + str(
                self.hour).zfill(
                3) + '&all_lev=on&all_var=on&subregion=&leftlon=' + self.min_lon + '&rightlon=' + self.max_lon + '&toplat=' + self.max_lat + '&bottomlat=' + self.min_lat + '&dir=%2Fgfs.' + self.date + '%2F00%2Fatmos'
            self.file_name = 'gfs.t' + self.hour_run + 'z.pgrb2.0p' + self.resolution + '.f' + str(self.hour).zfill(3)
        elif (self.resolution == '1'):
            self.url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_' + self.resolution + 'p00.pl?file=gfs.t' + self.hour_run + 'z.pgrb2.' + self.resolution + 'p00.f' + str(
                self.hour).zfill(
                3) + '&all_lev=on&all_var=on&subregion=&leftlon=' + self.min_lon + '&rightlon=' + self.max_lon + '&toplat=' + self.max_lat + '&bottomlat=' + self.min_lat + '&dir=%2Fgfs.' + self.date + '%2F00%2Fatmos'
            self.file_name = 'gfs.t' + self.hour_run + 'z.pgrb2.' + self.resolution + 'p00.f' + str(self.hour).zfill(3)

        # Sends a GET request to the specified url
        myfile = requests.get(self.url)

        # Download the file
        open(os.getcwd() + '//' + self.file_name, 'wb').write(myfile.content)

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                               DOWNLOAD DOS MODELOS WRF ETA OU BAM
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    def donwload_WRF_ETA_or_BAM(self):

        if int(self.today_format_month) < 10:
            self.today_format_month = str(self.today_format_month)

        # FTP Address
        ftp = FTP('ftp.cptec.inpe.br')
        # FTP Credentials
        ftp.login('', '')

        # Access the FTP folder, based on the desired model
        if (self.model == 'WRF'):
            # FTP Path
            self.path_model = ('modelos/tempo/WRF/ams_05km/brutos/' + str(
                self.today_format_year) + '/' + self.today_format_month_string + '/' + str(
                self.today_format_day) + '/' + self.hour_run + '/')
            self.file_name = 'WRF_cpt_05KM_' + self.date_run_string + '_' + self.date_forecast + '.grib2'
        elif (self.model == 'ETA'):
            # FTP Path
            self.path_model = ('modelos/tempo/Eta/ams_40km/brutos/' + str(
                self.today_format_year) + '/' + self.today_format_month_string + '/' + str(
                self.today_format_day) + '/' + self.hour_run + '/')
            self.file_name = 'eta_40km_' + self.date_run_string + '+' + self.date_forecast + '.grb'
        elif (self.model == 'BAM'):
            # FTP Path
            self.path_model = ('modelos/tempo/BAM/TQ0666L064/brutos/' + str(
                self.today_format_year) + '/' + self.today_format_month_string + '/' + str(
                self.today_format_day) + '/' + self.hour_run + '/')
            self.file_name = 'GPOSNMC' + self.date_run_string + self.date_forecast + 'P.fct.TQ0666L064.grb'
        # Enter the FTP Path
        ftp.cwd(self.path_model)

        # Download the file
        try:
            ftp.retrbinary("RETR " + self.file_name, open(os.getcwd() + '//' + self.file_name, 'wb').write)
        except FileNotFoundError:
            print(f'Erro {self.file_name} não encontrado')
        # Quit the FPT connection
        ftp.quit()
        return

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                                               DOWNLOAD DO MODELO GEFS --- FAZENDO ---
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    def download_gefs(self):
        #
        if (self.resolution == '25'):
            self.url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p' + self.resolution + 'a.pl?file=geavg.t' + self.hour_run + 'z.pgrb2a.0p' + self.resolution + '.f' + str(
                self.hour).zfill(
                3) + '&leftlon=' + self.min_lon + '&rightlon=' + self.max_lon + '&toplat=' + self.max_lat + '&bottomlat=' + self.min_lat + '&showurl=&dir=%2Fgefs.' + self.date + '%2F00%2Fatmos%2Fpgrb2ap5'
            self.file_name = 'geavg.t' + self.hour_run + 'z.pgrb2a.0p' + self.resolution + '.f' + str(hour).zfill(3)
        elif (self.resolution == '50'):
            # url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p'+resolution+'a.pl?file=geavg.t'+hour_run+'z.pgrb2a.0p'+resolution+'.f'+str(hour).zfill(3)+'&all_lev=on&all_var=on&subregion=&leftlon='+min_lon+'&rightlon='+max_lon+'&toplat='+max_lat+'&bottomlat='+min_lat+'&dir=%2Fgefs.'+date+'%2F12%2Fatmos%2Fpgrb2ap5'
            self.url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p' + self.resolution + 'a.pl?file=geavg.t' + self.hour_run + 'z.pgrb2a.0p' + self.resolution + '.f' + str(
                self.hour).zfill(
                3) + '&all_lev=on&all_var=on&subregion=&leftlon=' + self.min_lon + '&rightlon=' + self.max_lon + '&toplat=' + self.max_lat + '&bottomlat=' + self.min_lat + '&dir=%2Fgefs.' + self.date + '%2F00%2Fatmos%2Fpgrb2ap5'
            # 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p'+self.resolution+'a.pl?file=geavg.t'+self.hour_run+'z.pgrb2a.0p'+self.resolution+'.f'+str(self.hour).zfill(3)+'&all_lev=on&all_var=on&subregion=&leftlon='+self.min_lon+'&rightlon='+self.max_lon+'&toplat='+self.max_lat+'&bottomlat='+self.min_lat+'&showurl=&dir=%2Fgefs.'+self.date+'%2F12%2Fatmos%2Fpgrb2ap5'
            self.file_name = 'geavg.t' + self.hour_run + 'z.pgrb2a.0p' + self.resolution + '.f' + str(self.hour).zfill(
                3)
        elif (self.resolution == '1'):
            # url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_'+resolution+'p00.pl?file=gfs.t'+hour_run+'z.pgrb2.'+resolution+'p00.f'+str(hour).zfill(3)+'&all_lev=on&all_var=on&subregion=&leftlon='+min_lon+'&rightlon='+max_lon+'&toplat='+max_lat+'&bottomlat='+min_lat+'&dir=%2Fgfs.'+date+'%2F00%2Fatmos'
            self.file_name = 'gfs.t' + self.hour_run + 'z.pgrb2.' + self.resolution + 'p00.f' + str(self.hour).zfill(3)
        # Print the file name
        print("File name: ", self.file_name)
        # Sends a GET request to the specified url
        myfile = requests.get(self.url)

        # Download the file
        open(os.getcwd() + '//' + self.file_name, 'wb').write(myfile.content)

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                                                            BAIXAR O MODELO
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    def download_model(self):
        os.chdir(os.getcwd() + '')
        if len(os.listdir(os.getcwd())) <= 1:
            for hour in range(self.hora_inicial, self.samples_hour + 1, self.hour_int):
                self.hour = hour
                if self.model == 'GFS':
                    self.download_gfs()
                elif self.model == 'WRF' or self.model == 'ETA' or self.model == 'BAM':
                    self.date_run = datetime.strptime(
                        str(self.today_format_year) + self.today_format_month_string + str(
                            self.today_format_day) + self.hour_run, '%Y%m%d%H')
                    self.date_run_string = self.date_run.strftime('%Y%m%d%H')
                    self.date_forecast = (self.date_run + timedelta(hours=hour)).strftime('%Y%m%d%H')
                    self.donwload_WRF_ETA_or_BAM()
                elif self.model == 'GEFS':
                    self.download_gefs()
                else:
                    print('Modelo não encontrado')


        else:
            print('Modelo já baixado')
            # for hour in range(self.hora_inicial, self.samples_hour + 1, self.hour_int):
            # self.hour = hour
            # self.download_gfs()

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                                                      CALCULA A PRECIPITAÇÃO
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #

    def range_forecast(self):
        self.samples = os.listdir(os.getcwd())
        for sample in self.samples:
            try:
                forecast = int(re.search(r'\.f(\d{3})', sample).group(1))
                if forecast <= self.samples_hour and forecast > self.hora_inicial:

                    grib_file = pygrib.open(os.getcwd() + '/' + sample)
                    if self.model == 'GFS':
                        grb = grib_file[596]
                    elif self.model == 'GEFS':
                        grb = grib_file[69]

                    self.totpr, self.lats, self.lons = grb.data(lat1=self.extent[1], lat2=self.extent[3],
                                                                lon1=self.extent[0] + 360, lon2=self.extent[2] + 360)
                    self.precipitation_data = self.totpr + self.precipitation_data
                else:
                    None
            except:
                print(f'Erro - {os.getcwd() + str("/") + sample} não possui padrão no nome do arquivo')

        return

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                                               CALCULA A PRECIPITACAO POR DIA
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #

    def pentada_csv(self):
        print(os.getcwd())
        self.samples = os.listdir(os.getcwd())
        self.extent = [-110.0, -60.00, -20.00, 18.00]
        self.precipitation_data = np.array(0)
        self.date = datetime.today().strftime('%Y%m%d')
        self.today_format_month = int(datetime.today().strftime('%m'))
        self.mes_final = self.today_format_month
        self.today_format_day = int(datetime.today().strftime('%d'))
        self.samples = os.listdir(os.getcwd())
        self.final_day = self.today_format_day
        self.df_consolidado = pd.DataFrame(columns=['Precipitacao', 'Latitude', 'Longitude', 'Data'])
        self.df_dia_unico = pd.DataFrame(columns=['Precipitacao', 'Latitude', 'Longitude', 'Data'])
        test = 0
        self.contador_dias = 1
        self.quant_dias = (len(self.samples) - 2) / 4
        for sample in self.samples:

            try:
                self.forecast = int(re.search(r'\.f(\d{3})', sample).group(1))
                self.forecast_hour = self.forecast % 24
                if self.forecast <= 384 and self.forecast > 0:
                    grib_file = pygrib.open(os.getcwd() + '/' + sample)
                    if self.model == 'GFS':
                        grb = grib_file[596]
                    elif self.model == 'GEFS':
                        grb = grib_file[69]
                    self.totpr, self.lats, self.lons = grb.data(lat1=self.extent[1], lat2=self.extent[3],
                                                                lon1=self.extent[0] + 360, lon2=self.extent[2] + 360)

                    self.row, self.column = self.totpr.shape
                    self.precipitation_data = self.totpr + self.precipitation_data
                    self.totpr_reshape = self.totpr.reshape(self.row * self.column, )
                    self.lats_reshape = self.lats.reshape(self.row * self.column, )
                    self.lons_reshape = self.lons.reshape(self.row * self.column, )

                    if self.today_format_month == 1 or self.today_format_month == 3 or self.today_format_month == 5 or self.today_format_month == 7 or self.today_format_month == 8 or self.today_format_month == 10 or self.today_format_month == 12:
                        if self.final_day > 31:
                            self.final_day = self.final_day - 31
                            self.mes_final = self.today_format_month + 1
                        else:
                            None
                        self.forecast_hour_coluna = np.full((self.row * self.column,), (
                            f'{str(self.final_day).zfill(2)}/{str(self.mes_final).zfill(2)}/2022  {str(self.forecast_hour).zfill(2)}:00:00'))
                        self.df_dia_unico['Precipitacao'] = self.totpr_reshape
                        self.df_dia_unico['Latitude'] = self.lats_reshape
                        self.df_dia_unico['Longitude'] = self.lons_reshape
                        self.df_dia_unico['Data'] = self.forecast_hour_coluna
                        self.df_consolidado = self.df_consolidado.append(
                            pd.DataFrame(self.df_dia_unico, columns=self.df_consolidado.columns), ignore_index=True)
                    elif self.today_format_month == 2:
                        if (self.today_format_day + self.quant_dias) > 28:
                            self.final_day = self.today_format_day + self.quant_dias - 28
                            self.mes_final = self.today_format_month + 1
                        else:
                            None
                        self.forecast_hour_coluna = np.full((self.row * self.column,), (
                            f'{str(self.final_day).zfill(2)}/{str(self.mes_final).zfill(2)}/2022  {str(self.forecast_hour).zfill(2)}:00:00'))
                        self.df_dia_unico['Precipitacao'] = self.totpr_reshape
                        self.df_dia_unico['Latitude'] = self.lats_reshape
                        self.df_dia_unico['Longitude'] = self.lons_reshape
                        self.df_dia_unico['Data'] = self.forecast_hour_coluna
                        self.df_consolidado = self.df_consolidado.append(
                            pd.DataFrame(self.df_dia_unico, columns=self.df_consolidado.columns), ignore_index=True)
                        if test == 0:
                            print(self.df_consolidado)
                            display(self.df_dia_unico)
                            test += 1
                    else:
                        if (self.today_format_day + self.quant_dias) > 30:
                            self.final_day = self.today_format_day + self.quant_dias - 30
                            self.mes_final = self.today_format_month + 1
                        else:
                            None
                        self.forecast_hour_coluna = np.full((self.row * self.column,), (
                            f'{str(self.final_day).zfill(2)}/{str(self.mes_final).zfill(2)}/2022  {str(self.forecast_hour).zfill(2)}:00:00'))
                        self.df_dia_unico['Precipitacao'] = self.totpr_reshape
                        self.df_dia_unico['Latitude'] = self.lats_reshape
                        self.df_dia_unico['Longitude'] = self.lons_reshape
                        self.df_dia_unico['Data'] = self.forecast_hour_coluna
                        self.df_consolidado = self.df_consolidado.append(
                            pd.DataFrame(self.df_dia_unico, columns=self.df_consolidado.columns), ignore_index=True)
                        self.mes_final = self.today_format_month

                    if self.mes_final > 12:
                        self.mes_final -= 12

                else:
                    None

                if self.contador_dias >= 4:
                    self.contador_dias = 1
                    self.final_day += 1

                else:
                    self.contador_dias += 1


            except:
                None

        # self.df_consolidado.to_csv('Teste.csv',sep = ';')
        display(self.df_consolidado)
        self.rows, nothing = self.df_consolidado.shape
        self.df_prim = self.df_consolidado.iloc[:self.rows // 3]
        self.df_seg = self.df_consolidado.iloc[self.rows // 3:2 * self.rows // 3]
        self.df_terc = self.df_consolidado.iloc[2 * self.rows // 3:self.rows]

        # self.df_prim = self.df_consolidado.iloc[]

        self.df_consolidado.Precipitacao.replace(to_replace="\.", value=",", inplace=True, regex=True)
        self.df_consolidado.Precipitacao.replace(to_replace="\.", value=",", inplace=True, regex=True)
        self.df_consolidado.Latitude.replace(to_replace="\.", value=",", inplace=True, regex=True)
        self.df_consolidado.Longitude.replace(to_replace="\.", value=",", inplace=True, regex=True)
        self.df_prim = self.df_consolidado.iloc[:self.rows // 3]
        self.df_seg = self.df_consolidado.iloc[self.rows // 3:2 * self.rows // 3]
        self.df_terc = self.df_consolidado.iloc[2 * self.rows // 3:self.rows]

        dir_modelo = os.getcwd()
        os.chdir('/content')
        self.df_prim.to_csv(f'{self.model} Primeira Pêntada.csv', sep=';')
        self.df_seg.to_csv(f'{self.model}  Segunda Pêntada.csv', sep=';')
        self.df_terc.to_csv(f'{self.model} Terceira Pêntada.csv', sep=';')
        os.chdir(dir_modelo)

    #
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                                                                                                                                             PLOTA O GRÁFICO
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    def plot_precip_chart(self, save_path, valor_max, intervalo_valores):
        fig, axs = plt.subplots(figsize=(20, 10), sharex=False, sharey=False,
                                subplot_kw=dict(projection=ccrs.PlateCarree()))  # 1 row x 2 columns
        axs.set_extent([self.extent[0], self.extent[2], self.extent[1], self.extent[3]], ccrs.PlateCarree())
        self.colors = self.color if self.model == 'GFS' else ['#FCFCFC', '#BFBEBE', '#ACA5A8', '#858585', '#6F6E6F',
                                                              '#B7FBAD', '#96F88B', '#7AF86D', '#50F153', '#22B322',
                                                              '#0BA10E', '#0F65DC',
                                                              '#2780EE', '#4FA5F8', '#95D4FD', '#BCF3FA', '#FEFBAA',
                                                              '#FDE878', '#FDC037',
                                                              '#FEA204', '#FC6106', '#FA3302', '#E11400', '#C30000',
                                                              '#A20100', '#970400',
                                                              '#850405', '#6B3931', '#876258', '#B28E87', '#CAA399',
                                                              '#F0DED1', '#CFC8DD',
                                                              '#AEA2C8', '#9C8ABA', '#6B5797', '#6B5797', '#750272',
                                                              '#920193', '#AF03B0',
                                                              '#CE04CF', '#E100D6']
        self.range = self.range if self.model == 'GFS' else [0, 0.2, 0.7, 1.2, 1.85, 2.5, 3.75, 5, 6.25, 7.5, 10, 12.5,
                                                             15, 17.5, 20, 22.5, 26.25, 30, 35, 40, 45, 50, 62.5, 75,
                                                             87.5, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325,
                                                             350, 375, 400, 425, 450, 475, 500]
        self.cmap = matplotlib.colors.ListedColormap(self.colors)
        self.cmap.set_over('#000000')
        self.cmap.set_under('#ffffff')
        # Add a shapefile
        # https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2019/Brasil/BR/br_unidades_da_federacao.zip
        try:
            shapefile = list(shpreader.Reader('/content/drive/MyDrive/Exponencial/BR/BR_UF_2019.shp').geometries())
            axs.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=0.3)
        except:
            print('Directory (Brasil UF) Not Found')
        try:
            america2 = list(shpreader.Reader(
                '/content/drive/MyDrive/Exponencial/America do Sul/a__031_001_americaDoSul.shp').geometries())
            axs.add_geometries(america2, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=0.5)
        except:
            print('Directory (America Do Sul) Not Found')
        # Add coastlines, borders and gridlines
        gl = axs.gridlines(crs=ccrs.PlateCarree(), color='gray', alpha=1.0, linestyle='--', linewidth=0.25,
                           xlocs=np.arange(-180, 180, 10), ylocs=np.arange(-90, 90, 10), draw_labels=True)
        gl.top_labels = False
        gl.right_labels = False
        levels = self.range

        # Plot the contours
        img1 = axs.contourf(self.lons, self.lats, self.precipitation_data, colors=self.colors, levels=self.range)

        # Define the ticks to be shown
        ticks2 = self.range

        # Add a colorbar
        plt.colorbar(img1, label='Acumulado (mm)', orientation='horizontal', ticks=ticks2, ax=axs, cmap=self.cmap)

        # Add a title
        self.mes_inicial = '0' + str(self.mes_inicial) if self.mes_inicial < 10 else str(self.mes_inicial)
        self.mes_final = '0' + str(self.mes_final) if self.mes_final < 10 else str(self.mes_final)
        axs.set_title(
            f'{self.model}: Acumulado de chuva {self.today_format_day}/{self.mes_inicial} - {self.final_day}/{self.mes_final} 00z',
            fontweight='bold', fontsize=10, loc='left')

        plt.savefig(
            save_path + f'{self.model}__{self.today_format_day}-{self.mes_inicial}_{self.final_day}-{self.mes_final}',
            pad_inches=0, dpi=300)
        plt.show()



previsao = Previsao("/content")
previsao.set_vars_auto()
previsao.download_model()
previsao.pentada_csv()