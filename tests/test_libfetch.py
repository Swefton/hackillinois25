import os
from libfetch.combined_libs import parse_workspace_for_libraries


alexandria_path = "/Users/amrit/Desktop/Repositories/hackillinois25/tests/workspace/.alexandria"
workspace_path = "/Users/amrit/Desktop/Repositories/hackillinois25/tests/workspace"

print(alexandria_path)
print(workspace_path)

parse_workspace_for_libraries(alexandria_path,workspace_path)
