<?php

use Slim\App;
use Slim\Http\Request;
use Slim\Http\Response;

$keyprefix = "moonbase";

function redisConnect(array $redisOptions = []) {
	$redisOptions = array_merge([
		'host' => '127.0.0.1',
		'port' => 6379,
		'timeout' => 0.0,
	], $redisOptions);

	$redis = new Redis();

	$redis->connect($redisOptions['host'], $redisOptions['port'], $redisOptions['timeout']);

	return $redis;
}

function getUserIpAddr() {
	if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
		//ip from share internet
		$ip = $_SERVER['HTTP_CLIENT_IP'];
	} elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
		//ip pass from proxy
		$ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
	} else {
		$ip = $_SERVER['REMOTE_ADDR'];
	}
	return $ip;
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

	$app->post(
		'/moonbase/createsession', function (Request $request, Response $response, array $args) use ($container) {
			global $keyprefix;

			// Sample log message
			$container->get('logger')->info("Slim-Skeleton '/moonbase/createsession' route");

			$parsedBody = $request->getParsedBody();

			if (array_key_exists('name', $parsedBody)) {
				$container->get('logger')->info("Got $parsedBody[name]");
			}

			$ip = getUserIpAddr();

			$redis = redisConnect();

			$keys = $redis->keys("$keyprefix;sessions;$ip;*");

			if (!sizeof($keys)) {
				$sessionid = rand();

				$redis->setEx("$keyprefix;sessions;$ip;$sessionid", 3600, "{\"sessionid\": $sessionid, \"name\": \"$parsedBody[name]\"}");

				$container->get('logger')->info("Generated session $sessionid");
			} else {
				$session = $redis->get($keys[0]);

				$par = json_decode($session);

				$sessionid = $par->sessionid;

				$container->get('logger')->info("Retrieved session $sessionid");
			}

			return $response->withJson(["sessionid" => $sessionid]);
		}
	);

	$app->post(
		'/moonbase/adduser', function (Request $request, Response $response, array $args) use ($container) {
			global $keyprefix;

			// Sample log message
			$container->get('logger')->info("Slim-Skeleton '/moonbase/adduser' route");

			$parsedBody = $request->getParsedBody();

			if (!array_key_exists('sessionid', $parsedBody)) {
				return $response->withJson(["error" => "No sessionid specified"]);
			}

			$sessionid = $parsedBody['sessionid'];

			$redis = redisConnect();

			$keys = $redis->keys("$keyprefix;sessions;*;$sessionid");

			if (!sizeof($keys)) {
				return $response->withJson(["error" => "Unknown sessionid $sessionid"]);
			}

			$sessionkey = $keys[0];

			$session = json_decode($redis->get($sessionkey));

			if (array_key_exists('players', $session)) {
				if (sizeof($session->players) > 3) {
					return $response->withJson(["error" => "Too many players in $sessionid"]);
				}
			} else {
				$session->players = [];
			}

			$playerid = rand();

			array_push($session->players, [ "shortname" => $parsedBody['shortname'],
											"longname"  => $parsedBody['longname'],
											"id"        => $playerid]);

			$redis->setEx($sessionkey, 3600, json_encode($session));

			return $response->withJson(["userid" => $playerid]);
		}
	);

	$app->get(
		'/moonbase/lobbies', function (Request $request, Response $response, array $args) use ($container) {
			global $keyprefix;

			$container->get('logger')->info("Slim-Skeleton '/moonbase/lobbies' route");

			$redis = redisConnect();

			$keys = $redis->keys("$keyprefix;sessions;*");

			if (!sizeof($keys)) {
				return $response->withJson([]);
			}

			$res = [];

			foreach ($keys as $key) {
				$session = json_decode($redis->get($key));

				array_push($res, [ "name" => $session->name, "sessionid" => $session->sessionid]);
			}

			return $response->withJson($res);
		}
	);

};
