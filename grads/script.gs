* grads -lbc "/home/ccmmma/prometeo/opt/ccmmmaapi/grads/script.gs /tmp/control.ctl 14.13 40.79 14.35 40.92 com63049 d03 wrf5 gen /data1/ccmmma/prometeo/www/images/com63049_wrf5_20181003Z1100_gen_1024x768.png true|false"

function main(args)
  'reinit'
  say "script.gs " args
* Get arguments
  if (args='?')
    say 'script.gs requires 15 argument: controlfile minLon minLat maxLon maxLat place domain product output width height imagepath tempdir bars=true|false label'
    return
  endif

  controlFile=subwrd(args,1)
  minLon=subwrd(args,2)
  minLat=subwrd(args,3)
  maxLon=subwrd(args,4)
  maxLat=subwrd(args,5)
  place=subwrd(args,6)
  domain=subwrd(args,7)
  product=subwrd(args,8)
  output=subwrd(args,9)
  _xdim=subwrd(args,10)
  _ydim=subwrd(args,11)
  imagepath=subwrd(args,12)
  tempdir=subwrd(args,13)
  _bars=subwrd(args,14)
  _label=""
  
  count = 15
  part=subwrd(args,count)
  while (part != "") 
    if (_label!="")
      _label=_label' '
    endif

    _label=_label''part
    count = count + 1 
    part=subwrd(args,count)
  endwhile

  _label=_label' ('place'/'product')'

  pi  = 3.1415926
  d2r = pi/180
  r2d = 1/d2r

  _place=place
  _first2c='ca'
  _mode='grads'
*  _label=place
  
