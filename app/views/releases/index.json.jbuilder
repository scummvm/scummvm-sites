json.array!(@releases) do |release|
  json.extract! release, :id, :major, :minor, :patch, :release_date
  json.url release_url(release, format: :json)
end
