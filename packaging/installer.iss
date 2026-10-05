; Inno Setup script for ClipShow Windows installer
#ifndef AppVer
  #define AppVer "0.0.0"
#endif

[Setup]
AppName=ClipShow 中文版
AppVersion={#AppVer}
AppPublisher=ClipShow 中文版
DefaultDirName={autopf}\ClipShow
DefaultGroupName=ClipShow 中文版
OutputBaseFilename=ClipShow-{#AppVer}-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
UninstallDisplayName=ClipShow 中文版
LicenseFile=..\LICENSE

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式"

[Files]
Source: "..\dist\ClipShow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\ClipShow 中文版"; Filename: "{app}\ClipShow.exe"
Name: "{group}\{cm:UninstallProgram,ClipShow}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ClipShow 中文版"; Filename: "{app}\ClipShow.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ClipShow.exe"; Description: "启动 ClipShow 中文版"; Flags: nowait postinstall skipifsilent
