# xRADIAL

Tools for converting ASCII Radial data (CODAR, WERA, and LERA) to `xarray` Datasets.

### High-Level Features

To create an `xarray` dataset from an ASCII CODAR or WERA file, use the `xradial.create_xarray_dataset()` function. The function takes three
required arguments:
  1. `fp`: A string (or path-like object) pointing at the ASCII data
  2. `time_var_str`: A string name of the time variable in the dataset
  3. `cf_time_units`: A string describing the CF-compliant time units, e.g. `seconds since 1970-01-01 00:00:00`

and one optional argument:
  1. `numerical_metadata`: A boolean, indicating whether to attempt conversion to numerical data types; __NOTE__ that some functions depend on numerical values in the metadata, and this is how the current implementation operates

Example:

```python
In [1]: import xradial.xradial as xrad                                                                                                                                                  

In [2]: path = "test/data/codar_ascii/RDL_m_Rutgers_AMAG_2018_02_14_0000.hfrss10lluv"                                                                                                   

In [3]: time_var = "time"                                                                                                                                                               

In [4]: cf_time_units = "seconds since 1970-01-01 00:00:00"                                                                                                                             

In [5]: ds = xrad.create_xarray_dataset(path, time_var, cf_time_units, True)                                                                                                            

In [6]: ds                                                                                                                                                                              
Out[6]: 
<xarray.Dataset>
Dimensions:  (BEAR: 72, RNGE: 49, time: 1)
Coordinates:
  * time     (time) datetime64[ns] 2018-02-14
  * BEAR     (BEAR) float64 4.0 9.0 14.0 19.0 24.0 ... 344.0 349.0 354.0 359.0
  * RNGE     (RNGE) float64 5.825 11.65 17.47 23.3 ... 267.9 273.8 279.6 285.4
...
```

### TODO
- module documentation
- inline docs with `Sphinx`
- CircleCI badge
