Output demo.gif

Set FontSize 14
Set Width 900
Set Height 600
Set Theme "Dracula"

Type "prompthub" Sleep 500ms Enter
Sleep 2s

Type "prompthub init --name prompthub-demo" Sleep 500ms Enter
Sleep 1s

Type "echo 'You are a helpful assistant. Answer clearly.' > prompt.txt" Sleep 500ms Enter
Sleep 500ms

Type "prompthub add prompt.txt" Sleep 500ms Enter
Sleep 1s

Type "prompthub commit -m 'initial version'" Sleep 500ms Enter
Sleep 3s

Type "echo 'You are an expert assistant. Reply in JSON only.' > prompt.txt" Sleep 500ms Enter
Sleep 500ms

Type "prompthub commit -m 'added JSON format'" Sleep 500ms Enter
Sleep 3s

Type "prompthub log" Sleep 500ms Enter
Sleep 2s

Type "prompthub diff v1 v2" Sleep 500ms Enter
Sleep 2s