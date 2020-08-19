# LDI
Lumerical Data format importing schemes! 
Contains the main LDI file (LumericalDataImport.py) and also som QofL functions for console printing, file categorisation, json settings exporting and importing (and eventually more) with some additional functions in AuxFuct.py

Keep in mind, this project is VERY EARLY in development, and will likely never be fully finished unless I somehow end up using all parts of lumerical at least once!

The general goal of this project is to (eventually) support importing data from most of the lumerical monitors without the need for manual tweaking, and then feature analysis functions that mirror that of the Lumerical suite.

Current functions in AuxFunct (same as help(AuxFunct), but still incomplete):
 
 
 FUNCTIONS
    AbsPowIntegrator(Data, x, y, z, WL)
        "A function that uses a RectBivariateSpline function to determine the total absorbed power from a pabs_adv lumerical file."
        Calculating total power absorption as a power fraction:s
        Lumerical initially gives P_abs in terms of W/m^3, but then converts it by dividing by the source power - which is why the values are seemingly massive. 
        SP   = meshgrid4d(4,x,y,z,sourcepower(f));
        Pabs = Pabs / SP;
        
        If we then look inside the P_abs_tot analysis group script, we can see that this simply becomes an integration over each 2d slice:
        Pabs_integrated = integrate2(Pabs,1:3,x,y,z);
        We could simply export Pabs_tot, but I think we get more control if we do it manually, and we also save data!
    
    CUV(**kwargs)
    
    Get_FileList(path, **kwargs)
        A function that gives you a list of filenames from a specific folder
        path = path to files. Is relative unless you use kwarg pathtype = 'abs'
        kwargs**:
            pathtype: enum in ['rel','abs'], default = 'rel'. Allows you to manually enter absolute path    
            ext: file extension to look for, use format '.txt'. You can use a list e.g. ['.txt','.mat','.png'] to collect multiple files. Default is all files
            sorting: "alphabetical" or "numeric" sorting, default is "alphabetical"
    
    MatLoader(file, **kwargs)
    
    PathSet(filename, **kwargs)
        "
        p/pt/pathtype in [rel,relative,abs,absolute]
        Note that rel means you input a relative path, and it auto-completes it to be an absolute path, 
        whereas abs means that you input an absolute path!
    
    cprint(String, **kwargs)
            Note that some light colour variations do not work on all terminals! To get light colours on style-inedpendent terminals, you can use ts = bold!
            kwargs:
            
            mt: Message type - a string that defines one from a list of preset message formats. 
                List of acceptable entries: ['err','error','note','warning','caution','wrn','curio','status','stat','custom']. Note: only custom supports further kwargs
            fg: Foreground colour - a string with the full name or abbrviation of a colour to give to the text.
                List of acceptable entries: ['black','k','red','r','green','g','orange','o','blue','b','purple','p','cyan','c','lightgrey','lg',
                                             'darkgrey','dg','lightgreen','lgr','yellow','y','lightblue','lb','pink','pk','lightcyan','lc']
                                            Note that some light colours are accessed using bold style instead of this!
            bg: Background colour - a string with the full name or abbrviation of a colour to highlight text with.
                List of acceptable entries: ['black','k','red','r','green','g','orange','o','blue','b','purple','p','cyan','c','lightgrey','lg']
            ts: Text Style - a string indicating what style to apply to the text. Some do not work as intended.
                List of acceptable entries: ['bold','b','italic','it','underline','ul','strikethrough','st','reverse','rev','disable','db','invisible','inv']
            sc: StartCode - A custom startcode if you want to use specific colours not listed in the code. 
                Note: overwrites any bs/fg inputs, is compatible only with "custom" message type, but supports text style ts kwargs!
            jc: Join character - This is the character that will join the strings in a list together, recommend '
        ' or ' ' but anything works 
            cprint also supports lists with different styles and options applied. Use:
                cprint([string1,string2],fg = [fg1,fg2],bg = [bg1,bg2],ts = [ts1,ts2])
            tr: textreturn - returns the escape character strng instead - does not produce a print output!
            co: console output - a global variable if you want an option to disable console ouput throughout your code!
                list of acceptable entries: [True,False], default: False
    
    jsonhandler(**kwargs)
        #%%
    
    maxRepeating(str, **kwargs)
        DESCRIPTION.
        A function used to find and count the max repeating string, can be used to guess
        Parameters
        ----------
        str : TYPE
            DESCRIPTION.
        **kwargs : 
            guess : TYPE = str
            allows you to guess the escape character, and it will find the total number of that character only!
        
        Returns
        -------
        res,coount
        Character and total number consecutive


