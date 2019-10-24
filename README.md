# ScummVM cloud token site

This project is the ScummVM cloud website located at: https://cloud.scummvm.org

This site uses the Slim PHP framework to provide a simple API for acquiring oauth
tokens for Dropbox, Box, Onedrive and Google Drive.

Most of the configuration can be found in settings.php, and the business logic in 
routes.php.

The site uses a rate limiter middleware to prevent the same IP making too many requests.

For each token, a shortcode is generated and temporarly stored in redis, until that 
shortcode is accessed by ScummVM, once the token has been retrieved, or 10 minutes have passed,
the shortcode will expire and removed.

## Getting Started

These instructions will get you a copy of the project up and running on your
local machine for development and testing purposes.

Set the proper env vars for cloud secrets.

### Prerequisites

The ScummVM cloud website relies on several tools to install properly.
Before installing please make sure you have the following installed:

* [Composer](https://getcomposer.org/)
* [PHP Redis Extension](https://github.com/phpredis/phpredis)
* [PHP mbstring Extension](https://www.php.net/manual/en/mbstring.installation.php)

### Installing

Clone this repo

```
git clone https://github.com/scummvm/scummvm-sites.git
```

Then run

```
git checkout cloud
composer install
composer start
```

## Deployment
