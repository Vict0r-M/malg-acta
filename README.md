# Malg-ACTA (Automated Construction Testing and Analysis)

## Requirements

### General

- Use JSON files for persistent lists and maybe even non-persistent ones;
- Pluggable input and output methods (e.g., GUI, CLI, file, etc);
- Systematic file/folder and code naming and organization (e.g., Receipts PDF, Receipts Excel, Test Reports, Test Registry);
- Application exit functionality;
- Visual indicators showing progress through testing workflow steps and user warnings. These are strictly related to user actions. Examples:
    - If the user starts the app with the `scale` unplugged or unplugs after app starts, the workflow will wait for the issue to get fixed until proceeding with any `scale`-related steps (and implictly with any steps subsequent to `scale`-related steps), but will run the others. The "Atenție: Cântarul nu este conectat!" message will be displayed;
    - If the lifts the `specimen` too quickly from the `scale`, such that its reading has not been recorder, an appropriate message will be displayed and the user will be provided with another opportunity to place the `specimen` on the `scale`;
- Suitable for continuous use;
- Comprehensive error handling. Error mesasges should be directed towards developers displayed alongside the visual indicators, but in human readable format. They are strictly related to unexpected code behaviour. Examples:
    - "Eroare: Modulul *output* nu a primit datele in formatul așteptat!";
    - "Eroare: În cadrul funcției *read_press()*!";
- Compute `sample_age` in days as `testing_date` (current press or RPi date) - `sampling_date`. `sample_age` will appear in output;
- Support parallel operation of devices (thread safety for concurrent operations). *Example:* `cube_compression_testing` for 2 cubes should support:
    - placing both cubes first on the `scale`, then in the `press`;
    - placing first cube on the `scale`, then in the `press`, then repeating for the second cube;
- For GUI, all fields should become disabled after initiating test until completion;

### User Input

#### `protocol` - *"Protocol pentru"*:

- Radio button format;
- Validation: a choice must exist;
- Options:
    - `cube_compression_testing` - *Rezistență la Compresiune Cuburi*:
    - `cube_frost_testing` - *Gelivitate Cuburi*:
    - `beam_compression_testing` - *Rezistență la Prisme*:
    - `beam_flexural_testing` - *Rezistență la Încovoiere Prisme*:

#### `client` - *"Beneficiar"*:

- Dropdown format;
- Validation: a choice must exist (or typed);
- Case-insensitive filtering as user types;
- Dynamic addition of new clients to persistent list;
- Client deletion feature;
- Undo previous action feature;

#### `sampling_date` - *"Data Prelevării"*:

- Text input format;
- Validation: must respect `DD.MM.YYYY` format;

#### `concrete_class` - *"Clasa Betonului"*:

- Dropdown format;
- Validation: a choice must exist (or typed);
- Case-insensitive filtering as user types;
- Dynamic addition of new concrete classes to persistent list;
- Concrete class deletion feature;
- Undo previous action feature;

#### `set_id` - *"Indicativ"*:

- Text input format;
- Validation: a choice must be typed;

#### `set_size` - *"Număr Epruvete"*:

- Numerical input format;
- Refers to `specimens` per `set`;
- Validation: must be a greater than 0 integer;

#### `should_print` - *"Imprimare Bon"*:

- Radio button format;
- Controls whether a receipt is printed immediately after test completion;
- Validation: a choice must exist;
- Options:
    - Yes;
    - No;

#### `output_format` - *"Format Bon"*:

- Checkbox format;
- Validation: at least one choice must be selected;
- Options:
    - PDF;
    - Excel;
    - Word;

### Device Input

- Connect to and read data from `scale` (serial port);
- Connect to and read data from `press` (serial port);
- Connect to and print receipts with `printer`;
- Support plugging devices in and out without application restart;

### Protocols

- Architecture supporting easy addition of new testing protocols;
- Support protocol-specific calculations and formulas;

#### `cube_compression_testing` - *Rezistență la Compresiune Cuburi*:

- uses `scale` and `press`;
- requires one `scale` and one `press` measurement for each `specimen`;

