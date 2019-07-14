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
          'auth_uri' => 'https://www.dropbox.com/1/oauth2/authorize',
          'token_uri' => 'https://api.dropboxapi.com/oauth2/token',
          'refresh_uri' => ''
        ],

        // Box settings
        'box' => [
          'client_id' => 'ep9cz17to1wakzqbq2a5jn5u01b0omxw',
          'client_secret' => getenv('BOX_SECRET'),
          'redirect_uri' => 'https://cloud.scummvm.org/box/token',
          'auth_uri' => 'https://www.dropbox.com/1/oauth2/authorize',
          'token_uri' => 'https://api.dropboxapi.com/oauth2/token',
          'refresh_uri' => ''
        ],

        // Google Drive settings
        'google_drive' => [
          'client_id' => '102752616291108817673',
          'client_secret' => getenv('GOOGLE_DRIVE_SECRET'),
          'redirect_uri' => 'https://cloud.scummvm.org/google_drive/token',
          'auth_uri' => 'https://accounts.google.com/o/oauth2/auth',
          'token_uri' => 'https://oauth2.googleapis.com/token',
          'refresh_uri' => ''
        ],

        // Onedrive settings
        'onedrive' => [
          'client_id' => '12c88b6d-3037-4c0c-9076-cc4205cfb1d0',
          'client_secret' => getenv('ONEDRIVE_SECRET'),
          'redirect_uri' => 'https://cloud.scummvm.org/onedrive/token',
          'auth_uri' => 'https://www.dropbox.com/1/oauth2/authorize',
          'token_uri' => 'https://api.dropboxapi.com/oauth2/token',
          'refresh_uri' => ''
        ],
    ],
];
