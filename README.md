# Malg-ACTA (Automated Construction Testing and Analysis)

## Requirements

### General

- Use JSON files for persistent lists and maybe even non-persistent ones;
- Pluggable input and output methods (e.g., GUI, CLI, file, etc);
- Systematic file/folder and code naming and organization (e.g., Receipts PDF, Receipts Excel, Test Reports, Registry);
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
    - `beam_compression_testing` - *Rezistență la Compreiune Prisme*:
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

#### `beam_compression_testing` - *Rezistență la Compresiune Prisme*:

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
- Model available at `examples/output`.

## Control Flow Diagram

Decision tree available both [here](https://mermaid.live/view?fbclid=IwZXh0bgNhZW0CMTEAAR7mEuMYccp8hioQikzrIGXwfMDqczq9udkhe57xQd0POunKrUT0guI9zIzbyw_aem_RvWth-26Zj6dSdO5l3HD4Q#pako:eNqdWo1P47gS_1esnHi8k8weTT8ole5WLGz3Ie0eaMvu6r2AViZx24g06SXpLlzhf39jj53YTlLgQGrj8W9m7PmyY3frhVnEvYm3t7eN07ickO1-ueQrvj8h-xHL7_YpQcJXlsfsNuEF9GzJ_jqPVyx_OM2SLBfYX4ZsGPKRgKuuK35f1t3z-dzoe5flEc_bmJM45TWdHYp_QS94mKWRpXHkszFncoA8L2Orr38s_vefnp729q7TeZL9DJcsL8nV2XVK4G9vj3xicUrYep3EISvjLCUCRX7G5ZLkPNqEPCI_hNyQJaRYszBOF8g7K0FSID9BSLI4ODm9Orkhv__-B_mYseiS50VclDwtz1jJAkEiNY18hO_iBiU14VLKWVysE_bw4ct5oB4JPCueupMcHPxBvhQ8P0_BACwUkwhEmxgExVXNWqiHUadsAT5NS6Q7QqRgxMjRbvEZh_72CXmMfoF__C8vHiVixhMuxWylrqqp-CyI5DxNYhgJcH9ZR6zkqilwAVKIIknem04xWRrmXKJZUfBanqIrsiXXYTEVNAbTZm4L2tTTzVL544oXJUQW-ZbldyIA2437Z_aokRq4xQBUVO0VB1Qxtw6iDSzdeJ6uN-Uly9kK5pMXgWxXQ607lKkcuJz1V5bEwiqyb6tbCFVjtSBS-Xn6Q9AeyWyZ_ZTk93me5YFoIiuRBKXXRkm1zlC6FH1FNR-z8E5aZc5CHogWgbSaxjyJ6hQ1IFLFZZ6VWZglGH1b3WwEeuXiM_4jBt7TJQf5t6yAwgIhq_kQZguVepBNcm2R9zP_axNDbVJdhVJkAOXkVC_5MyuBhUUPjwryjeUpOBDNqUalaDemKEXrjt4ujUqbnsy7nKXhsrbQ1cOau8Y53dzyKrL-fZqt1jkvCtD02zTPivJXYtsHRWK-C84Gw6OUqAROq4TCz2Jzu8jZeulignZZelzKOOJPAM9hnQzERwxR9Hc1-hsVgJp-IZa4K7DbnbC5gZcdRPcYwjt40Q-yxoAZFmKIuoD9Sy8HZAbLlGhfim6icYZwWwCWeM6KTS7XgdNlBh7cytUDY7Awu59qOfUTeA-1GkAoDuWyhjQ0SM8hF6rhIttFG8pnKttb7K7abw3lNrKqbpJsRTfKsIO7EmDFt2WWnZpkabxMoA5cpLI7ALbVGvZMkkhmax7GMFWR3bLf0GuySb3feLxYllDDYUu1xS-ZPkYtF38mzJ6uoMVJXD5Y80Y8qTq7TOByY2UzBrljCNIOn2E_lkfYF2BDK5dbqM4gNxmlVllGVA6JFEygcneEGwb3a8MNuepwk-063LC7NdxsZGV_SbbMjjKatjaRO8OtRVMdbuep7O4KtzhFdjfcFJvUK-yrgk08Em1oc7Y1xp5pe6RJMR0z7o4uNaZOpUZsSeBnXmySKsBwPkh7UZgZMl4ba7i6xXPCkoSUaoGKCxI22NqEbk-ASy9rbcZuY6p3ax1R0skkzaYpAhBU3fYaxtPIWYDfcbZqXYB_7Vx5JYuBfJRCDELnutuCC1xpLavuu9Pv-NLVteoC4GOWrQPxQeawF-QMxloYGVLw0hYooYpXhklvVyWoQJWPNEWFeG93IXDRtuYuPdKtmoTZ33OqQDVHMet5nENSruoq2DICJcYagIyrHlaGXmu42kjTCILJtkFHZXCw1gDUoHbq08aYlVnOMad7ujBM5cSR6MZNjbZU-i9xt9_lbv9V7vZtzV16Wtzt73I3nom8yN9-098--tt_3t9-h7_9V_jbb_G3v1Nfi7997e8ZzvwZh1c6pdRPQN-Kj8qIhTPjCmbpF4ViB0yZRRvxnxbeacLvNzlLnqm6GoYlV7d21lsTFFhC2irt9LlKO31lpZ0alXaKTt6ZeQpT23b6_eX7LQdsae3QgW6emnHZlXMwubWz0bIZLX345t6527Jg5myNpNmdXxbUUo2j2aVLz9rIFp1bzaSyYFrRi3Jq2ppTUzenpm05Nf0HOfUp-8HJB57yXLwdX2zK9QZeZMMkE--1ZUaycgkPt0kW3ql4cE4C5Oy0AMWPwJaty26wmXfdSCdhHUzgzsVwy4cLlarg7VBEs4wTdFKByQqQU5aEJwswIXxvEiFpxoQxCRBtYQqpGXEP-pkv4qLMH_SBg9KBRJvfZtBiplm-YuqkVh1j6Tcxgn3FkyXGZMDXt7Op8fIGCCDUdoHGzW7-9_chT2wJklTLkM1npHzDZccQIii1DNGyRYhxKyNc5nFabiGZN4l4iYHGW3vSOEYTbXVL5Z29klKnl4gLyAxJDcSTCHzZ4vlNB6NIOBECjYTDsNNhWd8n6ADUiqpws96OnAR1ghtfiNPEOoTFduMY1oG94GD9xLjZeX8f77jpEL2A3opvwaZ9o-i1ZQUhkKj62qcJ7Txur4Y2Kx8gASM-Fzdu0K1KQSguDs74XPQwUWnncZJMfvEj8U8hqbI7PlFXYqp58DOOyuXEX9_TUNx9TcQ9W0NaGMv3KhTXO-6Hw1ElbhCx0Xz-CnFrVW2UNNa_7dWDG7Lb21H_FdK4PLlHWSCJ9Vglaz4fhsPwFbLiTFsMxPTHlaDb_mgUHb9CUAGrnbjvQmmDw_6od1xJ44dsMBw_L80KxAeQCT43HW3e8VDnJoZat1vUur-gxuE7ta8NqL1rpI3jMGqfalLzaI_aR1C0PpihbccOtHpTpfa7WtX07Q7ZrJZ5qrck1NqbUHMrQJ06THXJojrddGibZnVSjzo3QtS60KH6PJ92nL1T81CF6nMIql4LqPOC6bRxypXBppp5qpitfRU1NjxUr-20XpcpLilUrxZUrQvULMPUKMHUqZnSajp9TYtZlz7UvlSj5oE5bT06puaOm7ae_1H3-IM6hwEuwHcAPnV29tTZ_co6Yk4KzVdfllPzcJuaZ5HUPm2jzpmE065Horb8cWaqbd7o08ZFMu28L6bm4ThtHGHS5i5LlSr3kp8vqqW32lqaRHmz-f1MpU-gH24mk4mdUwhUO0y90xQwK44QhXe1yiO_4UUtIA3XIO78wviVglzN3yd4egFobU6EznB6gfH7CWFTAbRm3ji9hboBcqEUblYpgQjINmXbzGHBPqjn1zJlBXjvzkHfOB_I-dizU-TZzgH-J47E-GS1BUniZy-Gfmje4S5hPCJq5UmzlLcijp5FjJ9FHDcRECwe9RZ5HHmTMt9w6q04FGPR9LYCcu3JHwZdexN4FL8Vuvau0yfgWbP0f1m20mx5tlksvcmcJQW0NjKAz2IGUVlDQJn4PdAmLb0JLN1ChDfZevfexD_uvxn0B8eD_uFh72jsD6j34E0OBuPRm8PhUe9w1Ov3_KPj4RP1_pZKe2_G42FvMO4PjwYDfzgaHFGPRzFY-RP-1En-4unp_1gEbLk) and below:

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#5a5ce6', 'primaryTextColor': '#fff', 'primaryBorderColor': '#5a5ce6', 'lineColor': '#a0a0a0', 'secondaryColor': '#62a8ea', 'tertiaryColor': '#393939'}}}%%
flowchart TD
    %% Main application flow with reduced vertical spacing
    Start[Start Malg-ACTA] ==> LoadPersistentData[Load Persistent Lists]
    LoadPersistentData ==> DisplayGUI[Display GUI]
    DisplayGUI --> UserInteraction[User Interaction]
    
    %% List Management
    UserInteraction --> ManageLists{Manage Lists?}
    ManageLists -->|Yes| ListSelection{List Selection}
    ListSelection -->|Clients| UpdateClientsList[Update Clients List]
    ListSelection -->|Concrete Classes| UpdateConcreteClassesList[Update Concrete Classes List]
    UpdateClientsList --> UserInteraction
    UpdateConcreteClassesList --> UserInteraction
    
    %% Testing Workflow
    ManageLists -->|No| TestingWorkflow{Start Testing?}
    TestingWorkflow -->|No| UserInteraction
    TestingWorkflow -->|Yes| InputParameters[Input Testing Parameters]
    InputParameters --> ValidateInput{Validate Input}
    ValidateInput -->|Invalid| ShowInputError[Show Input Error]
    ShowInputError --> InputParameters
    ValidateInput -->|Valid| LockInterface[Lock UI Fields]
    LockInterface --> ProtocolSelect{Protocol Selection}
    
    %% Device Check based on Protocol
    ProtocolSelect --> DeviceCheck{Check Required Devices}
    DeviceCheck -->|Devices Not Ready| DeviceWarning[Show Device Warning]
    DeviceWarning --> UserInteraction
    DeviceCheck -->|Devices Ready| ProtocolBranch{Protocol Type}
    
    %% Cube Testing (Compression/Frost) 
    ProtocolBranch -->|Cube Compression/Frost| CubeTestingFlow
    
    subgraph CubeTestingFlow[Cube Compression/Frost Testing]
        CubeInit[Initialize Testing] --> InitializeOrderTracking[Initialize Order Tracking]
        InitializeOrderTracking --> UpdateProgress[Update & Display Scale & Press Progress]
        UpdateProgress --> MeasurementChoice{User Selects Measurement}
        
        %% Scale Measurement Path
        MeasurementChoice -->|Scale Selected| ScaleConnected{Scale Connected?}
        ScaleConnected -->|No| ScaleWarning[Show Scale Warning]
        ScaleWarning --> UpdateProgress
        ScaleConnected -->|Yes| PlaceOnScale[Prompt: Place Specimen on Scale]
        PlaceOnScale --> WeightStable{Stable Reading?}
        WeightStable -->|No| ScaleStabilityWarning[Show Weight Stability Warning]
        ScaleStabilityWarning --> PlaceOnScale
        WeightStable -->|Yes| RecordWeight[Record Weight with Order Tracking]
        RecordWeight --> CheckTestingComplete
        
        %% Press Measurement Path
        MeasurementChoice -->|Press Selected| PressConnected{Press Connected?}
        PressConnected -->|No| PressWarning[Show Press Warning]
        PressWarning --> UpdateProgress
        PressConnected -->|Yes| PlaceInPress[Prompt: Place Specimen in Press]
        PlaceInPress --> TestStable{Test Complete?}
        TestStable -->|No| PressStabilityWarning[Show Test Warning]
        PressStabilityWarning --> PlaceInPress
        TestStable -->|Yes| RecordPressResult[Record Press Result with Order Tracking]
        RecordPressResult --> CheckTestingComplete
        
        %% Check if all testing is complete
        CheckTestingComplete{All Testing Complete?}
        CheckTestingComplete -->|No| UpdateProgress
        CheckTestingComplete -->|Yes| CompleteTest[Complete Testing]
    end
    
    %% Beam Testing (Compression)
    ProtocolBranch -->|Beam Compression| BeamCompressionFlow
    
    subgraph BeamCompressionFlow[Beam Compression Testing]
        BC_Start[Initialize Testing] --> BC_Loop[Loop for each specimen in set]
        BC_Loop --> BC_Press1{Press Connected?}
        BC_Press1 -->|No| BC_PressWarning1[Show Press Warning]
        BC_PressWarning1 --> BC_Press1
        BC_Press1 -->|Yes| BC_PressPrompt1[Prompt: Place specimen for first measurement]
        BC_PressPrompt1 --> BC_PressCheck1{Test 1 Complete?}
        BC_PressCheck1 -->|No| BC_TestWarning1[Show Test Warning]
        BC_TestWarning1 --> BC_PressPrompt1
        BC_PressCheck1 -->|Yes| BC_StoreResult1[Record First Result]
        BC_StoreResult1 --> BC_Press2{Press Connected?}
        BC_Press2 -->|No| BC_PressWarning2[Show Press Warning]
        BC_PressWarning2 --> BC_Press2
        BC_Press2 -->|Yes| BC_PressPrompt2[Prompt: Place specimen for second measurement]
        BC_PressPrompt2 --> BC_PressCheck2{Test 2 Complete?}
        BC_PressCheck2 -->|No| BC_TestWarning2[Show Test Warning]
        BC_TestWarning2 --> BC_PressPrompt2
        BC_PressCheck2 -->|Yes| BC_StoreResult2[Record Second Result]
        BC_StoreResult2 --> BC_CheckMore{More specimens?}
        BC_CheckMore -->|Yes| BC_Loop
        BC_CheckMore -->|No| BC_Complete[Complete Testing]
    end
    
    %% Beam Testing (Flexural)
    ProtocolBranch -->|Beam Flexural| BeamFlexuralFlow
    
    subgraph BeamFlexuralFlow[Beam Flexural Testing]
        BF_Start[Initialize Testing] --> BF_Loop[Loop for each specimen in set]
        BF_Loop --> BF_Press{Press Connected?}
        BF_Press -->|No| BF_PressWarning[Show Press Warning]
        BF_PressWarning --> BF_Press
        BF_Press -->|Yes| BF_PressPrompt[Prompt: Place specimen in press]
        BF_PressPrompt --> BF_PressCheck{Test Complete?}
        BF_PressCheck -->|No| BF_TestWarning[Show Test Warning]
        BF_TestWarning --> BF_PressPrompt
        BF_PressCheck -->|Yes| BF_StoreResult[Record Result]
        BF_StoreResult --> BF_CheckMore{More specimens?}
        BF_CheckMore -->|Yes| BF_Loop
        BF_CheckMore -->|No| BF_Complete[Complete Testing]
    end
    
    %% Move Generate Outputs closer to other blocks
    CubeTestingFlow --> GenerateOutputs
    BeamCompressionFlow --> GenerateOutputs
    BeamFlexuralFlow --> GenerateOutputs
    
    subgraph GenerateOutputs[Generate Outputs]
        GO_Start[Process Test Results] --> GO_UpdateRegistry[Update Registry]
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
    ExitApp -->|Yes| Exit[Exit Malg-ACTA]
    ExitApp -->|No| UserInteraction
    
    %% Style definitions
    classDef default fill:#2d2d2d,stroke:#a0a0a0,stroke-width:2px,color:#fff
    classDef decision fill:#193c56,stroke:#4da6ff,stroke-width:2px,color:#fff
    classDef process fill:#1a3b1d,stroke:#5abb63,stroke-width:2px,color:#fff
    classDef error fill:#3b1a1a,stroke:#ff5c5c,stroke-width:2px,color:#fff
    classDef io fill:#2a1a38,stroke:#b366d9,stroke-width:2px,color:#fff
    classDef storage fill:#403619,stroke:#e0a458,stroke-width:2px,color:#fff
    
    %% Apply styles
    class ManageLists,TestingWorkflow,ListSelection,ValidateInput,DeviceCheck,ProtocolSelect,ProtocolBranch,MeasurementChoice,ScaleConnected,WeightStable,PressConnected,TestStable,CheckTestingComplete,BC_Press1,BC_PressCheck1,BC_Press2,BC_PressCheck2,BC_CheckMore,BF_Press,BF_PressCheck,BF_CheckMore,GO_FormatSelect,GO_Print,ExitApp decision
    class UserInteraction,InputParameters,LockInterface,CubeInit,InitializeOrderTracking,CompleteTest,BC_Start,BC_Loop,BC_StoreResult1,BC_StoreResult2,BC_Complete,BF_Start,BF_Loop,BF_StoreResult,BF_Complete,GO_Start,GO_CalcAge,GO_PDF,GO_Excel,GO_Word,GO_SendPrint,GO_Complete,UnlockInterface,Exit process
    class DeviceWarning,ShowInputError,ScaleWarning,ScaleStabilityWarning,PressWarning,PressStabilityWarning,BC_PressWarning1,BC_TestWarning1,BC_PressWarning2,BC_TestWarning2,BF_PressWarning,BF_TestWarning error
    class Start,DisplayGUI,PlaceOnScale,PlaceInPress,UpdateProgress,BC_PressPrompt1,BC_PressPrompt2,BF_PressPrompt io
    class LoadPersistentData,UpdateClientsList,UpdateConcreteClassesList,RecordWeight,RecordPressResult,GO_UpdateRegistry storage
    
    %% Legend
    subgraph Legend
        L_Decision[Decision]:::decision
        L_Process[Process]:::process
        L_Error[Warning/Error]:::error
        L_IO[User Interface Element]:::io
        L_Storage[Persistent and Order Tracking Data]:::storage
        
        %% Force column layout
        L_Decision --- L_Process
        L_Process --- L_Error
        L_Error --- L_IO
        L_IO --- L_Storage
        
        %% Hide connector lines
        linkStyle 86 stroke:none
        linkStyle 87 stroke:none
        linkStyle 88 stroke:none
        linkStyle 89 stroke:none
    end
```

## Language Distribution

### Python Components:
- Core state machine;
- Plugin manager;
- Device plugins (including serial communication);
- High-level business logic;
- Data store and persistence.

### C++ Components:
- Performance-critical calculations (if needed);
- Data processing algorithms;
- Future improvement: Serial communication library.

### Java Components:
- UI implementation;
- Receipt generation.

## Project Structure Template

```
malg-acta/
├── main.py                         # Application entry point
├── app_modules/
│   ├── core/
│   │   ├── state_machine.py        # Application flow control point
│   │   ├── plugin_manager.py       # Manages loading and lifecycle of all plugins
│   │   ├── data_storage.py         # Central data storage and access point
│   │   ├── communication.py        # Inter-module communication bridge
│   │   └── config_loader.py        # Configuration loader and manager
│   ├── states/
│   │   ├── base_state.py           # Abstract base class for all states
│   │   ├── idle_state.py           # Idle (waiting) state implementation
│   │   ├── testing_state.py        # Base class for testing-related states
│   │   └── error_state.py          # Error and warning state implementation
│   ├── interfaces/
│   │   ├── ui_plugin.py            # Interface for UI
│   │   ├── device_plugin.py        # Interface for device connections
│   │   ├── protocol_plugin.py      # Interface for testing protocols
│   │   └── output_plugin.py        # Interface for receipt generators
│   ├── devices/
│   │   ├── scale_plugin.py         # Scale communication implementation
│   │   ├── press_plugin.py         # Press communication implementation
│   │   ├── printer_plugin.py       # Printer communication implementation
│   │   └── serial/                 # Serial communication utilities
│   │       ├── serial_manager.py   # Manages serial port connections
│   │       └── device_detector.py  # Detects connected devices
│   ├── protocols/
│   │   ├── base_protocol.py        # Abstract base class for all protocols
│   │   ├── cube_compression.py     # Cube compression testing implementation
│   │   ├── cube_frost.py           # Cube frost testing implementation
│   │   ├── beam_compression.py     # Beam compression testing implementation
│   │   └── beam_flexural.py        # Beam flexural testing implementation
│   ├── models/
│   │   ├── specimen.py             # Specimen data model
│   │   ├── set.py                  # Set data model
│   │   ├── batch.py                # Batch data model
│   │   └── test_data.py            # Test results data model
│   ├── data_persistence/
│   ├── utils/
│   │   ├── logging.py              # Logging setup and utilities
│   │   ├── typing.py               # Custom typing
│   │   ├── errors.py               # Custom error
│   │   └── validation.py           # Input validation
│   ├── calculations/               # Calculation-related functionality (C++)
│   ├── data_processing/            # Data processing functionality (C++)
│   ├── input/                      # Input methods (Java)
│   ├── output/                     # Output methods (Java)
│   └── bridges/
│       ├── cpp_bridge.py           # Bridge to C++ components
│       └── java_bridge.py          # Bridge to Java components
├── config/
│   ├── app_config.yaml             # Main application configuration
│   └── protocols.yaml              # Protocol configurations
├── data/
│   ├── clients.json                # Client list
│   ├── concrete_classes.json       # Concrete classes list (editable during runtime)
│   ├── registry.json               # Registry storage
│   └── temp/                       # Temporary data storage
├── examples/                       # Example implementations
├── .gitignore                      # Files and folders that shouldn't appear on GitHub
├── requirements.txt                # Environment requirements
├── LICENSE                         # Repository license
└── README.md                       # Project documentation
```