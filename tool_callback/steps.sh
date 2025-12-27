VERSION=0.16.0
curl -O https://storage.googleapis.com/genai-toolbox/v$VERSION/darwin/arm64/toolbox
chmod +x toolbox
./toolbox --version

./toolbox --tools-file "tools.yaml" --port 7000
./toolbox --tools-file "tools.yaml" --ui
./toolbox --tools_file "tools.yaml"

npx @modelcontextprotocol/inspector
The MCP Inspector is an interactive developer tool for testing and debugging MCP servers.

export VERSION=0.13.0
curl -O https://storage.googleapis.com/genai-toolbox/v$VERSION/linux/amd64/toolbox
chmod +x toolbox
