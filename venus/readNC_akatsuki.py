import numpy as np
import xarray as xr
import netCDF4 as nc

file_path=''

ds=xr.open_dataset(file_path)
da_var_names=list(ds.data_vars)
ds.close()

da=ds[da_var_names[0]]

# print(f"데이터구성: {da.dims}")
# print(f"데이터차원: {da.shape}")
# print(f"데이터성분: {da.attrs}")
# print(f"데이터좌표: {da.coords}")
# print(f"관측 파장: {ds['FILTER'].values}")
# print(f"관측 장비: {ds['INSTRUME'].values}")
# print(f"관측 일자: {ds['DATE_OBS'].values}")




##plot

# import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
# import cartopy,crs as ccrs

# venus_globe=ccr.Globe(ellipse=None, semimajor_axis=6_051_800,semiminor_axis=6_051_800)

# # 탐사선 관측 위치
# lon_center=ds['S_SSCLON'].item()
# lat_center=ds['S_SSCLAT'].item()

# # 태양 위치
# sun_lon=ds['S_SOLLON'].item()
# sun_lat=ds['S_SOLLAT'].item()

# proj_data=ccrs.PlateCarree(globe=venus_globe)
# proj_view=ccrs.Orthographic(lon_center, lat_center, globe=venus_globe)

# fig,ax=plt.subplots(figsize=(9,5),subplot_kw={'projection':proj_data})
# da.plot(ax=ax,cmap='inferno',transform=proj_data,add_colorbar=False)
# ax.plot(sun_lon,sun_lat,marker='*',color='yellow',transform=proj_data)
# ax.gridlines(draw_labels=True)

# fig2=plt.figure(figsize=(10,10))
# ax2=plt.axes(projection=proj_view)
# da.plot(ax=ax2,
#         cmap='inferno',
#         transform=proj_data,
#         add_colorbar=True,
#         cbar_kwargs={
#           'orientation':'horizontal',
#           'pad':0.07,
#           'aspect':35
#         })

# ax2.plot(sun_lon,sun_lat,marker='*',color='yellow',transform=proj_data)
# ax2.gridlines(draw_labels=True)
# plt.show()
