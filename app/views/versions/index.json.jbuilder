json.array!(@versions) do |version|
  json.extract! version, :id, :platform, :game, :release_date, :aliases, :language, :introductory_release_id
  json.url version_url(version, format: :json)
end
