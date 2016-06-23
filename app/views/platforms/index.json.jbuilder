json.array!(@platforms) do |platform|
  json.extract! platform, :id, :name
  json.url platform_url(platform, format: :json)
end
