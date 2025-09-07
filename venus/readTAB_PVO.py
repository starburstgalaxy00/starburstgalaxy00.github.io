file_lbl = '2001_OIMS_ION_DENS_HR.LBL'
file_tab = '2001_OIMS_ION_DENS_HR.TAB'

import pvl
import pandas as pd

lbl = pvl.load(file_lbl)
all_columns = lbl['TABLE'].getlist('COLUMN')
col_names = [col['NAME'] for col in all_columns]
col_widths = [col['BYTES'] for col in all_columns]
col_widths[0] = 16

df = pd.read_fwf(file_tab, widths=col_widths, header=None, names=col_names)
