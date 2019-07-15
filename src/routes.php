<?php

use Slim\App;
use Slim\Http\Request;
use Slim\Http\Response;

function getCloudProvider($cloudProviderName, $container)
{
    $oauth = $container->get('settings')[$cloudProviderName];
    switch ($cloudProviderName) {
    case 'dropbox':
        $provider = new Stevenmaguire\OAuth2\Client\Provider\Dropbox(
            [
            'clientId'          => $oauth['client_id'],
            'clientSecret'      => $oauth['client_secret'],
            'redirectUri'       => $oauth['redirect_uri']
            ]
        );
        break;
    case 'box':
        $provider = new Stevenmaguire\OAuth2\Client\Provider\Box(
            [
            'clientId'          => $oauth['client_id'],
            'clientSecret'      => $oauth['client_secret'],
            'redirectUri'       => $oauth['redirect_uri']
            ]
        );
        break;
    case 'gdrive':
        $provider = new League\OAuth2\Client\Provider\Google(
            [
            'clientId'          => $oauth['client_id'],
            'clientSecret'      => $oauth['client_secret'],
            'redirectUri'       => $oauth['redirect_uri']
            ]
        );
        break;
    case 'onedrive':
        $provider = new Stevenmaguire\OAuth2\Client\Provider\Microsoft(
            [
            'clientId'          => $oauth['client_id'],
            'clientSecret'      => $oauth['client_secret'],
            'redirectUri'       => $oauth['redirect_uri']
            ]
        );
        break;
    default:
        return;
      break;
    }

    return $provider;
}

return function (App $app) {
    $container = $app->getContainer();

    $app->get(
        '/', function (Request $request, Response $response, array $args) use ($container) {
            // Sample log message
            $container->get('logger')->info("Slim-Skeleton '/' route");

            // Render index view
            return $container->get('renderer')->render($response, 'index.phtml', $args);
        }
    );

    $app->get(
        '/{cloud}', function (Request $request, Response $response, array $args) use ($container) {
            $cloud = $args['cloud'];
            $provider = getCloudProvider($cloud, $container);

            if (!isset($provider)) {
                return $response->withJson(['error' => true, 'message' => 'Unknown cloud provider']);
            }

            if (!isset($_GET['code'])) {
                // If we don't have an authorization code then get one
                $authUrl = $provider->getAuthorizationUrl();
                $_SESSION['oauth2state'] = $provider->getState();

                return $response->withRedirect($authUrl);

                // Check given state against previously stored one to mitigate CSRF attack
            } elseif (empty($_GET['state']) || ($_GET['state'] !== $_SESSION['oauth2state'])) {

                unset($_SESSION['oauth2state']);
                return $response->withJson(['error' => true, 'message' => 'Invalid state']);

            } else {

                // Try to get an access token (using the authorization code grant)
                $token = $provider->getAccessToken(
                    'authorization_code', [
                    'code' => $_GET['code']
                    ]
                );


                // Use this to interact with an API on the users behalf
                // echo $token->getToken();

                $this->random = new PragmaRX\Random\Random();
                $shortcode = $this->random->size(6)->get();
                $client = new Predis\Client();
                $client->set("cloud-{$cloud}-{$shortcode}", json_encode($token));
                $client->expire("cloud-{$cloud}-{$shortcode}", 600);
                return $container->get('renderer')->render($response, 'token.phtml', ['shortcode' => $shortcode]);
            }
        }
    );

    $app->get(
        '/{cloud}/token/{shortcode}', function (Request $request, Response $response, $args) {

            $cloud = $args['cloud'];

            $client = new Predis\Client();
            $shortcode = $args['shortcode'];
            $token = json_decode($client->get("cloud-{$cloud}-{$shortcode}"), true);

            if (!isset($token)) {
                return $response->withJson(['error' => true, 'message' => 'Token not found']);
            }
            return $response->withJson(['error' => false, 'oauth' => $token]);
        }
    );

    $app->get(
        '/{cloud}/refresh', function (Request $request, Response $response, $args) use ($container) {

            $provider = getCloudProvider($args['cloud'], $container);

            if (!isset($_GET['code'])) {
                return $response->withJson(['error' => true, 'message' => 'Missing code query parameter']);
            }

            $token = $provider->getAccessToken(
                'refresh_token', [
                'refresh_token' => $_GET['code']
                ]
            );

            // $json = json_decode(json_encode($token), true);
            return $response->withJson(['error' => false, 'oauth' => $token]);
        }
    );


};
