<?php

use Slim\App;
use Slim\Http\Request;
use Slim\Http\Response;

define("KEYPREFIX", "moonbase");
define("NET_SEND_TYPE_INDIVIDUAL", 1);
define("NET_SEND_TYPE_GROUP", 2);
define("NET_SEND_TYPE_HOST", 3);
define("NET_SEND_TYPE_ALL", 4);

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
			// Sample log message
			$container->get('logger')->info("Slim-Skeleton '/moonbase/createsession' route");

			$parsedBody = $request->getParsedBody();

			if (array_key_exists('name', $parsedBody)) {
				$container->get('logger')->info("Got $parsedBody[name]");
			}

			$ip = getUserIpAddr();

			$redis = redisConnect();

			$keys = $redis->keys(KEYPREFIX.";sessions;$ip;*");

			if (!sizeof($keys)) {
				$sessionid = rand();

				$redis->setEx(KEYPREFIX.";sessions;$ip;$sessionid", 3600, "{\"sessionid\": $sessionid, \"name\": \"$parsedBody[name]\"}");

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
		'/moonbase/disablesession', function (Request $request, Response $response, array $args) use ($container) {
			// Sample log message
			$container->get('logger')->info("Slim-Skeleton '/moonbase/disablesession' route");

			$parsedBody = $request->getParsedBody();

			if (!array_key_exists('sessionid', $parsedBody)) {
				return $response->withJson(["error" => "No sessionid specified"]);
			}

			$sessionid = $parsedBody['sessionid'];

			$redis = redisConnect();

			$keys = $redis->keys(KEYPREFIX.";sessions;*;$sessionid");

			if (!sizeof($keys)) {
				return $response->withJson(["error" => "Unknown sessionid $sessionid"]);
			}

			$sessionkey = $keys[0];

			$session = json_decode($redis->get($sessionkey));

			$session->disabled = 1;

			$redis->setEx($sessionkey, 3600, json_encode($session));

			return $response->withJson([]);
		}
	);

	$app->post(
		'/moonbase/endsession', function (Request $request, Response $response, array $args) use ($container) {
			// Sample log message
			$container->get('logger')->info("Slim-Skeleton '/moonbase/endsession' route");

			$parsedBody = $request->getParsedBody();

			if (!array_key_exists('sessionid', $parsedBody)) {
				return $response->withJson(["error" => "No sessionid specified"]);
			}

			$sessionid = $parsedBody['sessionid'];

			$redis = redisConnect();

			$keys = $redis->keys(KEYPREFIX.";sessions;*;$sessionid");

			if (!sizeof($keys)) {
				return $response->withJson(["error" => "Unknown sessionid $sessionid"]);
			}

			$redis->unlink($keys);

			return $response->withJson([]);
		}
	);

	$app->post(
		'/moonbase/adduser', function (Request $request, Response $response, array $args) use ($container) {
			// Sample log message
			$container->get('logger')->info("Slim-Skeleton '/moonbase/adduser' route");

			$parsedBody = $request->getParsedBody();

			if (!array_key_exists('sessionid', $parsedBody)) {
				return $response->withJson(["error" => "No sessionid specified"]);
			}

			$sessionid = $parsedBody['sessionid'];

			$redis = redisConnect();

			$keys = $redis->keys(KEYPREFIX.";sessions;*;$sessionid");

			if (!sizeof($keys)) {
				return $response->withJson(["error" => "Unknown sessionid $sessionid"]);
			}

			$sessionkey = $keys[0];

			$session = json_decode($redis->get($sessionkey));

			$playerid = rand();

			if (array_key_exists('players', $session)) {
				if (sizeof($session->players) > 3) {
					return $response->withJson(["error" => "Too many players in $sessionid"]);
				}
			} else {
				$session->players = [];
				$session->host = $playerid;
			}

			array_push($session->players, [ "shortname" => $parsedBody['shortname'],
											"longname"  => $parsedBody['longname'],
											"id"        => $playerid]);

			$redis->setEx($sessionkey, 3600, json_encode($session));

			return $response->withJson(["userid" => $playerid]);
		}
	);

	$app->get(
		'/moonbase/lobbies', function (Request $request, Response $response, array $args) use ($container) {
			$container->get('logger')->info("Slim-Skeleton '/moonbase/lobbies' route");

			$redis = redisConnect();

			$keys = $redis->keys(KEYPREFIX.";sessions;*");

			$res = [];

			foreach ($keys as $key) {
				$session = json_decode($redis->get($key));

				if (!array_key_exists('disabled', $session))
					array_push($res, $session);
			}

			return $response->withJson($res);
		}
	);

	$app->post(
		'/moonbase/packet', function (Request $request, Response $response, array $args) use ($container) {
			$container->get('logger')->info("Slim-Skeleton '/moonbase/packet' route");

			$container->get('logger')->info("got " .$request->getBody());

			$parsedBody = $request->getParsedBody();

			if (!array_key_exists('sessionid', $parsedBody)) {
				return $response->withJson(["error" => "No sessionid specified"]);
			}

			$sessionid = $parsedBody['sessionid'];

			$container->get('logger')->info("/moonbase/packet: sess: $sessionid");

			// Get session
			$redis = redisConnect();

			$keys = $redis->keys(KEYPREFIX.";sessions;*;$sessionid");

			if (!sizeof($keys)) {
				return $response->withJson(["error" => "Unknown sessionid $sessionid"]);
			}

			$count = $redis->incr(KEYPREFIX.";packets;$sessionid");

			$redis->setEx(KEYPREFIX.";packets;$sessionid;$count", 3600, json_encode($parsedBody));

			return $response->withJson([]);
		}
	);

	$app->post(
		'/moonbase/getpacket', function (Request $request, Response $response, array $args) use ($container) {
			// Sample log message
			//$container->get('logger')->info("Slim-Skeleton '/moonbase/getpacket' route");

			$parsedBody = $request->getParsedBody();

			if (!array_key_exists('sessionid', $parsedBody)) {
				return $response->withJson(["error" => "No sessionid specified"]);
			}

			$sessionid = $parsedBody['sessionid'];

			if (!array_key_exists('playerid', $parsedBody)) {
				return $response->withJson(["error" => "No playerid specified"]);
			}

			$playerid = $parsedBody['playerid'];


			$redis = redisConnect();

			$sessioncount = $redis->get(KEYPREFIX.";packets;$sessionid");
			$playercount  = $redis->get(KEYPREFIX.";players;$sessionid;$playerid");

			$keys = $redis->keys(KEYPREFIX.";sessions;*;$sessionid");

			if (!sizeof($keys)) {
				return $response->withJson(["error" => "Unknown sessionid $sessionid"]);
			}

			$sessionkey = $keys[0];

			$session = json_decode($redis->get($sessionkey));

			for (;;) {
				if ($playercount >= $sessioncount)	// No more packets
					return $response->withJson(["size" => 0]);

				$playercount = $redis->incr(KEYPREFIX.";players;$sessionid;$playerid");

				$container->get('logger')->info("'/moonbase/getpacket' reading packet $playercount");

				if (!$redis->exists(KEYPREFIX.";packets;$sessionid;$playercount")) {
					return $response->withJson(["error" => "Too big playercount: $playercount > $sessioncount"]);
				}

				$packet = json_decode($redis->get(KEYPREFIX.";packets;$sessionid;$playercount"));

				$from = $packet->from;
				$type = $packet->type;

				$to = -1;
				switch ($type) {
				case NET_SEND_TYPE_INDIVIDUAL: // 1
					$to = $packet->toparam;
					break;

				case NET_SEND_TYPE_GROUP: // 2
					$to = -1;
					break;

				case NET_SEND_TYPE_HOST: // 3
					$to = $session->host;
					break;

				case NET_SEND_TYPE_ALL: // 4
				default:
					$to = -1;
					break;
				}

				$container->get('logger')->info("'/moonbase/getpacket' type: $type from: $from, to: $to, playerid: $playerid, size: " . $packet->size);

				if (($to == -1 && $from != $playerid) || $to == $playerid) { // Send to all or to me
					return $response->withJson($packet);
				} else {
					$container->get('logger')->info("'/moonbase/getpacket' not ours: to $to");
				}

				# It is not pur packet, loop over to next one
			}
		}
	);

};
