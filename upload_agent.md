
# Upload Agent

The upload agent is available as a standalone binary executable file and is hosted on GitHub Releases. 

## Installation

1. **Download**: Obtain the executable from the [GitHub Releases](https://github.com/your-repo/releases) page.
2. **Rename**: After downloading, rename the file from its OS-specific format, such as `roboto-agent-macos-aarch64`, to `roboto-agent`.

## Configuration

The agent is configured using a JSON file located at `$HOME/.roboto/upload_agent.json`.

This configuration file can be generated in two ways:
- **Interactively**: Run `roboto-agent configure` in your terminal to create the configuration file.
- **Manually**: Create and edit the JSON file manually.

### Requirements

To run the upload agent, a Device Access Token or Personal Access Token must be present in `$HOME/.roboto/config.json`. 

For more information on tokens, refer to the relevant documentation pages.

