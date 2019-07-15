<?php
return [
    'settings' => [
        'displayErrorDetails' => true, // set to false in production
        'addContentLengthHeader' => false, // Allow the web server to send the content-length header

        // Renderer settings
        'renderer' => [
            'template_path' => __DIR__ . '/../templates/',
        ],

        // Monolog settings
        'logger' => [
            'name' => 'slim-app',
            'path' => isset($_ENV['docker']) ? 'php://stdout' : __DIR__ . '/../logs/app.log',
            'level' => \Monolog\Logger::DEBUG,
        ],

        // Dropbox settings
        'dropbox' => [
          'client_id' => 'vgij09edeilbrtm',
          'client_secret' => getenv('DROPBOX_SECRET'),
          'redirect_uri' => 'https://cloud.scummvm.org/dropbox/token',
        ],

        // Box settings
        'box' => [
          'client_id' => 'ep9cz17to1wakzqbq2a5jn5u01b0omxw',
          'client_secret' => getenv('BOX_SECRET'),
          'redirect_uri' => 'https://cloud.scummvm.org/box',
        ],

        // Google Drive settings
        'gdrive' => [
          'client_id' => 'AIzaSyBbhRYGs1Xi_RxNMRu_Jhh3tQne2Ipgzfc',
          'client_secret' => getenv('GOOGLE_DRIVE_SECRET'),
          'redirect_uri' => 'https://cloud.scummvm.org/gdrive',
        ],

        // Onedrive settings
        'onedrive' => [
          'client_id' => '12c88b6d-3037-4c0c-9076-cc4205cfb1d0',
          'client_secret' => getenv('ONEDRIVE_SECRET'),
          'redirect_uri' => 'https://cloud.scummvm.org/onedrive',
        ],
    ],
];
