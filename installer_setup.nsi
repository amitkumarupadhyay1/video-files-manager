; Video Manager Professional Installer
; NSIS Modern User Interface

;--------------------------------
; Includes

!include "MUI2.nsh"
!include "FileFunc.nsh"

;--------------------------------
; General

; Name and file
Name "Video Manager"
OutFile "VideoManager_Setup.exe"
Unicode True

; Default installation folder
InstallDir "$PROGRAMFILES64\VideoManager"

; Get installation folder from registry if available
InstallDirRegKey HKLM "Software\VideoManager" "InstallPath"

; Request application privileges
RequestExecutionLevel admin

; Compression
SetCompressor /SOLID lzma

;--------------------------------
; Variables

Var StartMenuFolder

;--------------------------------
; Interface Settings

!define MUI_ABORTWARNING
!define MUI_ICON "assets\app_icon.ico"
!define MUI_UNICON "assets\app_icon.ico"
!define MUI_HEADERIMAGE
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\installer_banner.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "assets\installer_banner.bmp"

;--------------------------------
; Pages

; Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY

; Start Menu Folder Page Configuration
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM" 
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\VideoManager" 
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

!insertmacro MUI_PAGE_INSTFILES

; Finish page with option to launch
!define MUI_FINISHPAGE_RUN "$INSTDIR\VideoManager.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Video Manager"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Video Manager"
VIAddVersionKey "CompanyName" "Jingle Bell Nursery School Society"
VIAddVersionKey "LegalCopyright" "© 2025 All Rights Reserved"
VIAddVersionKey "FileDescription" "Video Management System Installer"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"

;--------------------------------
; Installer Sections

Section "Video Manager" SecMain

  SetOutPath "$INSTDIR"
  
  ; Copy all files from dist\VideoManager
  File /r "dist\VideoManager\*.*"
  
  ; Create storage directories (will be created by app if not exist)
  CreateDirectory "$INSTDIR\storage"
  CreateDirectory "$INSTDIR\storage\videos"
  CreateDirectory "$INSTDIR\storage\thumbnails"
  CreateDirectory "$INSTDIR\storage\documents"
  
  ; Store installation folder
  WriteRegStr HKLM "Software\VideoManager" "InstallPath" $INSTDIR
  WriteRegStr HKLM "Software\VideoManager" "Version" "1.0.0"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                   "DisplayName" "Video Manager"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                   "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                   "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                   "DisplayIcon" "$\"$INSTDIR\VideoManager.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                   "Publisher" "Jingle Bell Nursery School Society"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                   "DisplayVersion" "1.0.0"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                     "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                     "NoRepair" 1
  
  ; Calculate and store installed size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager" \
                     "EstimatedSize" "$0"
  
  ; Create Start Menu shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Video Manager.lnk" \
                   "$INSTDIR\VideoManager.exe" "" "$INSTDIR\VideoManager.exe" 0
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" \
                   "$INSTDIR\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
  
  ; Create Desktop shortcut
  CreateShortcut "$DESKTOP\Video Manager.lnk" "$INSTDIR\VideoManager.exe" \
                 "" "$INSTDIR\VideoManager.exe" 0

SectionEnd

;--------------------------------
; Descriptions

; Language strings
LangString DESC_SecMain ${LANG_ENGLISH} "Video Manager application files"

; Assign language strings to sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller Section

Section "Uninstall"

  ; Confirm before deleting user data
  MessageBox MB_YESNO|MB_ICONQUESTION \
    "Do you want to delete all video data and database?$\n$\nClick 'No' to keep your data for future use." \
    IDYES DeleteData IDNO KeepData
  
  DeleteData:
    RMDir /r "$INSTDIR\storage"
    Goto Continue
  
  KeepData:
    ; Keep storage folder
    Goto Continue
  
  Continue:
  
  ; Remove application files
  Delete "$INSTDIR\VideoManager.exe"
  Delete "$INSTDIR\*.dll"
  Delete "$INSTDIR\*.pyd"
  Delete "$INSTDIR\*.manifest"
  Delete "$INSTDIR\Uninstall.exe"
  
  ; Remove directories
  RMDir /r "$INSTDIR\assets"
  RMDir /r "$INSTDIR\_internal"
  RMDir /r "$INSTDIR\PyQt6"
  
  ; Try to remove install directory (will fail if storage exists and user chose to keep it)
  RMDir "$INSTDIR"
  
  ; Remove Start Menu shortcuts
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  Delete "$SMPROGRAMS\$StartMenuFolder\Video Manager.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"
  
  ; Remove Desktop shortcut
  Delete "$DESKTOP\Video Manager.lnk"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\VideoManager"
  DeleteRegKey HKLM "Software\VideoManager"

SectionEnd
