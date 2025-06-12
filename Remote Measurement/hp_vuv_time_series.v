menu 'Repeat Acquire' ;

{ Variables }
var
  TempStr1 ;
  DisplayMode1 ;
  NumFrames1 ;
  DataReady1 ;
  CalibDevice1 ;
  XSize1 ;
  YSize1 ;
  MaxLinesForSpectrum1 ;
  Data1 ;
  StopFlag1 ;
  StopFlag2 ;
  CalibUsageType1 ;
  Spectrum1 ;
  DataType1 ;
  SpectrumData1 ;
  DisplayHandle1 ;
  CalibData1 ;
  idx1 ;
  BasePath, Filename;
  Interval_mins, Duration_mins;
  StartTime, ElapsedTime ;
  SpectrumName; 
  i ; 
begin
  // ----------------------- USER CONFIG --------------------------

  // Configure data paths
  BasePath := 'Z:\Research Projects\UVDCS\Data\6-11-2025\mikey_uv_time_series\Spectrum_x.csv';

  // Configure run time
  Interval_mins := 1;
  Duration_mins := 120;

  // --------------- RECORD AND DISPLAY SPECTRUM LOOP ----------------

 
  
  StartTime := 0;
  ElapsedTime := 0;
  i := 0;
  while ElapsedTime < Duration_mins do 
    begin
      // ---------------------- CONFIGURING CAMERA ------------------------------
        // Setting Current Sequence ALSO Sets its Camera as Current Camera
      // Select Sequence 1 as Current Sequence (and thus Camera 1 as Current Camera)
      vsSelectDevice( dev_Sequence, 1 ) ;
      // Set Exposure (seconds)
      vsSetParam( dev_Sequence, 99, 0.01 );   // ParamID 99 = Exposure

      // Set Experiment Parameters
      vsSetParam( dev_Sequence, 155, 3 );   // ParamID 155 = Current Focus Mode
      vsSetParam( dev_Sequence, 154, 0 );   // ParamID 154 = Current Acquire Mode

      NumFrames1 := 1;         // Set Number of Frames To Collect
      vsSetupExperiment( NumFrames1, 2 );   // Frame Count = NumFrames1, Collection Mode 2 = Acquire
      vsInitialize( dev_Sequence );

      XSize1 := vsGetParam( dev_Sequence, 7519 );       // ParamID 7519 = X Dimension
      YSize1 := vsGetParam( dev_Sequence, 7520 );       // ParamID 7520 = Y Dimension (Number of Lines Per Frame)
      MaxLinesForSpectrum1 := 10;         // Set Maxiumum Lines (Strips) For Spectral Display
      DataType1 := vsGetParam( dev_Sequence, 7522 );       // ParamID 7522 = Data Type
      i := i+1;

      if YSize1 > MaxLinesForSpectrum1 then
        begin
            // Setup For Image
          DisplayHandle1 := CreateImage( DataType1, XSize1, YSize1, NumFrames1 );
          DisplayHandle1 := 0;          // Initialize the image
          Show( DisplayHandle1 );       // Display the image frame
          DisplayMode1 := 1;         // Set Display Mode to IMAGE
        end
      else
        begin
            // Setup For Spectrum Display
		      SpectrumName := ReplaceStr('Spectrumx', 'x', Str(i), rs_ReplaceAll);

          DisplayHandle1 := vsCreateSpectrum( SpectrumName );

          SpectrumData1 := CreateArray( DataType1, XSize1, YSize1, NumFrames1 );   // Create space for all spectra
          FillLinear( SpectrumData1 , 0, 0 );    // Initialize Array to 0

            // Get labels for current spectrometer calibration
          vsSetYLabel( DisplayHandle1, 'Intensity' );
          vsSetYLabelUnits( DisplayHandle1,'ADU' );
          vsSetTitle( DisplayHandle1,'Spectral Data' );

            // Get Current Calibration Usage:
            //    0 = None
            //    1 = Manual
            //    2 = Spectrometer
          CalibUsageType1 := vsGetParam( dev_Sequence, 7516 );   // ParamID 7516 = Calibration Usage
          if CalibUsageType1 = 1 then
            CalibDevice1 := dev_SpectraCal
          else if CalibUsageType1 = 2 then
            CalibDevice1 := dev_ManualCal
          else
            CalibDevice1 := 0;

          if CalibDevice1 <> 0 then     // Make sure a calibration exists
            begin
              CalibData1 := vsGetData( CalibDevice1 );   // Get Calibration Array for Display
              vsSetCalibration( DisplayHandle1, CalibData1 );
              TempStr1 := vsGetParamString( CalibDevice1, 21 )    // ParamID 21 = Calibration X Axis Display Label
            end
          else
            begin
              TempStr1 := 'Pixel';
            end;
          vsSetXLabel( DisplayHandle1, TempStr1 );

          DisplayMode1 := 2;         // Set Display Mode to SPECTRUM
        end;

      if DisplayMode1 = 1 then      // Check type of display
        begin
          SetDisplayMode( DisplayHandle1, dm_Histogram );   // Set Display Scaling Mode To Histogram
        end;

      vsStart( dev_Sequence );       // Start Data Collection 

      // Collect 1 Frames of Data, Then Stop
      idx1 := 1;
      StopFlag1 := 1;
      while (idx1 <= NumFrames1) and (StopFlag1 = 1) do
        begin

          vsCheckData( dev_Sequence, DataReady1 );

          if (vsError = True) and (vsLastErrorCode = 40273 ) then    // 40273 = Sequence Stopped
            StopFlag1 := 0;

          if DataReady1 = 1 then
            begin
              if DisplayMode1 = 1 then      // Check type of display
                begin
                    // Display Image Data
                  DisplayHandle1[..,..,idx1-1] := vsGetData( dev_Sequence );   // Data Transferred Direct To Image Display
                  SetActiveFrame( DisplayHandle1, idx1-1 );   // Set Current Frame As Active
                  SetDisplaySequence( DisplayHandle1, dm_Frame, idx1-1 );   // Scales On Active Frame
                end
              else
                begin
                    // Display Spectrum Data
                  SpectrumData1[..,..,idx1-1] := vsGetData( dev_Sequence );   // Data First Transferred To Local Array
                  vsSetSpectrumData( DisplayHandle1, SpectrumData1 );   // Then Transfer Data To Spectrum Display
                  vsSetFrame( DisplayHandle1, idx1-1 );        // Display the Current Frame
                end;
                idx1 := idx1 + 1;
            end;
        end;


      { Associate object with variable Spectrum1 }
      vsGetSpectrum( SpectrumName,Spectrum1 ) ;

      { Save variable to disk }
	    Filename := ReplaceStr(BasePath, 'x', Str(i), rs_ReplaceAll);
      Save( Spectrum1, Filename);
      { Wait }
	    ElapsedTime := ElapsedTime + Interval_mins;
      Delay(1000 * 60 * Interval_mins);
	  { Configure next run}
    end;
end
