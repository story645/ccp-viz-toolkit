#!/usr/bin/env python
#
# urltranslate.py
#
# Hannah Aizenman, 2011-28-11

"""Functions for pulling kwargs out of the url"""

__docformat__ = "restructuredtext"

# http://docs.python.org/library/re.html 
import re

def get_kwargs_from_url(url_args):
    """
    Parses the url into its component kwargs.
    Assumes every kwarg field is seperated by /:
    root/kwarg1/kwarg2/...
    All kwargs are optional
    """
    # add support for ampersand notation or translate url down?
    kwargs = dict()
    # initial sorting-parsing is in url_to functions
    # in is used because it's much faster than re
    for arg in url_args:
        # labels goes first  because it's most likely to match the 
        # other if statements too
        if 'LABELS' in arg:
            kwargs['labels'] = url_to_labels(arg)
        elif 'ALG' in arg:
            kwargs['algorithm'] = arg.strip('ALG')
        elif (('T' and 'B' and 'L' and 'R') in arg) or (('T' and 'L') in arg):
            kwargs['coords'] = url_to_coords(arg)
        elif ('X' in arg) and ('Y' in arg):
            kwargs['data_reshape'] = url_to_reshape(arg)
        elif 'CDIM' in arg:
            kwargs['concat_dim'] = int(arg.strip('CDIM')) 
        elif arg[:4].isdigit():
            kwargs['time_range'] = url_to_time(arg)
        else:
            print("unknown arg: {!r}".format(arg))
    return kwargs
    
def url_to_time(arg):
    """Extracts the time_range kwarg from a url arg of the form:
        time1STtime2ED returns data between time1 and time2
        time1 returns the data at a single time point, 
        time1ST returns the data from time one until the last end point
        time2ED returns all the data up to time2
        time1 and time2 are of the form:
        YYYYMMDDHHMMDDmmmmmmm (where only year is required)
    """
    time_range = dict()
    dt_str = [r'(?P<year>[0-2]?\d{3}-?)',
              '(?P<month>[0-1][0-2]-?)?',
              '(?P<day>[0-3]\d)?',
              '(?P<hour>T?[0-2]\d)?',
              '(?P<minute>[0-5]\d:?)?',
              '(?P<second>[0-5]\d:?)?',
              '(?P<microsecond>[0-1]\d{0,6})?']              
    dt_regex = re.compile(''.join(dt_str))
    dt_found = dt_regex.findall(arg)
    int_dates = [convert_list_to_int(dt_list, 'T-:') for dt_list in dt_found]    
    
    if ('ST' in arg) and ('ED' in arg):
        time_range['start'] = int_dates[0]
        time_range['end'] = int_dates[1]
    elif 'ST' in arg:
        time_range['start'] = int_dates[0]
    elif 'ED' in arg:
        time_range['end'] = int_dates[0]
    elif int_dates:
        time_range['start'] = int_dates[0]
        time_range['end'] = int_dates[0]
    return time_range

def url_to_coords(arg):
    """Extracts the coords kwargs dict from a url arg of the form:
        lat1NTlat2SBlon1WLlon2ER
        where only latTlonL is required
    """
    latstr = '[-]?\d{1,2}((\d{2})?(\d{2})?)?(\.\d{0,2})?([NS])?'
    lonstr = '[-]?\d{1,3}((\d{2})?(\d{2})?)?(\.\d{0,2})?([WE])?'
    grid_str = [''.join(['(', '?P', '<top>', latstr, 'T', ')']),
                ''.join(['(', '?P', '<bottom>', latstr, 'B', ')', '?']),     
                ''.join(['(', '?P', '<left>', lonstr, 'L', ')']),
                ''.join(['(', '?P', '<right>', lonstr, 'R', ')', '?'])]
                
    grid_regex = re.compile(''.join(grid_str))
    grid_found = grid_regex.match(arg)
    
    coords = dict()
    for key in grid_found.groupdict():
        if grid_found.group(key): # checks for null keys
            # str strips away 'u
            coords[key] = grid_found.group(key).strip('TBLR')
            
    if not grid_found.group('bottom'):
        coords['bottom'] = coords['top']
    if not grid_found.group('right'):
        coords['right'] = coords['left']
    
    return coords
    
def url_to_reshape(arg):
    """Extracts the reshape kwarg from a url arg of the form:
       XtimeYlatlon or XS1YS2ZS3
       S1, S2 and S3 are digits and ZS3 is optional
    """
    
    if re.match('XtimeYlatlon', arg, re.IGNORECASE):
        return ('time', 'latlon')
    
    rs_dict = re.match('(?P<X>X\d+)(?P<Y>Y\d+)(?P<Z>\d+)?', arg)
    int_dict = convert_dict_to_int(rs_dict.groupdict(), 'XYZ')
        
    if num_elem == 3:
        return (int_dict['X'], int_dict['Y'], int_dict['Z'])
    elif num_elem == 2:
        return (int_dict['X'], int_dict['Y'])
    elif num_elem == 1:
        return (int_dict['X'])
    
def url_to_labels(arg):
    """Extracts label kwargs from a url arg of the form:
        LABELS0S01S12S23S3
        where any field is optional and S are strings. 
    """
    
    lab_str = ['LABELS',
               '(?P<title>0\w+0)?',
               '(?P<xlabel>1\w+1)?',
               '(?P<ylabel>2\w+2)?',
               '(?P<cblabel>3\w+3)?']
    lab_regexp = re.compile(''.join(lab_str))
    lab_found = lab_regexp.match(arg)
    labels = dict()
    for key in lab_found.groupdict():
        if lab_found.group(key):
            labels[key] = labelclean(lab_found.group(key)[1:-1])
    return labels

def labelclean(label):
    """replaces + with " " per html convention
    """
    return label.replace("+"," ")
    
def convert_list_to_int(unicode_list, chars):
    """Converts unicode values in a list to integers
    """
    return [int(u.strip(chars)) for u in unicode_list if u]
            
def convert_dict_to_int(unicode_dict, chars):
    """Converts unicode values in a dict to integers
    :Param unicode_dict:
        dictionary of values that need to be converted
    :Param strip:
        string of characters to be stripped out
    """
    int_dict = dict()
    for key in unicode_dict:
        if unicode_dict[key]:
            int_dict[key] = int(unicode_dict[key].strip(chars))
    return int_dict

