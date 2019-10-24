<?php

use Slim\App;

return function (App $app) {
    // e.g: $app->add(new \Slim\Csrf\Guard);
    $app->add(
        \RateLimit\Middleware\RateLimitMiddleware::createDefault(
            \RateLimit\RateLimiterFactory::createRedisBackedRateLimiter(
                [
                'host' => 'localhost',
                'port' => 6379,
                ], 100, 3600
            ),
            [
              'limitExceededHandler' => function ($request, $response) {
                return $response->withJson(
                    [
                      'message' => 'API rate limit exceeded',
                      ], 429
                );
              },
            ]
        )
    );
};
