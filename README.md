![Robocorp](./docs/include/robocorp-header.svg)

<samp>[Docs](https://robocorp.com/docs) | [Blog](https://robocorp.com/blog) | [Examples](https://robocorp.com/portal) | [ReMark](https://chat.robocorp.com) | [Courses](https://robocorp.com/docs/courses) | [Slack](https://robocorp-developers.slack.com/) | [Youtube](https://www.youtube.com/@Robocorp) | [𝕏](https://twitter.com/RobocorpInc)</samp>

[![PyPI - Version](https://img.shields.io/pypi/v/robocorp?label=robocorp&color=%23733CFF)](https://pypi.org/project/robocorp)
[![PyPI - Version](https://img.shields.io/pypi/v/robocorp-action-server?label=action-server&color=%23733CFF)](https://pypi.org/project/robocorp-action-server)
[![Downloads](https://static.pepy.tech/badge/robocorp/month)](https://pepy.tech/project/robocorp)
[![GitHub issues](https://img.shields.io/github/issues/robocorp/robocorp?color=%232080C0)](https://github.com/robocorp/robocorp/issues)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Create, deploy and operate 🐍 Python AI Actions <br/> and 🤖 Automations anywhere.

Robocorp is the easiest way to extend the capabilities of AI agents, assistants and copilots with custom actions, written in Python. Create and deploy tools, skills, loaders and plugins that securely connects any AI Assistant platform to your data and applications.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./docs/include/robocorp-flow-dark.webp">
  <img alt="Text changing depending on mode. Light: 'So light!' Dark: 'So dark!'" src="./docs/include/robocorp-flow-light.webp">
</picture>

Looking for a replacement to RPA? Head over to our [Enterprise Python Automation site](https://robocorp.com/docs/quickstart-guide) for more.

---

# 🏃‍♂️ Quickstart

Install Robocorp Action Server:

```sh
# On macOS
brew install robocorp/tools/action-server

# On Linux or Windows
pip install robocorp-action-server
```

Bootstrap a new project from a template. You’ll be prompted for a name of the project:

```sh
action-server new
```

Navigate to the freshly created project folder and start the server:

```sh
cd my-first-action-server
action-server start --expose
```

Once that’s done, you’ll have an Action Server UI locally at [http://localhost:8080](http://localhost:8080)), and a public internet-facing URL (something like _twently-cuddly-dinosaurs.robocorp.link_).

Head over to [Action Server docs](./action_server/docs) for more in detail documentation.

---

# What makes a Python function an ⚡️Action?

1️⃣ `conda.yaml` file that sets up your **Python environment and dependencies**:

<details>
  <summary>Curious to more about <code>conda.yaml</code>? We've got your covered.</summary>

- Think of this as an equivalent of the requirements.txt, but much better. 👩‍💻 `conda.yaml` defines your channels (where are your dependencies coming from), the versions of e.g. python and pip your actions are built to work with, and all the packages you need as dependendencies.

- When starting an Action Server, this file is used as a "recipe" to build the entire environment, making sure everything works on any machine every time the exact same way. Neat, right? Dive deeper with [these](https://github.com/robocorp/rcc/blob/master/docs/recipes.md#what-is-in-condayaml) resources.

</details>

```yaml
channels:
  - conda-forge

dependencies:
  - python=3.10.12
  - pip=23.2.1
  - robocorp-truststore=0.8.0
  - pip:
      - robocorp==1.3.0
      - numpy==1.26.3
```

2️⃣ [@action decorator](./actions/docs) that determines the **action entry point** and [Type hints and docstring](./actions/docs) to let AI agents know **what the Action does** in natural language.

```py
@action
def greeting(name: str) -> str:
    """
    Greets the user

    Args:
        name (str): The user name

    Returns:
        str: Final user greeting
    """
```

---

## Add Action Server as a Toolkit to [🦜️🔗 LangChain](https://github.com/robocorp/langchain)

Robocorp Action Server comes with everything needed to connect it to your Langchain AI app project. The easiest way is to start with the template, provided in the Langchain project. Here’s how to do it:

```sh
# Install LangChain cli tool if not already there
pip install langchain-cli

# Create a new LangChain app using Action Server template
langchain app new my-awesome-app --package robocorp-action-server
```

And add the following code to the created `./my-awesome-app/app/server.py` file:

```py
from robocorp_action_server import agent_executor as action_server_chain

add_routes(app, action_server_chain, path="/robocorp-action-server")
```

And inside the project directory spin up a LangServe instance directly by:

```sh
langchain serve
```

After running the steps above, you’ll have a Playground available at http://127.0.0.1:8000/robocorp-action-server/playground/ where you can test your Actions with an AI agent.

**Want to build your own thing?** Adding your own Robocorp AI Actions to a Langchain project is as easy as the code below. Just remember to change the URL of the Action Server if you are not running both the Action Server and Langchain app on the same machine.

```py
from langchain_robocorp import ActionServerToolkit

# Initialize Action Server Toolkit
toolkit = ActionServerToolkit(url="http://localhost:8080")
tools = toolkit.get_tools()
```

## Connect with OpenAI GPTs Actions

Once you have started the Action Server with `--expose` flag, you’ll get a URL available to the public, along with the authentication token. The relevant part of the output from the terminal looks like this, of course with your own details:

```sh
...
Uvicorn running on http://localhost:8080 (Press CTRL+C to quit)
🌍 URL: https://seventy-six-helpless-dragonflies.robocorp.link
🔑 Add following header api authorization header to run actions: { "Authorization": "Bearer xxx_xxx" }
```

Adding the Action Server hosted AI Action to your custom GPT is super simple, basically just navigate to “Actions” section of the GPT configuration, add the link to import the actions, and **Add Authentication** with **Authentication method** set to _“API key”_ and **Auth Type** to _“Bearer”_.

---

## Why use Robocorp AI Actions

- ❤️ “when it comes to automation, the Robocorp suite is the best one” _[/u/disturbing_nickname](https://old.reddit.com/r/rpa/comments/18qqspn/codeonly_rpa_pet_project/kez2jds/?context=3)_
- ❤️ “Robocorp seems to be a good player in this domain” _[/u/thankred](https://old.reddit.com/r/rpa/comments/18r5gne/recommendation_for_open_source_or_somewhat_less/kez6aw6/?context=3)_
- ❤️ “Since you know Python, check out Robocorp. Their product is crazy good.” _[/u/Uomis](https://old.reddit.com/r/rpa/comments/18n5sah/c/ke8qz2g?context=3)_

Robocorp stack is hands down the easiest way to give AI agents more capabilities. It’s an end-to-end stack supporting every type of connection between AI and your apps and data. You are in control where to run the code and everything is built for easiness, security, and scalability.

- 🔐 **Decouple AI and Actions that touches your data/apps** - Clarity and security with segregation of duties between your AI agent and code that touches your data and apps. Build `@action` and use from multiple AI frameworks.
- 🏎️ **Develop Actions faster with `robocorp` automation libraries** - Robocorp libraries and the Python ecosystem lets you act on anything - from data to API to Browser to Desktops.
- 🕵️ **Observability out of the box** - Log and trace every `@action` run automatically without a single `print` statement.
- 🤯 **No-pain Python environment management** - Don't do [this](https://xkcd.com/1987/). Robocorp manages a full Python environment for your actions with ease.
- 🚀 **Deploy with zero config and infra** - One step deployment, and you'll be connecting your `@action` to AI apps like Langchain and OpenAI GPTs in seconds.

## Inspo

Check out these example projects for inspiration.

- 🤡 Get a random joke or jokes per theme. Showcases how easy it is to work with APIs. (Coming soon)
- 🕸️ Open a local Playwright browser and make some Google searches. (Coming soon)
- 🖥️ Securely fetch contents of `.txt` and `.pdf` files from your local machine's folder in real time. (Coming soon)

Build more `@actions` and be awesome! We'd love to hear and see what have you built. Join our [Slack community](https://robocorp-developers.slack.com/) to share your work, or drop us a line at [tommi@robocorp.com](mailto:tommi@robocorp.com). We'll soon start showcasing the best of the community here!

## Roadmap

- [x] Action Server `brew install` for Mac users
- [x] Expose actions to public URL
- [x] Resume previously exposed session
- [ ] Run and debug `@actions` like `@tasks` with [Robocorp VS Code Extension](https://marketplace.visualstudio.com/items?itemName=robocorp.robocorp-code)
- [ ] MS Copilot Studio manifest file support
- [ ] Llamaindex Tools support
- [ ] Link and deploy Action Servers to [Control Room](https://cloud.robocorp.com/)
- [ ] Hot reload of actions after a change
- [ ] Docstring validator and autogeneration
- [ ] More complex input args
- [ ] Explicit action user approval
- [ ] Stateful actions

## Contributing and issues

> ⭐️ First, please star the repo - your support is highly appreciated!

- 🚩 Issues – our [GitHub Issues](https://github.com/robocorp/robocorp/issues) is kept up to date with bugs, improvements, and feature requests
- 🙋 Help - you are welcome to [join our Community Slack](https://robocorp-developers.slack.com/) if you experience any difficulty getting setup
- 🌟 Contribution and recognition – Start [here](https://github.com/robocorp/robocorp/blob/master/CONTRIBUTING.md), [PR's](https://github.com/robocorp/robocorp/pulls) are welcome!
- 🔐 Refer to our [Security policy](https://robocorp.com/.well-known/security.txt) for details

### Contributors

![Contributors](https://contrib.nn.ci/api?repo=robocorp/robocorp)