#### `cube_frost_testing` - *Gelivitate Cuburi*:

- uses `scale` and `press`;
- requires one `scale` and one `press` measurement for each `specimen`;
- `specimens` must be provided in specific order (use visual indicators);

#### `beam_compression_testing` - *Rezistență la Prisme*:

- uses `press` only;
- requires two `press` measurements for each `specimen`;

#### `beam_flexural_testing` - *Rezistență la Încovoiere Prisme*:

- uses `press` only;
- requires one `press` measurements for each `specimen`;

### Output

- Partial results display (each receipt must contain 3 `specimens`, so if one is missing, its column will be empty);
- User-selectable output format options:
    - PDF output with standardized format;
    - Excel output with standardized format and embedded formulas for recalculation;
    - Word output with standardized format and with embedded formulas for recalculation;

## Control Flow Diagram

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#5a5ce6', 'primaryTextColor': '#fff', 'primaryBorderColor': '#5a5ce6', 'lineColor': '#a0a0a0', 'secondaryColor': '#62a8ea', 'tertiaryColor': '#393939'}}}%%
flowchart TD
    %% Main application flow
    Start[Start Malg-ACTA] --> LoadPersistentData[Load Persistent Lists]
    LoadPersistentData --> DisplaySingleScreen[Display Single Screen Interface]
    DisplaySingleScreen --> CheckDevices{Check Devices}
    CheckDevices -->|Devices OK| ShowStatus[Show Ready Status in Log]
    CheckDevices -->|Device Issues| DeviceWarning[Show Device Warning in Log]
    DeviceWarning --> ShowStatus
    ShowStatus --> UserInteraction[User Interaction with Single Screen]
    
    %% List Management
    UserInteraction --> ManageLists{Manage Lists?}
    ManageLists -->|Yes| ListSelection{List Selection}
    ListSelection -->|Clients| EditClients[Edit Clients List]
    ListSelection -->|Concrete Classes| EditConcreteClasses[Edit Concrete Classes List]
    EditClients --> SaveListChanges[Save Changes to JSON]
    EditConcreteClasses --> SaveListChanges
    SaveListChanges --> UserInteraction
    
    %% Testing Workflow
    ManageLists -->|No| TestingWorkflow{Start Testing?}
    TestingWorkflow -->|No| UserInteraction
    TestingWorkflow -->|Yes| InputParameters[Input Testing Parameters]
    InputParameters --> ValidateInput{Validate Input}
    ValidateInput -->|Invalid| ShowInputError[Show Input Error in Log]
    ShowInputError --> InputParameters
    ValidateInput -->|Valid| SaveInputTemp[Save Inputs to Temporary Storage]
    SaveInputTemp --> LockInterface[Lock UI Fields]
    LockInterface --> ProtocolSelect{Protocol Selection}
    
    %% Cube Testing (Compression/Frost) 
    ProtocolSelect -->|Cube Testing| CubeTestingFlow
    
    subgraph CubeTestingFlow[Cube Compression/Frost Testing]
        CubeInit[Initialize Testing] --> InitializeOrderTracking[Initialize Specimen Order Tracking]
        InitializeOrderTracking --> ShowMeasurementOptions[Display Scale & Press Options]
        ShowMeasurementOptions --> MeasurementChoice{User Selects Measurement}
        
        %% Scale Measurement Path
        MeasurementChoice -->|Scale Selected| SelectSpecimenScale[Select Untested Specimen for Scale]
        SelectSpecimenScale --> ScaleConnected{Scale Connected?}
        ScaleConnected -->|No| ScaleWarning[Show Scale Warning in Log]
        ScaleWarning --> ShowMeasurementOptions
        ScaleConnected -->|Yes| PlaceOnScale[Prompt: Place Selected Specimen on Scale]
        PlaceOnScale --> WeightStable{Stable Reading?}
        WeightStable -->|No| ScaleStabilityWarning[Show Weight Stability Warning in Log]
        ScaleStabilityWarning --> PlaceOnScale
        WeightStable -->|Yes| RecordWeight[Store Weight in Order-Tracked Data]
        RecordWeight --> UpdateScaleProgress[Update Scale Testing Progress]
        UpdateScaleProgress --> CheckTestingComplete
        
        %% Press Measurement Path
        MeasurementChoice -->|Press Selected| SelectSpecimenPress[Select Scale-Tested Specimen for Press]
        SelectSpecimenPress --> PressConnected{Press Connected?}
        PressConnected -->|No| PressWarning[Show Press Warning in Log]
        PressWarning --> ShowMeasurementOptions
        PressConnected -->|Yes| PlaceInPress[Prompt: Place Selected Specimen in Press]
        PlaceInPress --> TestStable{Test Complete?}
        TestStable -->|No| PressStabilityWarning[Show Test Warning in Log]
        PressStabilityWarning --> PlaceInPress
        TestStable -->|Yes| RecordPressResult[Store Press Result in Order-Tracked Data]
        RecordPressResult --> UpdatePressProgress[Update Press Testing Progress]
        UpdatePressProgress --> CheckTestingComplete
        
        %% Check if all testing is complete
        CheckTestingComplete{All Testing Complete?}
        CheckTestingComplete -->|No| ShowMeasurementOptions
        CheckTestingComplete -->|Yes| CompleteTest[Complete Testing]
    end
    
    %% Beam Testing (Compression)
    ProtocolSelect -->|Beam Compression| BeamCompressionFlow
    
    subgraph BeamCompressionFlow[Beam Compression Testing]
        BC_Start[Initialize Testing] --> BC_Loop[Loop for each specimen in set]
        BC_Loop --> BC_Press1{Press Connected?}
        BC_Press1 -->|No| BC_PressWarning1[Show Press Warning in Log]
        BC_PressWarning1 --> BC_Press1
        BC_Press1 -->|Yes| BC_PressPrompt1[Prompt: Place specimen in press for first measurement]
        BC_PressPrompt1 --> BC_PressCheck1{Test 1 Complete?}
        BC_PressCheck1 -->|No| BC_TestWarning1[Show Test Warning in Log]
        BC_TestWarning1 --> BC_PressPrompt1
        BC_PressCheck1 -->|Yes| BC_StoreResult1[Store result 1 in temp data]
        BC_StoreResult1 --> BC_Press2{Press Connected?}
        BC_Press2 -->|No| BC_PressWarning2[Show Press Warning in Log]
        BC_PressWarning2 --> BC_Press2
        BC_Press2 -->|Yes| BC_PressPrompt2[Prompt: Place specimen in press for second measurement]
        BC_PressPrompt2 --> BC_PressCheck2{Test 2 Complete?}
        BC_PressCheck2 -->|No| BC_TestWarning2[Show Test Warning in Log]
        BC_TestWarning2 --> BC_PressPrompt2
        BC_PressCheck2 -->|Yes| BC_StoreResult2[Store result 2 in temp data]
        BC_StoreResult2 --> BC_CheckMore{More specimens?}
        BC_CheckMore -->|Yes| BC_Loop
        BC_CheckMore -->|No| BC_Complete[Complete Testing]
    end
    
    %% Beam Testing (Flexural)
    ProtocolSelect -->|Beam Flexural| BeamFlexuralFlow
    
    subgraph BeamFlexuralFlow[Beam Flexural Testing]
        BF_Start[Initialize Testing] --> BF_Loop[Loop for each specimen in set]
        BF_Loop --> BF_Press{Press Connected?}
        BF_Press -->|No| BF_PressWarning[Show Press Warning in Log]
        BF_PressWarning --> BF_Press
        BF_Press -->|Yes| BF_PressPrompt[Prompt: Place specimen in press]
        BF_PressPrompt --> BF_PressCheck{Test Complete?}
        BF_PressCheck -->|No| BF_TestWarning[Show Test Warning in Log]
        BF_TestWarning --> BF_PressPrompt
        BF_PressCheck -->|Yes| BF_StoreResult[Store result in temp data]
        BF_StoreResult --> BF_CheckMore{More specimens?}
        BF_CheckMore -->|Yes| BF_Loop
        BF_CheckMore -->|No| BF_Complete[Complete Testing]
    end
    
    %% Output Generation
    CubeTestingFlow --> GenerateOutputs
    BeamCompressionFlow --> GenerateOutputs
    BeamFlexuralFlow --> GenerateOutputs
    
    subgraph GenerateOutputs[Generate Outputs]
        GO_Start[Process Test Results from Temp Data] --> GO_CalcAge[Calculate Sample Age]
        GO_CalcAge --> GO_UpdateRegistry[Update Test Registry JSON]
        GO_UpdateRegistry --> GO_FormatSelect{Check Selected Formats}
        GO_FormatSelect -->|PDF Selected| GO_PDF[Generate PDF]
        GO_FormatSelect -->|Excel Selected| GO_Excel[Generate Excel]
        GO_FormatSelect -->|Word Selected| GO_Word[Generate Word]
        GO_PDF --> GO_Print{Should Print?}
        GO_Excel --> GO_Print
        GO_Word --> GO_Print
        GO_Print -->|Yes| GO_SendPrint[Send to Printer]
        GO_Print -->|No| GO_Complete[Complete Output Generation]
        GO_SendPrint --> GO_Complete
    end
    
    GenerateOutputs --> UnlockInterface[Unlock UI Fields]
    UnlockInterface --> UserInteraction
    
    %% Application Exit
    UserInteraction --> ExitApp{Exit App?}
    ExitApp -->|Yes| Exit[Exit Application]
    ExitApp -->|No| UserInteraction
    
    %% Style definitions
    classDef default fill:#2d2d2d,stroke:#a0a0a0,stroke-width:2px,color:#fff
    classDef decision fill:#193c56,stroke:#4da6ff,stroke-width:2px,color:#fff
    classDef process fill:#1a3b1d,stroke:#5abb63,stroke-width:2px,color:#fff
    classDef error fill:#3b1a1a,stroke:#ff5c5c,stroke-width:2px,color:#fff
    classDef io fill:#2a1a38,stroke:#b366d9,stroke-width:2px,color:#fff
    classDef storage fill:#403619,stroke:#e0a458,stroke-width:2px,color:#fff
    
    %% Apply styles
    class CheckDevices,ValidateInput,ManageLists,TestingWorkflow,ListSelection,ProtocolSelect,MeasurementChoice,ScaleConnected,WeightStable,PressConnected,TestStable,CheckTestingComplete,BC_Press1,BC_PressCheck1,BC_Press2,BC_PressCheck2,BC_CheckMore,BF_Press,BF_PressCheck,BF_CheckMore,GO_FormatSelect,GO_Print,ExitApp decision
    class DisplaySingleScreen,ShowStatus,UserInteraction,InputParameters,LockInterface,CubeInit,InitializeOrderTracking,ShowMeasurementOptions,SelectSpecimenScale,PlaceOnScale,SelectSpecimenPress,PlaceInPress,UpdateScaleProgress,UpdatePressProgress,CompleteTest,BC_Start,BC_Loop,BC_PressPrompt1,BC_PressPrompt2,BC_Complete,BF_Start,BF_Loop,BF_PressPrompt,BF_Complete,GO_Start,GO_CalcAge,GO_PDF,GO_Excel,GO_Word,GO_SendPrint,GO_Complete,UnlockInterface process
    class DeviceWarning,ShowInputError,ScaleWarning,ScaleStabilityWarning,PressWarning,PressStabilityWarning,BC_PressWarning1,BC_TestWarning1,BC_PressWarning2,BC_TestWarning2,BF_PressWarning,BF_TestWarning error
    class Start,EditClients,EditConcreteClasses,Exit io
    class LoadPersistentData,SaveListChanges,SaveInputTemp,RecordWeight,RecordPressResult,BC_StoreResult1,BC_StoreResult2,BF_StoreResult,GO_UpdateRegistry storage
```