@echo off
echo Starting Distributed File System Cluster...

start cmd /k "cd master && npm start"
start cmd /k "cd node && node server.js 4001"
start cmd /k "cd node && node server.js 4002"
start cmd /k "cd node && node server.js 4003"
start cmd /k "cd frontend && npx serve -p 8080"

echo All services started!
echo Frontend: http://localhost:8080
echo Master: http://localhost:3000
