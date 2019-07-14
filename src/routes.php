<?php

use Slim\App;
use Slim\Http\Request;
use Slim\Http\Response;

return function (App $app) {
    $container = $app->getContainer();

    $app->get(
        '/[{name}]', function (Request $request, Response $response, array $args) use ($container) {
            // Sample log message
            $container->get('logger')->info("Slim-Skeleton '/' route");

            // Render index view
            return $container->get('renderer')->render($response, 'index.phtml', $args);
        }
    );

    $app->group(
        '/dropbox',  function () use ($app, $container) {
            $dropbox = $container->get('settings')['dropbox'];
            $app->get(
                '/auth', function (Request $request, Response $response, array $args) use ($app, $dropbox) {
                    $authUri = "{$dropbox['auth_uri']}?response_type=code&redirect_uri={$dropbox['redirect_uri']}&client_id={$dropbox['client_id']}";
                    return $response->withRedirect($authUri);
                }
            );

            $app->get(
                '/token', function (Request $request, Response $response, array $args) use ($app, $dropbox, $container) {
                    $code = $request->getQueryParam('code');
                    $client = new \GuzzleHttp\Client();
                    $res = $client->request(
                        'POST',
                        $dropbox['token_uri'],
                        [
                        'auth' => [
                          $dropbox['client_id'],
                          $dropbox['client_secret']
                        ],
                        'form_params' => [
                          'grant_type' => 'authorization_code',
                          'redirect_uri' => $dropbox['redirect_uri'],
                          'code' => $code
                        ]
                        ]
                    );

                    $json = json_decode($res->getBody(), true);

                    $this->random = new PragmaRX\Random\Random();
                    $shortcode = $this->random->size(6)->get();
                    $client = new Predis\Client();
                    $client->set("cloud-dropbox-{$shortcode}", $json['access_token']);
                    $client->expire("cloud-dropbox-{$shortcode}", 600);
                    return $container->get('renderer')->render($response, 'token.phtml', ['shortcode' => $shortcode]);
                }
            );

            $app->get(
                '/token/{shortcode}', function (Request $request, Response $response, $args) {
                    $client = new Predis\Client();
                    $shortcode = $args['shortcode'];
                    $token = $client->get("cloud-dropbox-{$shortcode}");
                    return $response->withJson(['shortcode' => $shortcode, 'token' => $token]);
                }
            );
        }
    );
};
