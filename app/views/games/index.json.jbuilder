json.array!(@games) do |game|
  json.extract! game, :id, :name, :developer
  json.url game_url(game, format: :json)
end