* Set the defaul landMask option  
  _landMask=0
  _first2c = substr(place,1,2)
  if (product= 'ww33' | product= 'rms3' | product= 'wcm3' | product= 'aiq3' | _first2c = 'po' | _first2c = 'me' | _first2c = 'xx' | _first2c = 'II' | _first2c = 'VE')
    _landMask=1
  endif
  if (product= 'rdr1' | product= 'rdr2')
    _landMask=2
  endif

  dLon=maxLon-minLon
  dLat=maxLat-minLat

  R = 6371
  dLatR = dLat * d2r
  dLonR = dLon * d2r 

  a = math_sin( dLatR / 2 ) * math_sin( dLatR / 2 ) + math_cos( minLat * d2r ) * math_cos( maxLat * d2r ) * math_sin( dLonR / 2 ) * math_sin( dLonR / 2 ) 
  c = 2 * math_atan2(math_sqrt(a), math_sqrt(1-a))
  d = R * c

  skp=calcSkip(product,domain,d)
  slpCint=1

  'open 'controlFile

  if (product='wrf5')
    if (output = 'cld')
      wrf5MapCld(tempdir,minLon,minLat,maxLon,maxLat)
    endif

    if (output = 'crh')
      wrf5MapCrh(tempdir,minLon,minLat,maxLon,maxLat)
    endif

    if (output = 'crd')
      wrf5MapCrd(tempdir,minLon,minLat,maxLon,maxLat)
    endif

    if (output = 'gen')
      wrf5MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'gp5')
      wrf5MapGp5(tempdir,minLon,minLat,maxLon,maxLat)
    endif

    if (output = 'gp8')
      wrf5MapGp8(tempdir,minLon,minLat,maxLon,maxLat)
    endif

    if (output = 'tsp')
      wrf5MapTsp(tempdir,minLon,minLat,maxLon,maxLat,slpCint)
    endif

    if (output = 'wnd')
      wrf5MapWnd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'wn1')
      wrf5MapWn1(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'wn2')
      wrf5MapWn2(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'wn3')
      wrf5MapWn3(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'rh2')
      wrf5MapRh2(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'tc2')
      wrf5MapTc2(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'rh3')
      wrf5MapRh300(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'tc3')
      wrf5MapTc300(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'rh5')
      wrf5MapRh500(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'tc5')
      wrf5MapTc500(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'rh7')
      wrf5MapRh700(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'tc7')
      wrf5MapTc700(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'rh8')
      wrf5MapRh850(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'tc8')
      wrf5MapTc850(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'r95')
      wrf5MapRh925(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 't95')
      wrf5MapTc925(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'rh9')
      wrf5MapRh950(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'tc9')
      wrf5MapTc950(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'r97')
      wrf5MapRh975(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 't97')
      wrf5MapTc975(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'r10')
      wrf5MapRh1000(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif
      
    if (output = 't10')
      wrf5MapTc1000(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'swe')
      wrf5MapSwe(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif
  endif

  if (product='rms3')
    if (output = 'gen')
      rms3MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'sst')
      rms3MapSst(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'sss')
      rms3MapSss(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'ssh')
      rms3MapSsh(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'bar')
      rms3MapBar(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif
  endif

  if (product='ww33')
    if (output = 'gen') 
      ww33MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'hsd') 
      ww33MapHsd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'lmd') 
      ww33MapLmd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'fpd') 
      ww33MapFpd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'ppd') 
      ww33MapPpd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif
  endif

  if (product='wcm3')
    if (output = 'con')
      wcm3MapCon(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'gen')
      wcm3MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif
  endif

  if (product='aiq3')
    if (output = 'mci')
      aiq3MapMci(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif

    if (output = 'gen')
      aiq3MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif
  endif

  if (product='rdr1' | product='rdr2')
    if (output = 'gen')
       rdrXMapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
     endif

     if (output = 'rdr')
       rdrXMapRdr(tempdir,minLon,minLat,maxLon,maxLat,skp)
     endif

     if (output = 'ref')
       rdrXMapRef(tempdir,minLon,minLat,maxLon,maxLat,skp)
    endif    
  endif

  '!cp 'tempdir'/output.png 'imagepath
  quit
return

*-------------- start function minmax() --------------------
**********************************
function minmax(var)
**********************************

*-- set graphic type to stat (= statistics)
'set gxout stat'

*-- display data variable expression
'd 'var

*-- write the statistics output to the variable ret
ret = result

strFirst1 = sublin(ret,1)
strFirst2 = subwrd(strFirst1,1)

if ( strFirst2 = "Notice:")
  nLine = 9
else
  nLine = 8
endif

*-- read line 8 from the result variable ret, holding min and max
line = sublin(ret,nLine)

*-- get minimum and maximum values of data variable expression
dmin = subwrd(line,4)
dmax = subwrd(line,5)


*-- return both, min and max
return dmin' 'dmax

*-------------- end function minmax() --------------------

function calcSkip(product,domain,d)
  if ( product = 'rms3' )
    skp=20

    if ( domain = 'd01' )
    skp=18
    slpCint=5
    if ( d >= 0 & d<240 )
      skp=2
    else
      if ( d>=240 & d<480)
        skp=6
      else
        skp=18
      endif
    endif
  else
    if (domain = 'd02' )
      skp=1
      slpCint=2
      if ( d >= 0 & d<60 )
        skp=2
      else
        if ( d >=60 & d<240 )
          skp=4
        else
          if ( d>=240 & d<480)
            skp=8
          else
            skp=16
          endif
        endif
      endif
    else
      if ( domain = 'd03' )
        slpCint=1
        if ( d >= 0 & d<30 )
*          skp=1
          skp=2
        else
          if ( d >=30 & d<60 )
*            skp=1
            skp=7
          else
            if ( d>=60 & d<120 )
*              skp=3
             skp=10
            else
              if ( d>=120 & d<240)
*                skp=4
               skp=20
              else
                if ( d>=240 & d<480)
*                  skp=15
                 skp=30
                else
*                  skp=25
                  skp=35
                endif
              endif
            endif
          endif
        endif
      else
        if ( domain = 'd04' )
          slpCint=1
          if ( d >= 0 & d<5 )
            skp=1
          else
            if ( d >=5 & d<10 )
              skp=2
            else
              if ( d>=10 & d<20 )
                skp=5
              else
                if ( d>=20 & d<50)
                  skp=10
                else
                  if ( d>=50 & d<100)
                    skp=15
                  else
                    skp=25
                  endif
                endif
              endif
            endif
          endif
        endif
      endif
    endif
  endif
  endif
  if ( product = 'wrf5' )
    skp=20
  if ( domain = 'd01' )
    skp=18
    slpCint=5
    if ( d >= 0 & d<240 )
      skp=2
    else
      if ( d>=240 & d<480)
        skp=6
      else
        skp=18
      endif
    endif
  else
    if (domain = 'd02' )
      skp=6
      slpCint=2
      if ( d >= 0 & d<60 )
        skp=2
      else
        if ( d >=60 & d<240 )
          skp=4
        else
          if ( d>=240 & d<480)
            skp=8
          else
            skp=16
          endif
        endif
      endif
    else
      if ( domain = 'd03' )
        slpCint=1
        if ( d >= 0 & d<30 )
          skp=1
        else
          if ( d >=30 & d<60 )
            skp=2
          else
            if ( d>=60 & d<120 )
              skp=6
            else
              if ( d>=120 & d<240)
                skp=8
              else
                if ( d>=240 & d<480)
                  skp=10
                else
                  skp=12
                endif
              endif
            endif
          endif
        endif
      else
        if ( domain = d04 )
          slpCint=1
          if ( d >= 0 & d<5 )
            skp=1
          else
            if ( d >=5 & d<10 )
              skp=2
            else
              if ( d>=10 & d<20 )
                skp=5
              else
                if ( d>=20 & d<50)
                  skp=10
                else
                  if ( d>=50 & d<100)
                    skp=15
                  else
                    skp=25
                  endif
                endif
              endif
            endif
          endif
        endif
      endif
    endif
  endif
  endif
  if ( product = 'ww33' )
    skp=20
  if ( domain = 'd01' )
    skp=18
    slpCint=5
    if ( d >= 0 & d<240 )
      skp=2
    else
      if ( d>=240 & d<480)
        skp=6
      else
        skp=18
      endif
    endif
  else
    if (domain = 'd02' )
      skp=6
      slpCint=2
      if ( d >= 0 & d<60 )
        skp=2
      else
        if ( d >=60 & d<240 )
          skp=4
        else
          if ( d>=240 & d<480)
            skp=8
          else
            skp=16
          endif
        endif
      endif
    else
      if ( domain = 'd03' )
        slpCint=1
        if ( d >= 0 & d<30 )
          skp=1
        else
          if ( d >=30 & d<60 )
            skp=2
          else
            if ( d>=60 & d<120 )
              skp=6
            else
              if ( d>=120 & d<240)
                skp=8
              else
                if ( d>=240 & d<480)
                  skp=10
                else
                  skp=12
                endif
              endif
            endif
          endif
        endif
      else
        if ( domain = d04 )
          slpCint=1
          if ( d >= 0 & d<5 )
            skp=1
          else
            if ( d >=5 & d<10 )
              skp=2
            else
              if ( d>=10 & d<20 )
                skp=5
              else
                if ( d>=20 & d<50)
                  skp=10
                else
                  if ( d>=50 & d<100)
                    skp=15
                  else
                    skp=25
                  endif
                endif
              endif
            endif
          endif
        endif
      endif
    endif
  endif
  endif
return skp

function drawHead(minLon,minLat,maxLon,maxLat)
  
  clear
  if (_bars='true')
    'set parea 2 9.3 1.1 7.5'
  endif
  'set grads off'
  'set mpt * off'
  'set LON ' minLon ' ' maxLon
  'set LAT ' minLat ' ' maxLat
  'set T 1'
  'query time'
  strTime = subwrd(result,3)
  drawLabels(strTime )
return

function drawLabels(labels)

  strTime = subwrd(labels,1)
  if (_landMask = 2)
  'set strsiz 0.15'
  'draw string 1 7.9 Date: ' strTime ' ' _label
  'set strsiz 0.2'
*  'draw string 0.05 0.2 http://meteo.uniparthenope.it'
  'draw string 6 8.2 http://meteo.uniparthenope.it'
  else
  'set strsiz 0.15'
  'draw string 1 7.9 Forecast: ' strTime ' ' _label
  'set strsiz 0.2'
*  'draw string 0.05 0.2 http://meteo.uniparthenope.it'
  'draw string 6 8.2 http://meteo.uniparthenope.it'
  endif
return

function drawGrADSMap()
   if (_mode = 'grads')
     if (_landMask = 1)
       'set rgb 16 217 217 217'
       'set shpopts 16'
     endif
     if (_landMask = 2)
       'set rgb 16 217 217 217'
       'set shpopts 16'
     endif

     'draw shp europe'
     'draw shp Africa'

     if (_landMask = 1 & _first2c = 'VE')
       'set shpopts 2 6 0.2'
       'draw shp Sorgenti_agg_feb2022'
     endif
     
    if (_place = 'com6304901' | _place = 'com6304902' | _place = 'com6304903' | _place = 'com6304904' | _place = 'com6304905' | _place = 'com6304906' | _place = 'com6304907' | _place = 'com6304908' | _place = 'com6304909' | _place = 'com6304910')
       'draw shp Napoli_Municipalità'
    endif

   endif
 return

function wrf5MapCld(tempdir,minLon,minLat,maxLon,maxLat)
    drawHead(minLon,minLat,maxLon,maxLat )
    drawClouds()
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapCrh(tempdir,minLon,minLat,maxLon,maxLat)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawClouds()
    drawRain2()
    drawUH()
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapCrd(tempdir,minLon,minLat,maxLon,maxLat)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRainDaily()
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawClouds()
    drawRain2()
    drawSnow()
    drawWind(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapGp5(tempdir,minLon,minLat,maxLon,maxLat)
   drawHead(minLon,minLat,maxLon,maxLat)
   drawGeopt500()
   drawGrADSMap()
   'run cbar 1'
   'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapGp8(tempdir,minLon,minLat,maxLon,maxLat)
   drawHead(minLon,minLat,maxLon,maxLat)
   drawGeopt850()
   drawGrADSMap()
   'run cbar 1'
   'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTsp(tempdir,minLon,minLat,maxLon,maxLat,slpCint)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTempSlp(slpCint)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapWn1(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawWind1(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapWn2(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawWind2(skp)
    drawGrADSMap()
    'run cbar 1'
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapWn3(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawWind3(skp)
    drawGrADSMap()
    'run cbar 1'
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapWnd(tempdir,minLon,minLat,maxLon,maxLat,skp)

    drawHead(minLon,minLat,maxLon,maxLat)
    drawWind(skp)
    drawGrADSMap()
    'run cbar 1'
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh2(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRh2(skp)
    drawWind(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTc2(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(mindLon,minLat,maxLon,maxLat)
    drawTc2(skp)
    drawWind(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh300(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRhByVars(skp,rh300,'300 hPa')
    drawWindByVars(skp,u300,v300)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

   function wrf5MapTc300(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTcByVars(skp,tc300,'300 hPa')
    drawWindByVars(skp,v300,u300)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh500(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRhByVars(skp,rh500,'500 hPa')
    drawWindByVars(skp,u500,v500)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTc500(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTcByVars(skp,tc500,'500 hPa')
    drawWindByVars(skp,u500,v500)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh700(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRhByVars(skp,rh700,'700 hPa')
    drawWindByVars(skp,u700,v700)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTc700(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTcByVars(skp,tc700,'700 hPa')
    drawWindByVars(skp,u700,v700)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh850(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRhByVars(skp,rh850,'850 hPa')
    drawWindByVars(skp,u850,v850)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTc850(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTcByVars(skp,tc850,'850 hPa')
    drawWindByVars(skp,u850,v850)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh925(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRhByVars(skp,rh925,'925 hPa')
    drawWindByVars(skp,u925,v925)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTc925(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTcByVars(skp,tc925,'925 hPa')
    drawWindByVars(skp,u925,v925)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh950(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRhByVars(skp,rh950,'950 hPa')
    drawWindByVars(skp,u950,v950)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTc950(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTcByVars(skp,tc950,'950 hPa')
    drawWindByVars(skp,u950,v950)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh975(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRhByVars(skp,rh975,'975 hPa')
    drawWindByVars(skp,u975,v975)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTc975(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTcByVars(skp,tc975,'975 hPa')
    drawWindByVars(skp,u975,v975)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapRh1000(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRhByVars(skp,rh1000,'1000 hPa')
    drawWindByVars(skp,u1000,v1000)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapTc1000(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawTcByVars(skp,tc1000,'1000 hPa')
    drawWindByVars(skp,u1000,v1000)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wrf5MapSwe(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawSnow()
    drawWind(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function rms3MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawCur(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function rms3MapSst(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawSst(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function rms3MapSss(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawSss(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function rms3MapSsh(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawSsh(skp)
    drawGrADSMap()
    'run cbar 1'
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function rms3MapBar(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawBar(skp)
    drawGrADSMap()
    'run cbar 1'
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function ww33MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawHs(skp)
    drawLm(skp,'contour')
    drawDir(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function ww33MapHsd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawHs(skp)
    drawDir(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function ww33MapLmd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawLm(skp,'shaded')
    drawDir(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function ww33MapFpd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawFp(skp,'shaded')
    drawDir(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function ww33MapPpd(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawPp(skp,'shaded')
    drawDir(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wcm3MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawConc(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function wcm3MapCon(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawConc(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function aiq3MapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawMci(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function aiq3MapCon(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawMci(skp)
    drawGrADSMap()
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function rdrXMapGen(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRdr()
    drawGrADSMap()
    'set rbcols'
    'set gxout shaded'
    'run crhBars.gs'
    'd rain'
    'draw shp europe'
    'set line 3 1'
    'draw shp roads_type__motorway'
    'set line 1 1'
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function rdrXMapRdr(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRdr()
    drawGrADSMap()
    'set rbcols'
    'set gxout shaded'
    'run crhBars.gs'
    'd rain'
    'draw shp europe'
    'set line 3 1'
    'draw shp roads_type__motorway'
    'set line 1 1'
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function rdrXMapRef(tempdir,minLon,minLat,maxLon,maxLat,skp)
    drawHead(minLon,minLat,maxLon,maxLat)
    drawRef()
    drawGrADSMap()
    'set rbcols'
    'set gxout shaded'
    'run refBars.gs'
    'd reflectivity'
    'draw shp europe'
    'set line 3 1'
    'draw shp roads_type__motorway'
    'set line 1 1'
    'printim 'tempdir'/output.png x'_xdim' y'_ydim' white'
return

function drawRdr()
  'set rbcols'
  'set gxout shaded'
  'run crhBars.gs'
  'd rain'
  'set rbcols'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Rain rate [mm/h]'
  endif
*  'set line 2'
*  'draw shp roads_type__motorway'
*  'set line 1'
return

function drawRef()
  'set rbcols'
  'set gxout shaded'
  'run refBars.gs'
  'd reflectivity'
  'set rbcols'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Reflectivity [dBZ]'
  endif
*  'set line 2'
*  'draw shp roads_type__motorway'
*  'set line 1'
return

function drawConc(skp)
'set gxout shaded'
'run concBars.gs'
'set Z 1'
'd conc'
*'set gxout contour'
*'d conc'
if (_bars='true')
      'run xcbar.gs 10.1 10.3 1.7 7.0 -line on -edge triangle -fw 0'
      'set string 1 c 6 90'
      'set strsiz 0.13'
      'draw string 9.9 4.2 Concentration [N. of particles]'
      'set strsiz 0.08'
      'draw string 10.4 6.7 Forbidden'
      'draw string 10.4 5.85 Very High'
      'draw string 10.4 5.1 High'
      'draw string 10.4 4.35 Medium'
      'draw string 10.4 3.6 Low'
      'draw string 10.4 2.8 Very Low'
      'draw string 10.4 2 Absent'
endif
if (_landMask = 1 & _first2c = 'VE')
  'set line 2'
*  'draw shp ImpiantiNewWGS84'
*  'draw shp Molluschi2019_WGS84'
*'draw shp Shapefile_fonti_soloContinue'
  'draw shp Banchi_agg_feb2022'
endif
'set line 1'
return

function drawMci(skp)
'set gxout shaded'
'run mciBars.gs'
'set Z 1'
'd class_predict'
if (_bars='true')
      'run xcbar.gs 10.1 10.3 1.7 7.0 -line on -edge triangle -fw 0'
      'set string 1 c 6 90'
      'set strsiz 0.13'
      'draw string 9.9 4.2 Mussel Contamination Index (predicted)'
      'set strsiz 0.08'
*     'draw string 10.4 6.7 Forbidden'
      'draw string 10.4 6.5 Critical'
      'draw string 10.4 5.7 Very High'
      'draw string 10.4 4.7 High'
      'draw string 10.4 3.9 Medium'
      'draw string 10.4 3.0 Low'
      'draw string 10.4 2.1 Absent'
endif
if (_landMask = 1 & _first2c = 'VE')
  'set line 2'
  'draw shp Banchi_agg_feb2022'
endif
'set line 1'
return

function drawBar(skp)
'set rbcols'

  'curBars'

  'set gxout shaded'
  'cs=mag(ubar,vbar)'
  'display cs'
  'set rbcols'
  'set gxout vector'
  'set arrowhead 0.05'
  'set arrscl 0.125 1'
  'display skip(ubar/cs,'skp','skp');vbar/cs'
return

function drawSss(skp)
  'set rbcols'

  'saltBars'
  'set Z 1'
  'set gxout shaded'
  'display salt'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Sea Surface Salinity [1/1000]'
  endif

return

function drawSsh(skp)
  'set rbcols'

  'zetaBars'
  'set Z 1'
  'set gxout shaded'
  'display zeta'
  'cbarm'
return

function drawSst(skp)
  'set rbcols'

  'tempBars'
  'set Z 1'
  'set gxout shaded'
  'display temp'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Sea Surface Temperature [C]'
    endif

return

function drawCur(skp)
  'set rbcols'

  'curBars'
  'set Z 1'
  'set gxout shaded'
  'cs=mag(u,v)'
  'display cs'
  'set rbcols'
  'set gxout vector'
  'set arrowhead 0.05'
  'set arrscl .125 1'
  'display skip(u/cs,'skp','skp');v/cs'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Sea Surface Current [m/s]'
    endif
return

function drawHs(skp)
  'set rbcols'
  'hsBars'
  'set Z 1'
  'set gxout shaded'
  'display hs'
  
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Significant wave height [m]'
  endif
 
return

function drawLm(skp, mode)
  'set rbcols'
   
  'set Z 1'

  if (mode='shaded')
    'lmBars'
    'set gxout shaded'
  else
    'set ccolor 1'
    'set gxout contour'
  endif

  'display lm'

  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Mean wave length [m]'
  endif

return

function drawFp(skp,mode)
  'set rbcols'
  
  'set Z 1'

  if (mode='shaded')
    'fpBars'
    'set gxout shaded'
  else
    'set ccolor 1'
    'set gxout contour'
  endif

  'display fp'

  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Wave peak frequency [s-1]'
  endif
return

function drawDir(skp)
  'set rbcols'
  'set Z 1'
  'set gxout vector'
  'set arrowhead 0.05'
  'set arrscl .125 1'
  
*  'set cthick 3'
*  'set arrscl 0.25'
  'set arrlab off'
  'set ccolor 1'

  'd skip(cos((dir-180)*0.0174533),'skp');skip(sin((dir-180)*0.0174533),'skp')'
return

function drawPp(skp, mode)
  'set rbcols'

  'ppBars'
  'set Z 1'
  
  if (mode='shaded')
    'ppBars'
    'set gxout shaded'
  else
    'set ccolor 1'
    'set gxout contour'
  endif

  'display period'
  
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Mean wave period [s]'
  endif  
  
return

function drawTempSlp(slpCint)
  'set rbcols'

  'run tspBars.gs'

  'set gxout shaded'
  'display t2c'
  'set gxout contour'
  'set cint 'slpCint
  'set ccolor 3'
  'display slp'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Air Temperature at 2m [C]'
  endif


return

function drawTcByVars(slpCint,tc, level)
  'set rbcols'

  'run tc2Bars.gs'

  'set gxout shaded'
  'display 'tc
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Temperature in Celsius at 'level' [°]'
  endif

return

function drawRhByVars(slpCint,rh, level)
  'set rbcols'

  'run rh2Bars.gs'

  'set gxout shaded'
  'display 'rh
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Relative Humidity at 'level' [%]'
  endif

return

function drawRh2(slpCint)
  'set rbcols'

  'run rh2Bars.gs'

  'set gxout shaded'
  'display rh2'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Temperature in Celsius at 2m [°]'
  endif

return

function drawTc2(slpCint)
  'set rbcols'

  'run tc2Bars.gs'

  'set gxout shaded'
  'display t2c'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Relative Humidity at 2m [%]'
  endif

return

function drawGeopt500()
 'run define_colors.gs'
 'set grads off'
 'set gxout contour'
 'set rbcols'
 'display gph500'
return

function drawGeopt850()
 'run define_colors.gs'
 'set grads off'
 'set gxout contour'
 'set rbcols'
 'display gph850'
return

function drawSnow()
  hSnowMinMax = minmax('hourly_swe')
  hSnowMin = subwrd(hSnowMinMax,1)
  hSnowMax = subwrd(hSnowMinMax,2)

  if (hSnowMin != hSnowMax)
  'run snwBars.gs'
  'set grads off'
  'set gxout shaded'
*  'display delta_rain*(sr-0.75)*5'
  'display hourly_swe'

  if (_bars='true')
    'run xcbar.gs 1.5 9.5 0.5 0.7 -line on -edge triangle'
    'set string 1 c 6 0'
*   'draw string 5.5 0.2 Snow water equivalent [kg m-2]'
    'draw string 5.5 0.2 Snow [cm]'
  endif 

endif

return

function drawClouds()
  clfTotalMinMax = minmax('clf_total')
  clfTotalMin = subwrd(clfTotalMinMax,1)
  clfTotalMax = subwrd(clfTotalMinMax,2)
  if (clfTotalMin != clfTotalMax)
    'set gxout shaded'
    'run cldBars.gs'
    'set cmin 0.10'
    'display clf_total'
    if (_bars='true')
      'run xcbar.gs 0.5 0.7 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 0.2 4 Cloud fraction [%]'
    endif
  endif
return

function drawRain2()
  dRainMinMax = minmax('delta_rain')
  dRainMin = subwrd(dRainMinMax,1)
  dRainMax = subwrd(dRainMinMax,2)

  if (dRainMin != dRainMax)
    'run crhBars.gs'
    'set grads off'
    'set gxout shaded'
    'display delta_rain'
    if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Hourly Rain [mm]'
    endif
  endif

return

function drawRainDaily()
  dailyRainMinMax = minmax('daily_rain')
  dailyRainMin = subwrd(dailyRainMinMax,1)
  dailyRainMax = subwrd(dailyRainMinMax,2)

  if (dailyRainMin != dailyRainMax)
    'run crdBars.gs'
    'set grads off'
    'set gxout shaded'
    'display daily_rain'
    if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Cumulated Daily Rain (24h) [mm]'
    endif
  endif

return

function drawUH()
  UHMinMax = minmax('uh')
  UHMin = subwrd(UHMinMax,1)
  UHMax = subwrd(UHMinMax,2)

  if (UHMin != UHMax)
    'run uhBars.gs'
    'set grads off'
    'set gxout shaded'
    'display (uh)'
    if (_bars='true')
      'run xcbar.gs 1.5 9.5 0.5 0.7 -line on -edge triangle'
      'set string 1 c 6 0'
      'draw string 5.5 0.2 Updraf Helicity [m2/s2]'
    endif
  endif

return

function drawWindByVars(skp,uu,vv)
  'set rbcols'
  'set gxout barb'

  'set ccolor 1'
  'display skip('uu'*1.94,'skp','skp');'vv'*1.94'
return

function drawWind(skp)
  'set rbcols'
  'set gxout barb'

  'set ccolor 1'
  'display skip(u10m*1.94,'skp','skp');v10m*1.94'
return

function drawWind1(skp)

  'set rbcols'
  'run wn1Bars.gs'

  'set gxout shaded'
  'display ws10*1.94'
  'set rbcols'
  'set gxout vector'
  'set arrowhead 0.03'
  'set arrscl 0.2 1'
  'display skip(u10m/ws10,'skp','skp');v10m/ws10'
  if (_bars='true')
      'run xcbar.gs 10.2 10.4 1.5 7.0 -line on -edge triangle'
      'set string 1 c 6 90'
      'draw string 10 4 Wind speed [knt]'
    endif
return

function drawWind2(skp)
  'set gxout shaded'
  'display delta_ws10*1.94'
  'set gxout contour'
  'display delta_wd10'
  'set rbcols'

  'run wn2Bars.gs'

return

function drawWind3(skp)
  'set rbcols'
  'run wn3Bars.gs'

  'set gxout shaded'
  'b=pow((ws10/0.836),(2/3))'
  'display b'
  'set rbcols'
  'set gxout vector'
  'set arrowhead 0.03'
  'set arrscl 0.2 1'
  'display skip(u10m/ws10,'skp','skp');v10m/ws10'
return
