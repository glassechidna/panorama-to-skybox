# panorama_to_skybox

A web app that converts 2:1 equirectangular panoramas to skybox (cube) images.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# Prerequisites

* A free [Heroku](https://www.heroku.com) account.
* The [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).

## Manually deploy to Heroku

If you don't want to deploy manually, press the "Deploy to Heroku" button at the top of the page.

1. Clone panorama_to_skybox:

    ```bash
    git clone https://github.com/glassechidna/panorama_to_skybox.git
    ```

2. Create a Heroku app:

    ```bash
    heroku create
    ```
   
3. Deploy panorama_to_skybox to your Heroku app:

    ```bash
    git push heroku master
    ```

4. Run the setup script and ensure one dyno is running:

    ```bash
    heroku ps:scale web=1
    ```

## Usage

Visit the URL for your heroku app, and follow the instructions to upload a panorama image.
