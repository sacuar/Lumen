param([ValidateSet('QuickPhotoViewer','Lumen','CaptureForge','All')][string]$App='All',[string]$ProtectPath='')
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName Microsoft.VisualBasic
$names=@{QuickPhotoViewer='quick[ _-]*photo[ _-]*viewer(?:[ _-]*pro)?';Lumen='lumen';CaptureForge='capture[ _-]*forge'}
$pattern=if($App -eq 'All'){($names.Values -join '|')}else{$names[$App]}
$regex='(?i)^(?:'+$pattern+')(?:[ _.-]*(?:v(?:ersion)?[ _.-]*)?\d[\w.-]*|[ _-]*(?:build|setup|installer|portable|working|source)[\w.-]*)*$'
$form=New-Object Windows.Forms.Form
$form.Text="$App - Installation maintenance";$form.Width=1100;$form.Height=650;$form.StartPosition='CenterScreen'
$form.Font=New-Object Drawing.Font('Segoe UI',10)
$top=New-Object Windows.Forms.FlowLayoutPanel;$top.Dock='Top';$top.Height=82;$top.WrapContents=$true
$label=New-Object Windows.Forms.Label;$label.AutoSize=$true;$label.Text='Review possible old builds and registrations. Nothing is removed automatically.'
[void]$top.Controls.Add($label)
$status=New-Object Windows.Forms.Label;$status.Dock='Bottom';$status.Height=30;$status.Text='Choose a scan. A matching name is not proof of ownership.'
$grid=New-Object Windows.Forms.DataGridView;$grid.Dock='Fill';$grid.ReadOnly=$true;$grid.AllowUserToAddRows=$false;$grid.AllowUserToDeleteRows=$false;$grid.MultiSelect=$false;$grid.SelectionMode='FullRowSelect';$grid.AutoSizeColumnsMode='Fill';$grid.RowHeadersVisible=$false
[void]$grid.Columns.Add('Type','Type');[void]$grid.Columns.Add('Name','Name / detail');[void]$grid.Columns.Add('Path','Path / registration')
$grid.Columns[0].FillWeight=20;$grid.Columns[1].FillWeight=25;$grid.Columns[2].FillWeight=55
$form.Controls.Add($grid);$form.Controls.Add($status);$form.Controls.Add($top)
function Row($kind,$name,$path){[void]$grid.Rows.Add([string]$kind,[string]$name,[string]$path)}
function Button($name,$action){$b=New-Object Windows.Forms.Button;$b.Text=$name;$b.AutoSize=$true;$b.Add_Click($action);$top.Controls.Add($b)}
$script:job=$null;$script:seen=@{}
function Inventory {
 foreach($r in @('HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*')){
  foreach($v in @(Get-ItemProperty $r -ErrorAction SilentlyContinue)){if($v.DisplayName -match $regex){Row 'Installed app' "$($v.DisplayName) $($v.DisplayVersion)" "$($v.InstallLocation)";Row 'Uninstall registry' $v.DisplayName $v.PSPath}}
 }
 foreach($h in @('HKCU','HKLM')){
  $run="$($h):\Software\Microsoft\Windows\CurrentVersion\Run";$key=Get-Item $run -ErrorAction SilentlyContinue
  if($key){foreach($n in $key.GetValueNames()){if($n -match $regex){Row 'Startup registry' "$n = $($key.GetValue($n))" "$run|$n"}}}
  foreach($a in @('QuickPhotoViewer','Lumen','CaptureForge')){
   if($a -notmatch $regex){continue}
   foreach($p in @("$($h):\Software\Microsoft\Windows\CurrentVersion\App Paths\$a.exe","$($h):\Software\Classes\Applications\$a.exe")){
    if(Test-Path -LiteralPath $p){Row 'App registry' $a $p}
   }
  }
 }
 foreach($p in Get-Process -ErrorAction SilentlyContinue){if($p.ProcessName -match $regex){try{Row 'Running copy' "$($p.ProcessName) (PID $($p.Id))" $p.Path}catch{}}}
}
$worker={
 param([string]$rootsJson,[string]$regex)
 $stack=New-Object 'System.Collections.Generic.Stack[string]'
 foreach($root in @(ConvertFrom-Json $rootsJson)){if($root -and [IO.Directory]::Exists($root)){$stack.Push($root)}}
 $seen=New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
 $deadline=[datetime]::UtcNow.AddMinutes(4);$visited=0
 while($stack.Count -gt 0 -and $visited -lt 500000 -and [datetime]::UtcNow -lt $deadline){
  $dir=$stack.Pop();if(!$seen.Add($dir)){continue};$visited++
  try{
   foreach($f in [IO.Directory]::EnumerateFiles($dir)){
    if([IO.Path]::GetExtension($f) -notin @('.exe','.zip','.msi','.lnk')){continue}
    if([IO.Path]::GetFileNameWithoutExtension($f) -match $regex){[pscustomobject]@{Kind='Build / installer';Name=[IO.Path]::GetFileName($f);Path=$f}}
   }
   foreach($child in [IO.Directory]::EnumerateDirectories($dir)){
    $name=[IO.Path]::GetFileName($child)
    if($name -in @('Windows','$Recycle.Bin','System Volume Information','WinSxS','.git','node_modules','.venv','WindowsApps','Package Cache')){continue}
    try{if(([IO.File]::GetAttributes($child) -band [IO.FileAttributes]::ReparsePoint) -ne 0){continue}}catch{continue}
    if($name -match $regex){[pscustomobject]@{Kind='Possible app folder';Name=$name;Path=$child}}
    $stack.Push($child)
   }
  }catch{}
 }
 [pscustomobject]@{Kind='Scan summary';Name="$visited folders checked";Path=$(if($stack.Count){'Search limit reached; select a narrower folder'}else{'Accessible folders completed'})}
}
function Scan($roots){
 if($script:job -and $script:job.State -eq 'Running'){return}
 if($script:job){Remove-Job $script:job -Force -ErrorAction SilentlyContinue}
 $grid.Rows.Clear();$script:seen=@{};Inventory
 $json=ConvertTo-Json -InputObject @($roots) -Compress
 $script:job=Start-Job -ScriptBlock $worker -ArgumentList $json,$regex
 $status.Text='Scanning in background. No changes are being made.'
}
Button 'Quick scan' {Scan @([Environment]::GetFolderPath('Desktop'),[Environment]::GetFolderPath('MyDocuments'),(Join-Path $env:USERPROFILE 'Downloads'),(Join-Path $env:LOCALAPPDATA 'Programs'),$env:ProgramFiles,[Environment]::GetEnvironmentVariable('ProgramFiles(x86)'),(Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'))}
Button 'Scan fixed drives' {Scan @([IO.DriveInfo]::GetDrives()|Where-Object{$_.DriveType -eq 'Fixed' -and $_.IsReady}|ForEach-Object{$_.RootDirectory.FullName})}
Button 'Scan folder' {$d=New-Object Windows.Forms.FolderBrowserDialog;if($d.ShowDialog() -eq 'OK'){Scan @($d.SelectedPath)};$d.Dispose()}
Button 'Cancel scan' {if($script:job){Stop-Job $script:job -ErrorAction SilentlyContinue;$status.Text='Scan stopped.'}}
Button 'Open selected location' {
 if(!$grid.CurrentRow){return};$p=[string]$grid.CurrentRow.Cells[2].Value
 if($p -and (Test-Path -LiteralPath $p -PathType Container)){Start-Process explorer.exe -ArgumentList ('"'+$p+'"')}
 elseif($p -and (Test-Path -LiteralPath $p -PathType Leaf)){Start-Process explorer.exe -ArgumentList ('/select,"'+$p+'"')}
}
Button 'Installed apps / uninstall' {Start-Process 'ms-settings:appsfeatures'}
Button 'Running processes' {Start-Process taskmgr.exe}
Button 'Recycle selected old file' {
 if(!$grid.CurrentRow -or $grid.CurrentRow.Cells[0].Value -ne 'Build / installer'){return}
 try{
  $p=[IO.Path]::GetFullPath([string]$grid.CurrentRow.Cells[2].Value)
  if(!(Test-Path -LiteralPath $p -PathType Leaf)){throw 'File no longer exists.'}
  foreach($root in @($ProtectPath,$env:ProgramFiles,[Environment]::GetEnvironmentVariable('ProgramFiles(x86)'),$env:WINDIR,(Join-Path $env:LOCALAPPDATA 'Programs'),$env:ProgramData)|Where-Object{$_}){if($p.StartsWith(([IO.Path]::GetFullPath($root).TrimEnd('\')+'\'),[StringComparison]::OrdinalIgnoreCase)){throw 'Use the installed application uninstaller.'}}
  if((Get-Item -LiteralPath $p).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Links are not removed.'}
  if([IO.Path]::GetFileNameWithoutExtension($p) -notmatch $regex){throw 'Name no longer matches.'}
  if(@(Get-Process -ErrorAction SilentlyContinue|Where-Object{try{$_.Path -eq $p}catch{$false}}).Count){throw 'Close this running copy first.'}
  if([Windows.Forms.MessageBox]::Show("Move ONLY this file to the Recycle Bin? Review its path. $p",'Confirm old build','YesNo','Warning') -eq 'Yes'){
   [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($p,'OnlyErrorDialogs','SendToRecycleBin','ThrowException');$grid.Rows.Remove($grid.CurrentRow)
  }
 }catch{[void][Windows.Forms.MessageBox]::Show($_.Exception.Message,'Not removed')}
}
Button 'Remove stale startup entry' {
 if(!$grid.CurrentRow -or $grid.CurrentRow.Cells[0].Value -ne 'Startup registry'){return}
 $parts=([string]$grid.CurrentRow.Cells[2].Value).Split('|',2)
 if($parts.Count -ne 2 -or $parts[0] -ne 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -or $parts[1] -notmatch $regex){return}
 try{
  $key=Get-Item -LiteralPath $parts[0];$command=[string]$key.GetValue($parts[1])
  if($command -match '^\s*"([^"]+\.exe)"'){$exe=$Matches[1]}elseif($command -match '^\s*([^\s"]+\.exe)(?:\s|$)'){$exe=$Matches[1]}else{throw 'Cannot safely determine executable path.'}
  $exe=[Environment]::ExpandEnvironmentVariables($exe)
  if(![IO.Path]::IsPathRooted($exe) -or (Test-Path -LiteralPath $exe)){throw 'Target still exists or cannot be verified. Use Windows Startup Apps.'}
  if([Windows.Forms.MessageBox]::Show("Remove this missing-target startup value only? $command. A backup is saved first.",'Stale startup entry','YesNo','Warning') -eq 'Yes'){
   $backup=Join-Path $env:LOCALAPPDATA 'SACUAR\MaintenanceBackups';New-Item -ItemType Directory -Force $backup|Out-Null
   $name=Join-Path $backup ("Run-"+[guid]::NewGuid()+".reg")
   & reg.exe export 'HKCU\Software\Microsoft\Windows\CurrentVersion\Run' $name /y|Out-Null
   if($LASTEXITCODE -ne 0){throw 'Registry backup failed.'}
   Remove-ItemProperty -LiteralPath $parts[0] -Name $parts[1];$grid.Rows.Remove($grid.CurrentRow);$status.Text="Backup: $name"
  }
 }catch{[void][Windows.Forms.MessageBox]::Show($_.Exception.Message,'Not removed')}
}
Button 'Export CSV' {
 $d=New-Object Windows.Forms.SaveFileDialog;$d.Filter='CSV (*.csv)|*.csv';$d.FileName="$App-maintenance.csv"
 if($d.ShowDialog() -eq 'OK'){@($grid.Rows|ForEach-Object{[pscustomobject]@{Type=$_.Cells[0].Value;Name=$_.Cells[1].Value;Path=$_.Cells[2].Value}})|Export-Csv -LiteralPath $d.FileName -NoTypeInformation -Encoding UTF8};$d.Dispose()
}
$timer=New-Object Windows.Forms.Timer;$timer.Interval=300
$timer.Add_Tick({
 if(!$script:job){return}
 foreach($r in @(Receive-Job $script:job -ErrorAction SilentlyContinue)){
  $id="$($r.Kind)|$($r.Path)"
  if(!$script:seen.ContainsKey($id)){Row $r.Kind $r.Name $r.Path;$script:seen[$id]=$true}
 }
 if($script:job.State -notin @('Running','NotStarted')){$status.Text="Scan $($script:job.State). $($grid.Rows.Count) entries; review before removal.";Remove-Job $script:job -Force -ErrorAction SilentlyContinue;$script:job=$null}
})
$timer.Start()
$form.Add_FormClosed({$timer.Stop();if($script:job){Stop-Job $script:job -ErrorAction SilentlyContinue;Remove-Job $script:job -Force -ErrorAction SilentlyContinue}})
[void]$form.ShowDialog()
