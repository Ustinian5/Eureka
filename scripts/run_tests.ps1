$ErrorActionPreference = "Stop"
D:\conda_envs\eureka\python.exe -B -W ignore -m unittest discover -s backend\tests -v
node --check extension\popup.js
node --check extension\options.js
node --check extension\content.js
node --check web\app.js
