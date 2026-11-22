#ifndef AppVersion
#define AppVersion "1.2.0"
#endif
[Setup]
AppId={{D7E536F1-147B-45E9-A7E6-B7E9A784CF99}
AppName=Lumen
AppVersion={#AppVersion}
AppPublisher=Lumen contributors
AppPublisherURL=https://github.com/sacuar/Lumen
AppUpdatesURL=https://github.com/sacuar/Lumen/releases
DefaultDirName={localappdata}\Programs\Lumen
DefaultGroupName=Lumen
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\..\installer
OutputBaseFilename=Lumen-{#AppVersion}-Setup-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
SetupIconFile=..\..\assets\lumen.ico
WizardImageFile=..\..\assets\wizard.bmp
WizardSmallImageFile=..\..\assets\wizard-small.bmp
UninstallDisplayIcon={app}\Lumen.exe
ChangesAssociations=yes
CloseApplications=yes
RestartApplications=no
[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; Flags: unchecked
Name: "fileassoc"; Description: "Register Lumen in Open with and Default Apps"
Name: "contextmenu"; Description: "Add Open with Lumen and Open folder in Lumen to Explorer"
Name: "defaultapps"; Description: "Open Windows Default Apps after installation"; Flags: unchecked
[Files]
Source: "..\..\dist\Lumen\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{autoprograms}\Lumen"; Filename: "{app}\Lumen.exe"; IconFilename: "{app}\Lumen.exe"
Name: "{autodesktop}\Lumen"; Filename: "{app}\Lumen.exe"; Tasks: desktopicon
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\Lumen.exe"; ValueType: string; ValueData: "{app}\Lumen.exe"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Lumen.Editor"; ValueType: string; ValueData: "Lumen text document"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\Lumen.Editor\DefaultIcon"; ValueType: string; ValueData: "{app}\Lumen.exe,0"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\Lumen.Editor\shell\open\command"; ValueType: string; ValueData: """{app}\Lumen.exe"" ""%1"""; Tasks: fileassoc
Root: HKCU; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "Lumen"; ValueData: "Software\Lumen\Capabilities"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "Lumen"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Lumen text and code editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".txt"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.txt\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".py"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.py\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".pyw"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.pyw\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".md"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.md\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".json"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.json\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".js"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.js\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ts"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.ts\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".html"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.html\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".css"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.css\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".xml"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.xml\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".yaml"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.yaml\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".yml"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.yml\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".log"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.log\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ini"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.ini\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".php"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.php\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Lumen\Capabilities\FileAssociations"; ValueType: string; ValueName: ".csv"; ValueData: "Lumen.Editor"; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.csv\OpenWithProgids"; ValueType: none; ValueName: "Lumen.Editor"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\*\shell\LumenEdit"; ValueType: string; ValueData: "Open with Lumen"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\LumenEdit"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\Lumen.exe,0"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\LumenEdit\command"; ValueType: string; ValueData: """{app}\Lumen.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\Directory\shell\LumenEdit"; ValueType: string; ValueData: "Open folder in Lumen"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\Directory\shell\LumenEdit"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\Lumen.exe,0"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\Directory\shell\LumenEdit\command"; ValueType: string; ValueData: """{app}\Lumen.exe"" ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\LumenEdit"; ValueType: string; ValueData: "Open folder in Lumen"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\LumenEdit\command"; ValueType: string; ValueData: """{app}\Lumen.exe"" ""%V"""; Tasks: contextmenu
[Run]
Filename: "ms-settings:defaultapps"; Description: "Choose Lumen in Windows Default Apps"; Flags: shellexec postinstall skipifsilent unchecked; Tasks: defaultapps
Filename: "{app}\Lumen.exe"; Description: "Launch Lumen"; Flags: nowait postinstall skipifsilent
