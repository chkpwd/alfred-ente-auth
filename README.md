# Ente Auth - Alfred Workflow for Ente Exports

Easily integrate your **Ente Auth** with Alfred using this simple and powerful workflow to manage your Ente secrets and authentication.

## 📸 Shots
![image1](./metadata/image.png)

## 🚀 Setup

### 1. Install the Workflow
Download and install the workflow from the latest [releases](https://github.com/chkpwd/alfred-ente-auth/releases) page.


> [!NOTE]
> Currently, Homebrew installation is not available for the Ente CLI due to an issue with the formula. When running brew test for the formula, the ente CLI fails with an error. As a result, the formula is not ready for installation via brew yet. Please use the manual installation steps outlined above. https://github.com/ente-io/ente/pull/4028

### 2. Download and Install the Ente CLI
To use the **Ente Auth** workflow, you'll need the **Ente CLI**. Follow the steps below to install it:

1. Visit the [Ente CLI releases page](https://github.com/ente-io/ente/releases?q=tag%3Acli-v0).
2. Download the latest version for **macOS**.
3. Move the binary to `/usr/local/bin` and make it executable with the following commands:

   ```bash
   sudo mv /path/to/ente /usr/local/bin/ente
   sudo chmod +x /usr/local/bin/ente
   ```

Once installed, verify that it's working by running the following command in your terminal:

```bash
ente version
```

### 3. Configure Your Database
To configure the Ente CLI and ensure the workflow has access to your data, you'll need to set the **export path**. This path should be the same one you configured when adding your Ente account.

---

## 📖 Instructions

1. **Launch Alfred**
   - Open Alfred and navigate to the **Workflows** tab.

2. **Select Ente Auth**
   - Find the "Ente Auth" workflow in your list and click on it.

3. **Configure Workflow**
   - Hit the **Configure Workflow** button to open the settings.
   - Specify the **export path**—this should be the same path you configured when adding your Ente account.
   - Configure any additional settings as needed (e.g., API keys, other preferences).

4. **Import Your Data**
   - To import your Ente secrets, simply trigger the workflow by running the command **Import Ente Secrets** in Alfred. This will import your stored Ente secrets into the workflow.

---

## 🛠 Local Development

### Install/Update Dependencies
To set up your local environment, run the following command to install or update the necessary dependencies:

```bash
poetry install --only=main
```

### Build the Alfred Workflow File
Once your environment is ready, use this command to build the workflow file:

```bash
python3 build.py
```

---

## Making it Better 🤝

Feel free to open issues or submit pull requests.
