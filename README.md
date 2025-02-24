# Hex-Viewer
## Selects a path to load files from in order to scan and analyze their HEX contents.
### Virustotal Analysis:
> [SCAN RESULTS](https://www.virustotal.com/gui/file/b2509473d0408706c37fb9533b6166bbdc9a5bc4a3fa8d4f9def6b4e0907e690)

![image](https://github.com/user-attachments/assets/3c3d1ad1-fb4f-48f1-9fa5-01e136ae0b75)

<iframe width="560" height="315" src="https://www.youtube.com/embed/tgvKu3SqpEU?si=jSgx-DCiho1fVvp0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Executing the application:
**It is recommended to run this .exe through Command Prompt / Powershell as Admin**
1) The user is prompted to specify a path they want to load files from. The default path is the %username%\AppData\Roaming\.minecraft directory, as the initial objective of this program was to parse servers.dat and servers.dat_old files to detect disallowed server proxies.
2) The user can also provide a filter pattern (i.e, .txt, .exe or .dat or any other word a file may begin with, i.e f_0 for download caches), or leave it blank to list all files.
**File Listing:**
1) All files in the chosen directory that match the filter are listed for selection.
**File Selection Mode:**
1) Navigate with UP or DOWN arrows and press Enter to view a file.
**Content View Mode:**
1) Views the full hex dump of the selected file. In order for the process to be sped up, a loading screen is displayed while the program loads file's contents. If it has been loading for a while, make sure to press any button to continue.
   2)  Scroll with arrow keys or Page Up/Page Down if your keyboard supports these functions. Press '/' to recursively search the whole Hex dump.
**Search Results Mode:**
1) All matching lines are shown. Use arrow keys or Page Up/Page Down to navigate, then press Enter on a result to jump to that line in the hex dump.
2) Press b to return.
3) Press q at any time to quit the application.
**   ~ Software made by UnMonsieur.**
